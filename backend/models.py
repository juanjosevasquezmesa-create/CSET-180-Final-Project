from sqlalchemy import Enum, Identity, Integer, String, create_engine, select, text
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column
from werkzeug.security import generate_password_hash

from backend.config import DATABASE_URL, DB_CREATE_DATABASE, DB_ECHO, DB_NAME, MYSQL_SERVER_URL

conn_temp = create_engine(MYSQL_SERVER_URL)

if DB_CREATE_DATABASE:
    with conn_temp.connect() as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}"))
        conn.commit()

engine = create_engine(DATABASE_URL, echo=DB_ECHO)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    userID: Mapped[int] = mapped_column(
        Integer, Identity(start=1), primary_key=True, autoincrement=True
    )
    firstName: Mapped[str] = mapped_column(String(50), nullable=True)
    lastName: Mapped[str] = mapped_column(String(50), nullable=True)
    phoneNumber: Mapped[str] = mapped_column(String(20), unique=True, nullable=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(75), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(
        Enum("admin", "vendor", "customer", name="user_role"),
        nullable=False,
        default="customer",
    )


Base.metadata.create_all(engine)

with Session(engine) as event:
    exists = event.scalars(select(User).where(User.email == "admin@tsct.com")).first()

    if not exists:
        event.add(
            User(
                firstName="Admin",
                username="admin",
                email="admin@tsct.com",
                password=generate_password_hash("adminPW"),
                role="admin",
            )
        )
        event.commit()
