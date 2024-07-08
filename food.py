
from your_flask_app import db, Food

# Example data
foods = [
    {'name': 'Hot Soup', 'price': 5.99, 'suitable_weather': 'Cold'},
    {'name': 'Ice Cream', 'price': 3.99, 'suitable_weather': 'Hot'},
    {'name': 'Salad', 'price': 7.49, 'suitable_weather': 'Mild'},
]

with app.app_context():
    for food in foods:
        new_food = Food(name=food['name'], price=food['price'], suitable_weather=food['suitable_weather'])
        db.session.add(new_food)
    db.session.commit()
