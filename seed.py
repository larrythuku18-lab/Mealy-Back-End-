"""
Seed script to populate the database with initial data matching the
frontend's mock data for development and testing.
"""
import bcrypt
from app import create_app
from config import db
from models import User, MealOption, DailyMenu, Category, Order, OrderItem


def seed_database():
    app = create_app()
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()

        # --- Categories ---
        categories = [
            Category(name='Breakfast'),
            Category(name='Lunch'),
            Category(name='Dinner'),
            Category(name='Snacks'),
            Category(name='Drinks'),
        ]
        for cat in categories:
            db.session.add(cat)
        db.session.flush()

        # --- Users ---
        admin_pw = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user_pw = bcrypt.hashpw('user123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        admin = User(
            name='Dev Admin',
            email='admin@mealy.com',
            password_hash=admin_pw,
            phone='+254 700 111 222',
            role='admin',
            caterer_id='dev-caterer',
            address='Nairobi, Kenya',
        )
        customer1 = User(
            name='Kev Mwangi',
            email='kev@mealy.com',
            password_hash=user_pw,
            phone='+254 700 333 444',
            role='user',
            caterer_id='dev-caterer',
            address='Westlands, Nairobi',
        )
        customer2 = User(
            name='Eugene Gaitano',
            email='eugene@mealy.com',
            password_hash=user_pw,
            phone='+254 700 555 666',
            role='user',
            caterer_id='dev-caterer',
            address='Kilimani, Nairobi',
        )
        customer3 = User(
            name='Larry Thuku',
            email='larry@mealy.com',
            password_hash=user_pw,
            phone='+254 700 777 888',
            role='user',
            caterer_id='dev-caterer',
            address='CBD, Nairobi',
        )
        customer4 = User(
            name='Joy Mwongera',
            email='joy@mealy.com',
            password_hash=user_pw,
            phone='+254 700 999 000',
            role='user',
            caterer_id='dev-caterer',
            address='Kasarani, Nairobi',
        )

        for u in [admin, customer1, customer2, customer3, customer4]:
            db.session.add(u)
        db.session.flush()

        # --- Meal Options ---
        # No `image` set: the frontend generates a food-themed SVG
        # illustration from the name/description when there's no photo,
        # which looks better than a placeholder box and (unlike a
        # placehold.co-style placeholder) doesn't bake redundant text into
        # the image itself.
        meal_options = [
            MealOption(name='Pancake Stack', description='Fluffy pancakes with maple syrup and fresh berries', price=850, category='Breakfast', caterer_id='dev-caterer'),
            MealOption(name='Caesar Salad', description='Romaine lettuce, parmesan, croutons, and Caesar dressing', price=1000, category='Lunch', caterer_id='dev-caterer'),
            MealOption(name='Grilled Chicken Pasta', description='Penne pasta with grilled chicken in Alfredo sauce', price=1400, category='Dinner', caterer_id='dev-caterer'),
            MealOption(name='Avocado Toast', description='Sourdough toast topped with smashed avocado and poached egg', price=900, category='Breakfast', caterer_id='dev-caterer'),
            MealOption(name='Berry Smoothie', description='Mixed berries blended with yogurt and honey', price=650, category='Drinks', caterer_id='dev-caterer'),
            MealOption(name='Grilled Salmon', description='Atlantic salmon with lemon butter and roasted vegetables', price=1800, category='Dinner', caterer_id='dev-caterer'),
            MealOption(name='Chicken Wrap', description='Grilled chicken, veggies, and hummus in a whole wheat wrap', price=1100, category='Lunch', caterer_id='dev-caterer'),
            MealOption(name='Energy Bites', description='Oat and peanut butter energy balls with dark chocolate chips', price=500, category='Snacks', caterer_id='dev-caterer'),
            MealOption(name='Iced Lemon Tea', description='Refreshing iced tea with fresh lemon and mint', price=400, category='Drinks', caterer_id='dev-caterer'),
            MealOption(name='Mushroom Omelette', description='Three-egg omelette with sautéed mushrooms and cheese', price=950, category='Breakfast', caterer_id='dev-caterer'),
            MealOption(name='French Toast', description='Golden brioche French toast with berry syrup and powdered sugar', price=800, category='Breakfast', caterer_id='dev-caterer'),
            MealOption(name='Greek Yogurt Parfait', description='Layers of Greek yogurt, granola, and mixed berries', price=600, category='Breakfast', caterer_id='dev-caterer'),
            MealOption(name='Club Sandwich', description='Triple-decker sandwich with chicken, bacon, lettuce, and tomato', price=1050, category='Lunch', caterer_id='dev-caterer'),
            MealOption(name='Margherita Pizza', description='Wood-fired pizza with tomato, fresh mozzarella, and basil', price=1500, category='Lunch', caterer_id='dev-caterer'),
            MealOption(name='Beef Stir Fry', description='Tender beef strips stir-fried with mixed vegetables in soy sauce', price=1600, category='Dinner', caterer_id='dev-caterer'),
            MealOption(name='Vegetable Curry', description='Mixed vegetables simmered in a fragrant coconut curry sauce', price=1200, category='Dinner', caterer_id='dev-caterer'),
            MealOption(name='Loaded Nachos', description='Crispy tortilla chips topped with cheese, jalapenos, and salsa', price=750, category='Snacks', caterer_id='dev-caterer'),
            MealOption(name='Hummus with Pita', description='Creamy hummus served with warm pita bread and olive oil', price=550, category='Snacks', caterer_id='dev-caterer'),
            MealOption(name='Mango Juice', description='Freshly squeezed mango juice, chilled and served over ice', price=450, category='Drinks', caterer_id='dev-caterer'),
            MealOption(name='Cappuccino', description='Espresso topped with steamed milk and a layer of foam', price=350, category='Drinks', caterer_id='dev-caterer'),
            MealOption(name='Ugali with Sukuma Wiki', description='Traditional cornmeal ugali served with sautéed collard greens', price=500, category='Breakfast', caterer_id='dev-caterer'),
            MealOption(name='Mandazi', description='Sweet, lightly spiced East African doughnuts, perfect with tea', price=300, category='Breakfast', caterer_id='dev-caterer'),
            MealOption(name='Bacon and Eggs', description='Crispy bacon strips with two sunny-side-up eggs and toast', price=750, category='Breakfast', caterer_id='dev-caterer'),
            MealOption(name='Breakfast Burrito', description='Scrambled eggs, cheese, and sausage wrapped in a warm tortilla', price=850, category='Breakfast', caterer_id='dev-caterer'),
            MealOption(name='Nyama Choma', description='Kenyan-style grilled goat meat, char-grilled and served with kachumbari', price=1700, category='Lunch', caterer_id='dev-caterer'),
            MealOption(name='Beef Burger', description='Juicy beef patty with cheddar, lettuce, and special sauce in a brioche bun', price=1200, category='Lunch', caterer_id='dev-caterer'),
            MealOption(name='Falafel Wrap', description='Crispy falafel, hummus, and fresh veggies in a warm pita wrap', price=950, category='Lunch', caterer_id='dev-caterer'),
            MealOption(name='Fish Tacos', description='Grilled tilapia tacos with cabbage slaw and lime crema', price=1150, category='Lunch', caterer_id='dev-caterer'),
            MealOption(name='Pilau Rice with Beef', description='Fragrant spiced rice cooked with tender beef and whole spices', price=1450, category='Dinner', caterer_id='dev-caterer'),
            MealOption(name='Butter Chicken', description='Creamy tomato-based curry with tender chicken pieces', price=1550, category='Dinner', caterer_id='dev-caterer'),
            MealOption(name='Beef Biryani', description='Fragrant basmati rice layered with spiced beef and caramelized onions', price=1650, category='Dinner', caterer_id='dev-caterer'),
            MealOption(name='Grilled Tilapia', description='Whole grilled tilapia fish with lemon butter sauce and fresh vegetables', price=1750, category='Dinner', caterer_id='dev-caterer'),
            MealOption(name='Beef Samosas', description='Crispy pastry pockets filled with spiced beef and peas', price=450, category='Snacks', caterer_id='dev-caterer'),
            MealOption(name='Buffalo Chicken Wings', description='Spicy buffalo chicken wings served with ranch dip', price=900, category='Snacks', caterer_id='dev-caterer'),
            MealOption(name='Sweet Potato Fries', description='Crispy baked sweet potato fries with a hint of paprika', price=500, category='Snacks', caterer_id='dev-caterer'),
            MealOption(name='Popcorn Chicken', description='Bite-sized crispy fried chicken pieces, perfectly seasoned', price=650, category='Snacks', caterer_id='dev-caterer'),
            MealOption(name='Passion Fruit Juice', description='Freshly squeezed passion fruit juice, tangy and refreshing', price=400, category='Drinks', caterer_id='dev-caterer'),
            MealOption(name='Ginger Tea', description='Spiced ginger tea, warming and aromatic', price=300, category='Drinks', caterer_id='dev-caterer'),
            MealOption(name='Mocha', description='Espresso with steamed milk and rich chocolate syrup', price=400, category='Drinks', caterer_id='dev-caterer'),
            MealOption(name='Watermelon Juice', description='Chilled watermelon juice, naturally sweet and hydrating', price=400, category='Drinks', caterer_id='dev-caterer'),
        ]
        for mo in meal_options:
            db.session.add(mo)
        db.session.flush()

        # --- Daily Menu (today's published menu) ---
        from datetime import date
        today_menu = DailyMenu(
            date=date.today(),
            is_published=True,
            caterer_id=admin.caterer_id,
        )
        today_menu.set_meal_option_ids([1, 2, 3, 4, 5])
        db.session.add(today_menu)

        # --- Sample Orders ---
        order1 = Order(user_id=customer1.id, total_amount=2350, status='delivered', date=date.today())
        db.session.add(order1)
        db.session.flush()

        db.session.add(OrderItem(order_id=order1.id, meal_option_id=1, quantity=2, price=850))
        db.session.add(OrderItem(order_id=order1.id, meal_option_id=5, quantity=1, price=650))

        order2 = Order(user_id=customer2.id, total_amount=2200, status='in_transit', date=date.today())
        db.session.add(order2)
        db.session.flush()

        db.session.add(OrderItem(order_id=order2.id, meal_option_id=3, quantity=1, price=1400))
        db.session.add(OrderItem(order_id=order2.id, meal_option_id=9, quantity=2, price=400))

        order3 = Order(user_id=customer3.id, total_amount=1000, status='preparing', date=date.today())
        db.session.add(order3)
        db.session.flush()

        db.session.add(OrderItem(order_id=order3.id, meal_option_id=2, quantity=1, price=1000))

        db.session.commit()
        print('Database seeded successfully!')


if __name__ == '__main__':
    seed_database()
