from flask import Flask, request, session, url_for, render_template, flash, redirect, jsonify
import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash
from model import get_answer, get_chat, generate_text, summarization_data

app = Flask(__name__)
app.secret_key = 'your_unique_secret_key_here'  # Set a unique secret key for sessions

def create_connection():
    try:
        connection = mysql.connector.connect(
            host='127.0.0.1',  
            database='finforge',  
            user='root', 
            password='abdulrmohammed@38'
        )
        if connection.is_connected():
            print("Connected to MySQL database")
            return connection
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
    return None

@app.route('/')
def home():
    return render_template('temp.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        fullname = request.form.get('fullname')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Basic validation
        if not fullname or not email or not password or not confirm_password:
            flash('Please fill in all fields.', 'danger')
            return redirect(url_for('signup'))

        # Check if passwords match
        if password != confirm_password:
            flash('Passwords do not match. Please try again.', 'danger')
            return redirect(url_for('signup'))

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Store data in the database
        connection = create_connection()
        if connection is None:
            flash("Database connection failed. Please try again.", "danger")
            return redirect(url_for('signup'))

        cursor = connection.cursor()
        try:
            # Insert user into the database
            cursor.execute(
                '''INSERT INTO users (fullname, email, password) VALUES (%s, %s, %s)''',
                (fullname, email, hashed_password)
            )
            connection.commit()
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('services'))
        except mysql.connector.IntegrityError:
            flash('Email already exists. Please use a different email.', 'danger')
            return redirect(url_for('signup'))
        except Error as e:
            flash(f"An error occurred: {e}", 'danger')
            return redirect(url_for('signup'))
        finally:
            cursor.close()
            connection.close()

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Basic validation
        if not email or not password:
            flash('Please fill in all fields.', 'danger')
            return redirect(url_for('login'))

        # Database connection
        connection = create_connection()
        if connection is None:
            flash("Database connection failed. Please try again.", "danger")
            return redirect(url_for('login'))

        cursor = connection.cursor(dictionary=True)

        try:
            # Check if the user exists
            cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
            user = cursor.fetchone()

            if user and check_password_hash(user['password'], password):
                # Store session data
                session['logged_in'] = True
                session['user_id'] = user['id']
                session['user_email'] = user['email']

                flash('Login successful!', 'success')
                return redirect(url_for('services'))
            else:
                flash('Login failed. Incorrect email or password.', 'danger')
                return redirect(url_for('login'))
        except Error as e:
            flash(f"An error occurred: {e}", 'danger')
            return redirect(url_for('login'))
        finally:
            cursor.close()
            connection.close()

    return render_template('login.html')


@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/calculator')
def calculator():
    return render_template('calculator.html')

@app.route('/stock')
def stocks():
    return render_template('stock.html')

@app.route('/dashboard')
def dashboard():
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




@app.route('/logout')
def logout():
    # Clear the session data
    session.clear()  # This will remove all session data
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
