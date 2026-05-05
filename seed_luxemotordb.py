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
            email="admin@luxemotor.com",
            username="admin",
            password=generate_password_hash("246850"),
            role="admin",
            isVerified="verified",
        ),
        "vendor_1": User(
            name="Lamborghini",
            email="lamborghini@luxemotor.com",
            username="Lambo",
            password=generate_password_hash("123"),
            role="vendor",
            isVerified="verified",
        ),
        "vendor_2": User(
            name="Corvette",
            email="corvette@luxemotor.com",
            username="Corvette",
            password=generate_password_hash("123"),
            role="vendor",
            isVerified="verified",
        ),
        "vendor_3": User(
            name="Vyrus",
            email="vyrus@luxemotor.com",
            username="Vyrus",
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
        # Lamborghini
        "lamborghini_aventador": Product(
            vendor_id=users["vendor_1"].user_id,
            model="Lamborghini Aventador",
            description="Flagship V12 supercar.",
            warranty_period="36 months",
            price=507353.00,
            created_by=users["vendor_1"].user_id,
            carType="supercar",
        ),
        "lamborghini_huracan": Product(
            vendor_id=users["vendor_1"].user_id,
            model="Lamborghini Huracán EVO",
            description="V10 precision supercar.",
            warranty_period="36 months",
            price=261274.00,
            created_by=users["vendor_1"].user_id,
            carType="supercar",
        ),
        "lamborghini_revuelto": Product(
            vendor_id=users["vendor_1"].user_id,
            model="Lamborghini Revuelto",
            description="Hybrid V12 hyper-performance.",
            warranty_period="48 months",
            price=608358.00,
            created_by=users["vendor_1"].user_id,
            carType="supercar",
        ),

        # Corvette
        "corvette_stingray_1967": Product(
            vendor_id=users["vendor_2"].user_id,
            model="1967 Corvette Stingray",
            description="Iconic American classic.",
            warranty_period="12 months",
            price=85000.00,
            created_by=users["vendor_2"].user_id,
            carType="classic",
        ),
        "corvette_c1_1958": Product(
            vendor_id=users["vendor_2"].user_id,
            model="1958 Corvette C1",
            description="First-gen collectible.",
            warranty_period="12 months",
            price=72000.00,
            created_by=users["vendor_2"].user_id,
            carType="classic",
        ),
        "corvette_c3_1970": Product(
            vendor_id=users["vendor_2"].user_id,
            model="1970 Corvette C3",
            description="Retro performance classic.",
            warranty_period="12 months",
            price=65000.00,
            created_by=users["vendor_2"].user_id,
            carType="classic",
        ),

        # Vyrus
        "vyrus_987_c3": Product(
            vendor_id=users["vendor_3"].user_id,
            model="Vyrus 987 C3 4V",
            description="Exotic motorcycle.",
            warranty_period="24 months",
            price=92000.00,
            created_by=users["vendor_3"].user_id,
            carType="motorcycle",
        ),
        "vyrus_986_m2": Product(
            vendor_id=users["vendor_3"].user_id,
            model="Vyrus 986 M2",
            description="Radical engineering bike.",
            warranty_period="24 months",
            price=88000.00,
            created_by=users["vendor_3"].user_id,
            carType="motorcycle",
        ),
        "vyrus_984_c3": Product(
            vendor_id=users["vendor_3"].user_id,
            model="Vyrus 984 C3",
            description="Agile exotic bike.",
            warranty_period="24 months",
            price=83000.00,
            created_by=users["vendor_3"].user_id,
            carType="motorcycle",
        ),
    }

    session.add_all(products.values())
    session.flush()

    session.add_all(
        [
            ProductImage(product_id=products["lamborghini_aventador"].product_id),
            ProductImage(product_id=products["lamborghini_huracan"].product_id),
            ProductImage(product_id=products["corvette_stingray_1967"].product_id),
            ProductImage(product_id=products["vyrus_987_c3"].product_id),
        ]
    )

    return products


def seed_variations(session: Session, products: dict[str, Product]) -> dict[str, ProductVariation]:
    variations = {
        "aventador_black_2024": ProductVariation(
            product_id=products["lamborghini_aventador"].product_id,
            color="Black",
            year="2024",
            stock=2,
        ),
        "huracan_yellow_2024": ProductVariation(
            product_id=products["lamborghini_huracan"].product_id,
            color="Yellow",
            year="2024",
            stock=2,
        ),
        "vyrus987_black_2024": ProductVariation(
            product_id=products["vyrus_987_c3"].product_id,
            color="Black",
            year="2024",
            stock=2,
        ),
    }

    session.add_all(variations.values())
    session.flush()
    return variations


def seed_transactions(session, users, variations):
    session.add_all(
        [
            CartItem(
                customer_id=users["customer_1"].user_id,
                var_id=variations["aventador_black_2024"].var_id,
                quantity=1,
            ),
            CartItem(
                customer_id=users["customer_2"].user_id,
                var_id=variations["vyrus987_black_2024"].var_id,
                quantity=1,
            ),
        ]
    )

    order = Order(
        customer_id=users["customer_1"].user_id,
        order_date=datetime.now(),
        total_price=507353.00,
        status="confirmed",
    )

    session.add(order)
    session.flush()

    order_item = OrderItem(
        order_id=order.order_id,
        var_id=variations["aventador_black_2024"].var_id,
        quantity=1,
        price=507353.00,
    )

    session.add(order_item)
    session.flush()

    return {"order_item": order_item}


def seed_feedback_and_chat(session, users, products, order_items):
    session.add(
        Review(
            product_id=products["lamborghini_huracan"].product_id,
            customer_id=users["customer_1"].user_id,
            rating=5,
            description="Amazing car.",
            img_url=None,
            review_date=datetime.now(),
        )
    )

    complaint = Complaint(
        customer_id=users["customer_1"].user_id,
        order_item_id=order_items["order_item"].order_item_id,
        title="Paint issue",
        description="Minor defect.",
        demand="refund",
        status="processing",
        handled_by=users["admin"].user_id,
    )

    session.add(complaint)
    session.flush()

    session.add(ComplaintImage(complaint_id=complaint.complaint_id))

    convo = Conversation()
    session.add(convo)
    session.flush()

    session.add_all(
        [
            ChatParticipant(conversation_id=convo.conversation_id, user_id=users["customer_1"].user_id),
            ChatParticipant(conversation_id=convo.conversation_id, user_id=users["admin"].user_id),
        ]
    )

    session.add(
        Message(
            conversation_id=convo.conversation_id,
            sender_id=users["customer_1"].user_id,
            message_text="Issue with my car.",
            img_url=None,
            sent_at=datetime.now(),
            related_complaint_id=complaint.complaint_id,
        )
    )


def main():
    with Session(engine) as session:
        clear_existing_data(session)
        reset_auto_increment(session)
        users = seed_users(session)
        products = seed_products(session, users)
        variations = seed_variations(session, products)
        order_items = seed_transactions(session, users, variations)
        seed_feedback_and_chat(session, users, products, order_items)
        session.commit()

    print("Seed complete.")


if __name__ == "__main__":
    main()