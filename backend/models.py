from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Identity,
    Integer,
    Numeric,
    String,
    Text,
    create_engine,
    select,
    text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship
from werkzeug.security import generate_password_hash


# --- Ensure database exists before proceeding ---
from .config import DATABASE_URL, DB_CREATE_DATABASE, DB_ECHO, DB_NAME, MYSQL_SERVER_URL

def ensure_database_exists():
    if DB_CREATE_DATABASE:
        temp_engine = create_engine(MYSQL_SERVER_URL)
        with temp_engine.connect() as conn:
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}"))
            conn.commit()
        temp_engine.dispose()

ensure_database_exists()

engine = create_engine(DATABASE_URL, echo=DB_ECHO)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(
        Integer, Identity(start=1), primary_key=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(
        Enum("admin", "vendor", "customer", name="user_role"),
        nullable=False,
        default="customer"
    )
    isVerified: Mapped[str] = mapped_column (Enum("pending", "verified"),
                                                nullable=False,
                                                default="verified")
    
    vendor_products: Mapped[list["Product"]] = relationship(
        foreign_keys="Product.vendor_id",
        back_populates="vendor"
    )
    created_products: Mapped[list["Product"]] = relationship(
        foreign_keys="Product.created_by",
        back_populates="creator"
    )
    cart_items: Mapped[list["CartItem"]] = relationship(back_populates="customer")
    orders: Mapped[list["Order"]] = relationship(back_populates="customer")
    reviews: Mapped[list["Review"]] = relationship(back_populates="customer")
    complaints_created: Mapped[list["Complaint"]] = relationship(
        foreign_keys="Complaint.customer_id",
        back_populates="customer",
    )
    complaints_handled: Mapped[list["Complaint"]] = relationship(
        foreign_keys="Complaint.handled_by",
        back_populates="handler",
    )
    chat_participations: Mapped[list["ChatParticipant"]] = relationship(
        back_populates="user"
    )
    sent_messages: Mapped[list["Message"]] = relationship(back_populates="sender")

    @property
    def userID(self) -> int:
        return self.user_id


class Product(Base):
    __tablename__ = "products"

    product_id: Mapped[int] = mapped_column(
        Integer, Identity(start=1), primary_key=True, autoincrement=True
    )
    vendor_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    model: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    warranty_period: Mapped[str | None] = mapped_column(String(100), nullable=True)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    carType: Mapped[str] = mapped_column(Enum("supercar", "motorcycle", "classic"))

    vendor: Mapped["User"] = relationship(
        foreign_keys=[vendor_id],
        back_populates="vendor_products",
    )
    creator: Mapped["User"] = relationship(
        foreign_keys=[created_by],
        back_populates="created_products",
    )
    images: Mapped[list["ProductImage"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
    )
    variations: Mapped[list["ProductVariation"]] = relationship(
        back_populates="product",
        passive_deletes=True,
    )
    reviews: Mapped[list["Review"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
    )


class ProductImage(Base):
    __tablename__ = "product_imgs"

    img_id: Mapped[int] = mapped_column(
        Integer, Identity(start=1), primary_key=True, autoincrement=True
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.product_id", ondelete="CASCADE"),
        nullable=False,
    )

    product: Mapped["Product"] = relationship(back_populates="images")


class ProductVariation(Base):
    __tablename__ = "product_var"

    var_id: Mapped[int] = mapped_column(
        Integer, Identity(start=1), primary_key=True, autoincrement=True
    )
    product_id: Mapped[int | None] = mapped_column(
        ForeignKey("products.product_id", ondelete="SET NULL"),
        nullable=True,
    )
    color: Mapped[str] = mapped_column(String(50), nullable=False)
    year: Mapped[str] = mapped_column(String(4), nullable=False)
    stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    product: Mapped["Product | None"] = relationship(back_populates="variations")
    cart_items: Mapped[list["CartItem"]] = relationship(
        back_populates="variation",
        cascade="all, delete-orphan",
    )
    order_items: Mapped[list["OrderItem"]] = relationship(back_populates="variation")


class CartItem(Base):
    __tablename__ = "cart_items"

    cart_item_id: Mapped[int] = mapped_column(
        Integer, Identity(start=1), primary_key=True, autoincrement=True
    )
    customer_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
    )
    var_id: Mapped[int] = mapped_column(
        ForeignKey("product_var.var_id", ondelete="CASCADE"),
        nullable=False,
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    customer: Mapped["User"] = relationship(back_populates="cart_items")
    variation: Mapped["ProductVariation"] = relationship(back_populates="cart_items")


class Order(Base):
    __tablename__ = "orders"

    order_id: Mapped[int] = mapped_column(
        Integer, Identity(start=1), primary_key=True, autoincrement=True
    )
    customer_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    order_date: Mapped[DateTime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )
    total_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[str] = mapped_column(
        Enum(
            "pending",
            "confirmed",
            "handed_to_delivery",
            "shipped",
            name="order_status",
        ),
        nullable=False,
        default="pending",
    )

    customer: Mapped["User"] = relationship(back_populates="orders")
    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
    )


class OrderItem(Base):
    __tablename__ = "order_items"

    order_item_id: Mapped[int] = mapped_column(
        Integer, Identity(start=1), primary_key=True, autoincrement=True
    )
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.order_id", ondelete="CASCADE"),
        nullable=False,
    )
    var_id: Mapped[int] = mapped_column(ForeignKey("product_var.var_id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    order: Mapped["Order"] = relationship(back_populates="items")
    variation: Mapped["ProductVariation"] = relationship(back_populates="order_items")
    complaints: Mapped[list["Complaint"]] = relationship(back_populates="order_item")


class Review(Base):
    __tablename__ = "reviews"

    review_id: Mapped[int] = mapped_column(
        Integer, Identity(start=1), primary_key=True, autoincrement=True
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.product_id", ondelete="CASCADE"),
        nullable=False,
    )
    customer_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
    )
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    img_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    review_date: Mapped[DateTime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    product: Mapped["Product"] = relationship(back_populates="reviews")
    customer: Mapped["User"] = relationship(back_populates="reviews")


class Complaint(Base):
    __tablename__ = "complaints"

    complaint_id: Mapped[int] = mapped_column(
        Integer, Identity(start=1), primary_key=True, autoincrement=True
    )
    customer_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    order_item_id: Mapped[int] = mapped_column(
        ForeignKey("order_items.order_item_id"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    demand: Mapped[str] = mapped_column(
        Enum("return", "refund", "warranty_claim", name="complaint_demand"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        Enum(
            "pending",
            "rejected",
            "confirmed",
            "processing",
            "complete",
            name="complaint_status",
        ),
        nullable=False,
        default="pending",
    )
    handled_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.user_id"),
        nullable=True,
    )

    customer: Mapped["User"] = relationship(
        foreign_keys=[customer_id],
        back_populates="complaints_created",
    )
    order_item: Mapped["OrderItem"] = relationship(back_populates="complaints")
    handler: Mapped["User | None"] = relationship(
        foreign_keys=[handled_by],
        back_populates="complaints_handled",
    )
    images: Mapped[list["ComplaintImage"]] = relationship(
        back_populates="complaint",
        cascade="all, delete-orphan",
    )
    messages: Mapped[list["Message"]] = relationship(back_populates="related_complaint")


class ComplaintImage(Base):
    __tablename__ = "complaint_imgs"

    c_img_id: Mapped[int] = mapped_column(
        Integer, Identity(start=1), primary_key=True, autoincrement=True
    )
    complaint_id: Mapped[int] = mapped_column(
        ForeignKey("complaints.complaint_id", ondelete="CASCADE"),
        nullable=False,
    )

    complaint: Mapped["Complaint"] = relationship(back_populates="images")


class Conversation(Base):
    __tablename__ = "conversations"

    conversation_id: Mapped[int] = mapped_column(
        Integer, Identity(start=1), primary_key=True, autoincrement=True
    )

    participants: Mapped[list["ChatParticipant"]] = relationship(
        back_populates="conversation",
        cascade="all, delete-orphan",
    )
    messages: Mapped[list["Message"]] = relationship(
        back_populates="conversation",
        cascade="all, delete-orphan",
    )


class ChatParticipant(Base):
    __tablename__ = "chat_participants"

    participant_id: Mapped[int] = mapped_column(
        Integer, Identity(start=1), primary_key=True, autoincrement=True
    )
    conversation_id: Mapped[int] = mapped_column(
        ForeignKey("conversations.conversation_id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)

    conversation: Mapped["Conversation"] = relationship(back_populates="participants")
    user: Mapped["User"] = relationship(back_populates="chat_participations")


class Message(Base):
    __tablename__ = "messages"

    message_id: Mapped[int] = mapped_column(
        Integer, Identity(start=1), primary_key=True, autoincrement=True
    )
    conversation_id: Mapped[int] = mapped_column(
        ForeignKey("conversations.conversation_id", ondelete="CASCADE"),
        nullable=False,
    )
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    message_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    img_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    sent_at: Mapped[DateTime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )
    related_complaint_id: Mapped[int | None] = mapped_column(
        ForeignKey("complaints.complaint_id"),
        nullable=True,
    )

    conversation: Mapped["Conversation"] = relationship(back_populates="messages")
    sender: Mapped["User"] = relationship(back_populates="sent_messages")
    related_complaint: Mapped["Complaint | None"] = relationship(
        back_populates="messages"
    )


Base.metadata.create_all(engine)


with Session(engine) as event:
    exists = event.scalars(select(User).where(User.email == "admin@tsct.com")).first()
    if not exists:
        event.add(
            User(
                name="Admin",
                username="admin",
                email="admin@tsct.com",
                password=generate_password_hash("adminPW"),
                role="admin",
                isVerified="verified"
            )
        )
        event.commit()
