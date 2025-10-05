import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.utilities import SQLDatabase # Corrected import path
from langchain_community.agent_toolkits import create_sql_agent
from sqlalchemy import create_engine # Needed for database connection

# --- PART 1: Initialize your Google Gemini LLM ---
# IMPORTANT: Replace 'YOUR_ACTUAL_GOOGLE_API_KEY_HERE' with your real API key.
# This directly sets the API key for your session.
os.environ["GOOGLE_API_KEY"] = "AIzaSyDd6Z1btOpnZKimkrKMT8fdHDdbA9FmmJ4"

# Initialize the Gemini LLM. 'gemini-pro' is a good general-purpose model.
# temperature=0 makes the LLM's responses more deterministic, which is good for SQL generation.
print("Initializing Gemini LLM...")
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-lite", temperature=0)
print("LLM initialized.")

# --- PART 2: Connect LangChain to your SQL Database ---
# This should match the name of the .db file you just created
DATABASE_FILE = "my_sample_database.db"

print(f"Connecting to database: {DATABASE_FILE}...")
try:
    # SQLAlchemy is used by LangChain to interact with the database.
    # 'sqlite:///' indicates a local SQLite file database.
    engine = create_engine(f"sqlite:///{DATABASE_FILE}")

    # LangChain's SQLDatabase utility wraps the SQLAlchemy engine.
    db = SQLDatabase(engine)
    print("Database connected successfully.")

    # Let's verify by printing the table names LangChain found.
    print("\n--- Database Tables Identified by LangChain ---")
    print(db.get_table_names())
    print("-------------------------------------------\n")

except Exception as e:
    print(f"Error connecting to database: {e}")
    print(f"Please ensure '{DATABASE_FILE}' exists in the same directory as 'main_ai_app.py'.")

# The 'llm' and 'db' objects are now ready for the next steps!

# --- PART 3: Create the SQL Agent ---
print("\nCreating the SQL Agent...")
# 'verbose=True' is essential for seeing the agent's thought process.
agent_executor = create_sql_agent(llm, db=db, agent_type="openai-tools", verbose=True)
print("SQL Agent created. Ready to answer questions!")

# --- PART 4: Ask a question! ---
question = "How many employees are there in the sales department?"
print(f"\nAsking the agent: '{question}'")

# Invoke the agent to get the answer
response = agent_executor.invoke({"input": question})

# Print just the final answer
print("\n--- Agent's Final Answer ---")
print(response["output"])
print("---------------------------\n")