from flask import Flask, request, jsonify
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import difflib
import openai
import mysql.connector
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="admin",
            database="user",
            buffered=True  # Enable buffered cursor
        )
        
        # Create a cursor to execute SQL queries
        cursor = connection.cursor()
        
        # SQL query to create the users table if it doesn't exist
        create_table_query = """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(255) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL
        )
        """
        
        # Execute the SQL query to create the table
        cursor.execute(create_table_query)
        
        # Commit the changes to the database
        connection.commit()
        
        return connection
    
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

# Load data and set up necessary variables
df1 = pd.read_csv('Formulation-Indications.csv')
formulations_lst = list(df1['Name of Medicine'])
original_list = list(df1['Main Indications'])
processed_list = [''.join(item.split()).lower() for item in original_list]

symptoms = pd.read_csv('ayurvedic_symptoms_desc.csv')
symptoms['Symptom'] = symptoms['Symptom'].str.lower()
correct_words = list(set(symptom for sublist in processed_list for symptom in sublist.split(',')))

# Function to correct symptoms
def correct_symptoms(symptoms):
    corrected_symptoms = []
    for symptom in symptoms:
        corrected_symptom = difflib.get_close_matches(symptom, correct_words, n=1, cutoff=0.6)
        if corrected_symptom:
            corrected_symptoms.append(corrected_symptom[0])
        else:
            corrected_symptoms.append(symptom)
    return corrected_symptoms

# Function to calculate closest formulations
def get_closest_formulations(user_symptoms_str):
    # Create DataFrame
    df = pd.DataFrame({"Formulation": formulations_lst, "Symptoms": processed_list})
    # Create TF-IDF vectorizer
    tfidf_vectorizer = TfidfVectorizer()
    # Fit and transform symptom text data into numerical features
    tfidf_matrix = tfidf_vectorizer.fit_transform(df['Symptoms'])
    # Transform user symptoms into TF-IDF format
    user_symptoms_tfidf = tfidf_vectorizer.transform([user_symptoms_str])
    # Calculate cosine similarity between user's symptoms and all formulations
    similarities = cosine_similarity(user_symptoms_tfidf, tfidf_matrix)
    # Set a threshold for similarity score
    similarity_threshold = 0.5
    # Find all formulations with similarity scores above the threshold
    matching_indices = [i for i, sim in enumerate(similarities[0]) if sim > similarity_threshold]
    closest_formulations = df.iloc[matching_indices]["Formulation"].tolist()
    return closest_formulations

# Function to get symptom description
def symptoms_desc(symptom_name):
    row = symptoms[symptoms['Symptom'] == symptom_name.lower()]
    if not row.empty:
        description = row.iloc[0]['Description']
        return description
    else:
        return "Description not found."

# Function to generate response using OpenAI API
def generate_response(user_input):
    try:
        # Use an environment variable for the API key
        openai.api_key = "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"
        
        # Prepend a system message describing the chatbot's capabilities
        system_message = {
            "role": "system",
            "content": "You are an Ayurvedic Chatbot. You can give formulations based on the 'dosha' or can give any ayurvedic insight."
        }
        
        # User message
        user_message = {
            "role": "user",
            "content": user_input
        }
        
        # Generate response
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[system_message, user_message],
        )
        
        # Extract the text content of the response
        content = response.choices[0].message["content"].strip()
        
        return {"fulfillmentText": content}
    except Exception as e:
        print(f"Error generating response from OpenAI API: {e}")
        return {"error": "Internal Server Error"}
    

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_input = data.get('message', '')
        openai_response = generate_response(user_input)
        return jsonify(openai_response)
    except Exception as e:
        print(f"Error handling chat message: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@app.route('/formulations', methods=['POST'])
def get_formulations():
    try:
        data = request.get_json()
        symptoms = data.get('symptoms', '')
        user_symptoms = correct_symptoms(symptoms.split())
        user_symptoms_str = " ".join(user_symptoms)
        closest_formulations = get_closest_formulations(user_symptoms_str)
        
        # Filter the DataFrame to include only the closest formulations
        closest_formulations_df = df1[df1['Name of Medicine'].isin(closest_formulations)]
        
        # Convert the filtered DataFrame to a list of dictionaries
        formulations_info = closest_formulations_df.to_dict(orient='records')
        
        return jsonify({"formulations": formulations_info})
    except Exception as e:
        print(f"Error getting formulations: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        mydb = get_db_connection()
        cursor = mydb.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
        user = cursor.fetchone()
        
        # Ensure the cursor is closed after fetching the result
        cursor.close()
        
        # Properly handle the result before closing the connection
        if user:
            mydb.close()  # Close the connection after handling the result
            return jsonify({'message': 'Login successful'})
        else:
            mydb.close()  # Close the connection after handling the result
            return jsonify({'error': 'Invalid email or password'})
    except Exception as e:
        print(f"Error handling login request: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
@app.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        mydb = get_db_connection()
        cursor = mydb.cursor()
        
        # Check if the user already exists
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            cursor.close()
            mydb.close()
            return jsonify({'error': 'User already exists'})

        # If the user does not exist, insert the new user
        cursor.execute("INSERT INTO users (email, password) VALUES (%s, %s)", (email, password))
        mydb.commit()
        cursor.close()
        mydb.close()

        return jsonify({'message': 'Signup successful'})
    except Exception as e:
        print(f"Error handling signup request: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

# Remove the teardown_appcontext hook since we're manually managing connections now

if __name__ == "__main__":
    print("Starting Flask server...")
    app.run(debug=True)