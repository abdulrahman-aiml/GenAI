from flask import Flask, request, render_template, jsonify
from model import get_answer, get_chat, generate_text, summarization_data
import numpy as np # Import the function to get chatbot answers

app = Flask(__name__)

# Route to the home page
@app.route('/')
def home():
    return render_template('temp.html')

# Route to the signup page
@app.route('/signup')
def signup():
    return render_template('signup.html')

# Route to the login page
@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/calculator')
def calculator():
    return render_template('calculator.html')

@app.route('/stock')
def stock():
    return render_template('stock.html')

# Route to the dashboard page
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if request.method == 'POST':
        # Get user input from form
        values = {
            'income': request.form.get('income', 0),
            'expenditure': request.form.get('expenditure', 0),
            'month': request.form.get('month', 'Unknown')
        }

        # Call summarization function using Flan-T5
        summary = summarization_data(values)

        # Pass summarized data back to the dashboard template
        return render_template('dashboard.html', summary=summary, **values)
    
    # GET request: Just render the dashboard without processing
    return render_template('dashboard.html')

# Route to the chatbot page
@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')

# Route to handle chatbot response generation
import random
from flask import Flask, request, jsonify


@app.route('/generate-response', methods=['POST'])
def generate_response():
    try:
        # Get JSON data from the request (user input)
        data = request.get_json()
        user_input = data.get('user_input')

        # Check if user_input is not empty
        if user_input:
            # Check if user input is a greeting
            salutation_response = [
    "You're welcome", 
    "My pleasure", 
    "It's my job", 
    "Happy to help", 
    "No problem", 
    "Glad I could assist", 
    "Anytime", 
    "It was nothing", 
    "I'm here for you", 
    "Always happy to help"
]

            salutations = ['thanks', 'nice', 'good', 'wonderful', 'excellent', 'awesome', 'great','perfect']
            greetings = ["hi", "hello", "hey", "greetings", "good morning", "good evening", "howdy"]
            
            if any(greeting in user_input.lower() for greeting in greetings):
                answer = "Hello! How can I assist you today?"
            # Classify whether it's a Q&A or text generation request
            elif any(salutation in user_input.lower() for salutation in salutations):
                answer = random.choice(salutation_response) + '. Let me know if you need anything else!'
            elif "?" in user_input:  # Simple heuristic: if input contains a "?", treat as Q&A
                # Generate a Q&A response
                answer = get_answer(user_input)
            else:
                # Otherwise, treat it as a text generation request
                answer = generate_text(user_input)
        else:
            answer = "Sorry, I didn't get that. Can you please rephrase?"

        # Return the chatbot response as JSON
        return jsonify({'response': answer})
    
    except Exception as e:
        # Handle any exceptions and return a generic error message
        return jsonify({'response': "An error occurred. Please try again later."})


# Run the Flask app only if this script is executed directly
if __name__ == "__main__":
    # Run the Flask app on all available IP addresses (0.0.0.0) at port 5000 in debug mode
    app.run(host='0.0.0.0', port=5000, debug=True)
