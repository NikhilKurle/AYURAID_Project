Flask Chatbot Project

This project implements a chatbot using Flask, scikit-learn, and OpenAI.

Prerequisites:

- Python 3.x
- pip
- MySQL database (optional)

Installation:


1. Create a virtual environment (optional but recommended):

   On Windows:
   python -m venv venv
   venv\Scripts\activate
   
   On macOS/Linux:
   python3 -m venv venv
   source venv/bin/activate

2. Install the required dependencies:

   pip install -r requirements.txt

Usage:

1. Set up your MySQL database (if needed) and adjust the database configuration in app.py accordingly.

2. Ensure your CSV files (Formulation-Indications.csv and ayurvedic_symptoms_desc.csv) are in the project directory.

3. Run the Flask application:

   python ayurvedic_formulation.py


4. The application will start running on http://localhost:5000/ go to your front end and perform whatever operations you want.

Endpoints:

- /chat: For interacting with the chatbot.
- /formulations: For getting formulations based on symptoms.
- /login: For user login.
- /signup: For user signup.

License:

This project is licensed under the MIT License - see the LICENSE file for details.
