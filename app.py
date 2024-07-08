from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import openai
import requests
from flask_mysqldb import MySQL


app = Flask(__name__)
CORS(app)


    # # Create a cursor object
    # cur = mysql.connection.cursor()
    # # Execute a query
    # cur.execute('''SELECT * FROM yourtable''')
    # # Fetch all the results
    # results = cur.fetchall()
    # # Close the cursor
    # cur.close()
    # # Return the results as JSON
    # return jsonify(results)

# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:password123@localhost/food_delivery_db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db = SQLAlchemy(app)

openai.api_key = ''
weather_api_key = ''
#apiKey = ''

# Define User session dictionary
user_sessions = {}

# Food model
#class Food(db.Model):
   # id = db.Column(db.Integer, primary_key=True)
   # name = db.Column(db.String(100), nullable=False)
   # price = db.Column(db.Float, nullable=False)
   # suitable_weather = db.Column(db.String(50), nullable=False)

# Initialize database
# with app.app_context():
#     db.create_all()

# Weather fetching function
def get_weather(location):
    #location="27.7006, 83.4484"
    lat="27.7006"
    lon="83.4484"
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={weather_api_key}"
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for HTTP errors
    data = response.json()
    #return data
    return data['weather'][0]['main']

# ChatGPT function
def get_chat_response(prompt):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150
    )
    return response.choices[0].text.strip()

@app.route('/chat', methods=['POST'])
def chat():
    user_id = request.json.get('user_id')
    #return (user_id)
    user_message = request.json.get('message')
    location = request.json.get('location', 'Default Location')  # Default location for weather
    #return (location)
    if user_id not in user_sessions:
        
        user_sessions[user_id] = {'state': 'suggest_food', 'data': {'selected_foods': []}}
       
    
    session = user_sessions[user_id]
    state = session['state']
    #return (state)
    if state == 'suggest_food':
        weather_condition = get_weather(location)
        #return (weather_condition)
        session['data']['weather'] = weather_condition
        app.config['MYSQL_HOST'] = 'localhost'
        app.config['MYSQL_USER'] = 'root'
        app.config['MYSQL_PASSWORD'] = 'password123'
        app.config['MYSQL_DB'] = 'food_delivery_db'

        mysql = MySQL(app)
        #return (mysql)
        cur = mysql.connection.cursor()
        # Execute a query
        cur.execute('''SELECT * FROM foods''')
        # Fetch all the results
        results = cur.fetchall()
        # Close the cursor
        cur.close()
        return jsonify(results)
        # Return the results as JSON
        #return jsonify(results)
        #suitable_foods = Food.query.filter_by(suitable_weather=weather_condition).all()
        response_text = f"The weather is currently {weather_condition}. Based on the weather, we suggest the following foods:\n"
        return (suitable_foods)

        options = []
        for food in suitable_foods:
            options.append(f"{food.name} - ${food.price}")
        
        response_text += "\n".join(options)
        response_text += "\n\nPlease type the food(s) you would like to order, separated by commas."
        session['state'] = 'collect_food_choices'
    elif state == 'collect_food_choices':
        selected_food_names = [f.strip() for f in user_message.split(',')]
        selected_foods = Food.query.filter(Food.name.in_(selected_food_names)).all()

        if not selected_foods:
            response_text = "Sorry, we couldn't find the selected food items. Please choose from the suggested options."
        else:
            session['data']['selected_foods'] = selected_foods
            session['state'] = 'collect_name'
            response_text = "Great choice! To proceed, please provide your name."
    elif state == 'collect_name':
        session['data']['name'] = user_message
        session['state'] = 'collect_address'
        response_text = "Thank you. Please provide your address."
    elif state == 'collect_address':
        session['data']['address'] = user_message
        session['state'] = 'collect_phone'
        response_text = "Almost done! Please provide your phone number."
    elif state == 'collect_phone':
        session['data']['phone'] = user_message
        
        total_price = sum(food.price for food in session['data']['selected_foods'])
        response_text = (f"Thank you, {session['data']['name']}! Here is the information you provided:\n"
                         f"Address: {session['data']['address']}\n"
                         f"Phone: {session['data']['phone']}\n"
                         "Your order summary:\n")
        
        for food in session['data']['selected_foods']:
            response_text += f"{food.name} - ${food.price}\n"
        
        response_text += f"Total Price: ${total_price}\n"
        response_text += "We will contact you soon to confirm your order."
        session['state'] = 'complete'
    else:
        response_text = "Your order is complete. Thank you!"

    # Integrate ChatGPT for natural language understanding and response enhancement
    chatgpt_response = get_chat_response(response_text)
    final_response = f"{response_text}\n\nChatGPT: {chatgpt_response}"

    return jsonify({"response": final_response})

if __name__ == '__main__':
    app.run(debug=True)
