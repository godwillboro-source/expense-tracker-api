


from datetime import date

from app import app
from models import db, User, Category, Expense

with app.app_context():

    # reset data (children first, so nothing points at a deleted parent)
    print("Resetting database...")
    db.session.query(Expense).delete()
    db.session.query(Category).delete()
    db.session.query(User).delete()
    db.session.commit()

    # -----User Data-----
    print("seeding user data...")
    alice = User(username="alice")
    alice.password_hash = "password123"  
    bob = User(username="bob")
    bob.password_hash = "password123"

    db.session.add_all([alice, bob])
    db.session.commit()  

    # -----Category Data-----
    print("seeding category data...")
    alice_food = Category(name="Food", user_id=alice.id)
    alice_transport = Category(name="Transport", user_id=alice.id)
    alice_bills = Category(name="Bills", user_id=alice.id)
    bob_food = Category(name="Food", user_id=bob.id)      # same name is fine for a different user
    bob_fun = Category(name="Entertainment", user_id=bob.id)

    db.session.add_all([alice_food, alice_transport, alice_bills, bob_food, bob_fun])
    db.session.commit()

    # -----Expense Data-----
    print("seeding expense data...")
    expenses = [
        # alice's expenses
        Expense(title="Groceries", amount=6500, date=date(2026, 10, 27), user_id=alice.id, category_id=alice_food.id),
        Expense(title="Lunch", amount=3500, date=date(2026, 10, 28), user_id=alice.id, category_id=alice_food.id),
        Expense(title="Bus fare", amount=300, date=date(2026, 10, 28), user_id=alice.id, category_id=alice_transport.id),
        Expense(title="Fuel", amount=4000, date=date(2026, 10, 29), user_id=alice.id, category_id=alice_transport.id),
        Expense(title="Electricity", amount=7890, date=date(2026, 10, 30), user_id=alice.id, category_id=alice_bills.id),
        Expense(title="Birthday gift", amount=2500, date=date(2026, 10, 30), user_id=alice.id),  # no category
        # bob's expenses
        Expense(title="Coffee", amount=475, date=date(2026, 10, 27), user_id=bob.id, category_id=bob_food.id),
        Expense(title="Dinner out", amount=3640, date=date(2026, 10, 29), user_id=bob.id, category_id=bob_food.id),
        Expense(title="Movie night", amount=1500, date=date(2026, 10, 30), user_id=bob.id, category_id=bob_fun.id),
    ]

    db.session.add_all(expenses)
    db.session.commit()

    print("Seeding complete!")