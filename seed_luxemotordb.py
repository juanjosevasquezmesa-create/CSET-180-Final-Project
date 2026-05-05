from datetime import datetime

from sqlalchemy import delete, text
from sqlalchemy.orm import Session
from werkzeug.security import generate_password_hash

from backend.models import (
    CartItem,
    ChatParticipant,
    Complaint,
    ComplaintImage,
    Conversation,
    Message,
    Order,
    OrderItem,
    Product,
    ProductImage,
    ProductVariation,
    Review,
    User,
    engine,
)


def clear_existing_data(session: Session) -> None:
    session.execute(delete(Message))
    session.execute(delete(ChatParticipant))
    session.execute(delete(Conversation))
    session.execute(delete(ComplaintImage))
    session.execute(delete(Complaint))
    session.execute(delete(Review))
    session.execute(delete(OrderItem))
    session.execute(delete(Order))
    session.execute(delete(CartItem))
    session.execute(delete(ProductVariation))
    session.execute(delete(ProductImage))
    session.execute(delete(Product))
    session.execute(delete(User))
    session.commit()


def reset_auto_increment(session: Session) -> None:
    table_names = [
        "messages",
        "chat_participants",
        "conversations",
        "complaint_imgs",
        "complaints",
        "reviews",
        "order_items",
        "orders",
        "cart_items",
        "product_var",
        "product_imgs",
        "products",
        "users",
    ]

    for table_name in table_names:
        session.execute(text(f"ALTER TABLE {table_name} AUTO_INCREMENT = 1"))

    session.commit()


def seed_users(session: Session) -> dict[str, User]:

    users = {
        "admin": User(
            name="Admin User",
            # change it to this if the team agrees
            # email="admin@luxemotor.com",
            email="admin@tsct.com",
            username="admin",
            password=generate_password_hash("246850"),
            role="admin",
            isVerified="verified",
        ),
        "vendor_1": User(
            name="Shane Mcraw",
            email="shane@luxemotor.com",
            username="shaneSales",
            password=generate_password_hash("123"),
            role="vendor",
            isVerified="verified",
        ),
        "vendor_2": User(
            name="Elena Alnna",
            email="elena@luxemotor.com",
            username="elenaStore",
            password=generate_password_hash("123"),
            role="vendor",
            isVerified="verified",
        ),
        "customer_1": User(
            name="Jordan Lebron",
            email="jordan@luxemotor.com",
            username="jordanStalion",
            password=generate_password_hash("123"),
            role="customer",
            isVerified="verified",
        ),
        "customer_2": User(
            name="Riley Shuemer",
            email="riley@luxemotor.com",
            username="riley4eva",
            password=generate_password_hash("123"),
            role="customer",
            isVerified="verified",
        ),
    }

    session.add_all(users.values())
    session.flush()
    return users


def seed_products(session: Session, users: dict[str, User]) -> dict[str, Product]:
    products = {
        "apex_touring": Product(
            vendor_id=users["vendor_1"].user_id,
            model="Apex S Touring",
            description="Luxury sport sedan with adaptive suspension, panoramic roof, and premium interior.",
            warranty_period="48 months",
            price=58999.99,
            created_by=users["vendor_1"].user_id,
        ),
        "apex_performance": Product(
            vendor_id=users["vendor_1"].user_id,
            model="Apex X Performance",
            description="High-performance coupe with twin-turbo power and track-ready braking package.",
            warranty_period="36 months",
            price=74999.50,
            created_by=users["vendor_1"].user_id,
        ),
        "velora_hybrid": Product(
            vendor_id=users["vendor_2"].user_id,
            model="Velora Hybrid LX",
            description="Efficient hybrid crossover with leather seats, driver assist, and smart navigation.",
            warranty_period="60 months",
            price=42995.00,
            created_by=users["vendor_2"].user_id,
        ),
        "velora_ev": Product(
            vendor_id=users["vendor_2"].user_id,
            model="Velora EV Grand",
            description="Fully electric grand touring SUV with long-range battery and fast charging.",
            warranty_period="96 months",
            price=81990.00,
            created_by=users["vendor_2"].user_id,
        ),
    }

    session.add_all(products.values())
    session.flush()

    session.add_all(
        [
            ProductImage(product_id=products["apex_touring"].product_id),
            ProductImage(product_id=products["apex_touring"].product_id),
            ProductImage(product_id=products["apex_performance"].product_id),
            ProductImage(product_id=products["velora_hybrid"].product_id),
            ProductImage(product_id=products["velora_ev"].product_id),
        ]
    )

    return products


def seed_variations(session: Session, products: dict[str, Product]) -> dict[str, ProductVariation]:
    variations = {
        "apex_black_2024": ProductVariation(
            product_id=products["apex_touring"].product_id,
            color="Obsidian Black",
            year="2024",
            stock=4,
        ),
        "apex_white_2025": ProductVariation(
            product_id=products["apex_touring"].product_id,
            color="Pearl White",
            year="2025",
            stock=3,
        ),
        "performance_red_2025": ProductVariation(
            product_id=products["apex_performance"].product_id,
            color="Crimson Red",
            year="2025",
            stock=2,
        ),
        "performance_gray_2024": ProductVariation(
            product_id=products["apex_performance"].product_id,
            color="Graphite Gray",
            year="2024",
            stock=1,
        ),
        "hybrid_blue_2025": ProductVariation(
            product_id=products["velora_hybrid"].product_id,
            color="Ocean Blue",
            year="2025",
            stock=6,
        ),
        "hybrid_silver_2024": ProductVariation(
            product_id=products["velora_hybrid"].product_id,
            color="Silver Mist",
            year="2024",
            stock=5,
        ),
        "ev_midnight_2025": ProductVariation(
            product_id=products["velora_ev"].product_id,
            color="Midnight Blue",
            year="2025",
            stock=2,
        ),
        "ev_gold_2025": ProductVariation(
            product_id=products["velora_ev"].product_id,
            color="Champagne Gold",
            year="2025",
            stock=1,
        ),
    }

    session.add_all(variations.values())
    session.flush()
    return variations


def seed_transactions(
    session: Session, users: dict[str, User], variations: dict[str, ProductVariation]
) -> dict[str, OrderItem]:
    session.add_all(
        [
            CartItem(
                customer_id=users["customer_1"].user_id,
                var_id=variations["performance_red_2025"].var_id,
                quantity=1,
            ),
            CartItem(
                customer_id=users["customer_1"].user_id,
                var_id=variations["hybrid_blue_2025"].var_id,
                quantity=1,
            ),
            CartItem(
                customer_id=users["customer_2"].user_id,
                var_id=variations["ev_midnight_2025"].var_id,
                quantity=1,
            ),
        ]
    )

    order_1 = Order(
        customer_id=users["customer_1"].user_id,
        order_date=datetime(2026, 4, 20, 10, 15, 0),
        total_price=42995.00,
        status="confirmed",
    )
    order_2 = Order(
        customer_id=users["customer_2"].user_id,
        order_date=datetime(2026, 4, 22, 14, 45, 0),
        total_price=81990.00,
        status="shipped",
    )

    session.add_all([order_1, order_2])
    session.flush()

    order_items = {
        "hybrid_order_item": OrderItem(
            order_id=order_1.order_id,
            var_id=variations["hybrid_blue_2025"].var_id,
            quantity=1,
            price=42995.00,
        ),
        "ev_order_item": OrderItem(
            order_id=order_2.order_id,
            var_id=variations["ev_midnight_2025"].var_id,
            quantity=1,
            price=81990.00,
        ),
    }

    session.add_all(order_items.values())
    session.flush()
    return order_items


def seed_feedback_and_chat(
    session: Session,
    users: dict[str, User],
    products: dict[str, Product],
    order_items: dict[str, OrderItem],
) -> None:
    session.add_all(
        [
            Review(
                product_id=products["velora_hybrid"].product_id,
                customer_id=users["customer_1"].user_id,
                rating=5,
                description="Smooth drive, excellent fuel economy, and the cabin feels very premium.",
                img_url="https://example.com/reviews/hybrid-lx-review.jpg",
                review_date=datetime(2026, 4, 24, 9, 30, 0),
            ),
            Review(
                product_id=products["velora_ev"].product_id,
                customer_id=users["customer_2"].user_id,
                rating=4,
                description="Beautiful EV with strong acceleration. Charging network access could be better.",
                img_url="https://example.com/reviews/ev-grand-review.jpg",
                review_date=datetime(2026, 4, 26, 18, 20, 0),
            ),
        ]
    )

    complaint_1 = Complaint(
        customer_id=users["customer_2"].user_id,
        order_item_id=order_items["ev_order_item"].order_item_id,
        title="Charging cable missing",
        description="The delivery arrived without the premium charging cable listed in the package contents.",
        demand="warranty_claim",
        status="processing",
        handled_by=users["admin"].user_id,
    )
    complaint_2 = Complaint(
        customer_id=users["customer_1"].user_id,
        order_item_id=order_items["hybrid_order_item"].order_item_id,
        title="Minor paint blemish",
        description="Found a small paint defect on the rear passenger door after delivery inspection.",
        demand="refund",
        status="confirmed",
        handled_by=users["admin"].user_id,
    )

    session.add_all([complaint_1, complaint_2])
    session.flush()

    session.add_all(
        [
            ComplaintImage(complaint_id=complaint_1.complaint_id),
            ComplaintImage(complaint_id=complaint_2.complaint_id),
        ]
    )

    conversation_1 = Conversation()
    conversation_2 = Conversation()
    session.add_all([conversation_1, conversation_2])
    session.flush()

    session.add_all(
        [
            ChatParticipant(
                conversation_id=conversation_1.conversation_id,
                user_id=users["customer_2"].user_id,
            ),
            ChatParticipant(
                conversation_id=conversation_1.conversation_id,
                user_id=users["admin"].user_id,
            ),
            ChatParticipant(
                conversation_id=conversation_1.conversation_id,
                user_id=users["vendor_2"].user_id,
            ),
            ChatParticipant(
                conversation_id=conversation_2.conversation_id,
                user_id=users["customer_1"].user_id,
            ),
            ChatParticipant(
                conversation_id=conversation_2.conversation_id,
                user_id=users["admin"].user_id,
            ),
            ChatParticipant(
                conversation_id=conversation_2.conversation_id,
                user_id=users["vendor_1"].user_id,
            ),
        ]
    )

    session.add_all(
        [
            Message(
                conversation_id=conversation_1.conversation_id,
                sender_id=users["customer_2"].user_id,
                message_text="Hi, my EV order arrived without the charging cable.",
                img_url=None,
                sent_at=datetime(2026, 4, 25, 8, 10, 0),
                related_complaint_id=complaint_1.complaint_id,
            ),
            Message(
                conversation_id=conversation_1.conversation_id,
                sender_id=users["admin"].user_id,
                message_text="Thanks for reporting it. We are reviewing the packing checklist now.",
                img_url=None,
                sent_at=datetime(2026, 4, 25, 8, 18, 0),
                related_complaint_id=complaint_1.complaint_id,
            ),
            Message(
                conversation_id=conversation_1.conversation_id,
                sender_id=users["vendor_2"].user_id,
                message_text="We have a replacement cable ready to ship today.",
                img_url=None,
                sent_at=datetime(2026, 4, 25, 9, 5, 0),
                related_complaint_id=complaint_1.complaint_id,
            ),
            Message(
                conversation_id=conversation_2.conversation_id,
                sender_id=users["customer_1"].user_id,
                message_text="There is a paint blemish on delivery. I uploaded a photo in the complaint.",
                img_url=None,
                sent_at=datetime(2026, 4, 26, 11, 12, 0),
                related_complaint_id=complaint_2.complaint_id,
            ),
            Message(
                conversation_id=conversation_2.conversation_id,
                sender_id=users["admin"].user_id,
                message_text="We have confirmed the issue and are evaluating the refund amount.",
                img_url=None,
                sent_at=datetime(2026, 4, 26, 11, 40, 0),
                related_complaint_id=complaint_2.complaint_id,
            ),
        ]
    )


def main() -> None:
    with Session(engine) as session:
        clear_existing_data(session)
        reset_auto_increment(session)
        users = seed_users(session)
        products = seed_products(session, users)
        variations = seed_variations(session, products)
        order_items = seed_transactions(session, users, variations)
        seed_feedback_and_chat(session, users, products, order_items)
        session.commit()

    print("Mock data inserted into luxemotordb.")
    print("Sample logins:")
    print("  admin / adminPW")
    print("  marco_vendor / vendorPW1")
    print("  elena_vendor / vendorPW2")
    print("  jordan_customer / customerPW1")
    print("  riley_customer / customerPW2")


if __name__ == "__main__":
    main()
