import os
from flask import Flask, request, jsonify

# --- LangChain Imports (from your main_ai_app.py) ---
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.utilities import SQLDatabase
from sqlalchemy import create_engine
from langchain_community.agent_toolkits import create_sql_agent

# ADD this new import for creating tools
from langchain.agents import Tool
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

# --- 1. INITIALIZE THE FLASK APP ---
app = Flask(__name__)

# --- 2. SETUP THE AI AGENT (This logic is moved from your main_ai_app.py) ---
# This setup runs only once when the server starts.
print("Initializing AI Agent...")

# Set API Key from your script
os.environ["GOOGLE_API_KEY"] = "AIzaSyDd6Z1btOpnZKimkrKMT8fdHDdbA9FmmJ4"

# Initialize LLM from your script
# I've kept your model choice: gemini-2.0-flash-lite
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-lite", temperature=0)

# Connect to Database
DATABASE_FILE = "my_sample_database.db"
engine = create_engine(f"sqlite:///{DATABASE_FILE}")
db = SQLDatabase(engine)

# Create the SQL Agent
agent_executor = create_sql_agent(llm, db=db, agent_type="openai-tools", verbose=True)

print("AI Agent Initialized Successfully.")


# --- 3. DEFINE THE API ENDPOINT ---
# This replaces "PART 4" of your old script.
@app.route('/ask', methods=['POST'])
def ask_agent():
    """
    This function will be triggered when a POST request is sent to http://.../ask
    It expects a JSON body like: {"question": "How many employees?"}
    """
    # Check if the incoming request has JSON data
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    question = data.get('question')

    # Check if the 'question' key exists in the JSON
    if not question:
        return jsonify({"error": "JSON body must contain a 'question' key"}), 400

    print(f"Received question: {question}")

    try:
        # Use the agent we created at startup to process the question
        response = agent_executor.invoke({"input": question})
        answer = response.get("output")

        # Send the answer back as a JSON response
        return jsonify({"answer": answer})

    except Exception as e:
        # Handle any errors that might occur
        print(f"An error occurred: {e}")
        return jsonify({"error": "An error occurred while processing your request."}), 500

# This part allows you to run the app by typing "python app.py" in the terminal
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)