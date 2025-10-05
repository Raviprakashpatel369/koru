import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import AIMessage, HumanMessage # Needed for tool calling agent type
from langchain_core.messages import HumanMessage # Needed for simpler chat interaction

# --- Initialize your Google Gemini LLM ---
# IMPORTANT: Replace 'YOUR_ACTUAL_GOOGLE_API_KEY_HERE' with your real API key.
# This directly sets the API key for your session.
os.environ["GOOGLE_API_KEY"] = "AIzaSyDd6Z1btOpnZKimkrKMT8fdHDdbA9FmmJ4"

print("Initializing Gemini LLM for test...")
# Using a slightly different model type here for simpler chat-like interaction
# gemini-pro is good for general text.
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-lite", temperature=0.7) # Temperature can be higher for creative text
print("LLM initialized.")

# --- Make a simple call to the LLM ---
print("\nSending a test prompt to the LLM...")
user_query = "what is 1 divided by two and the result by 7"

# The 'invoke' method sends the message to the LLM
response = llm.invoke(user_query)

print("\n--- LLM Response ---")
# The response object contains the generated content
print(response.content)
print("--------------------")

# You can also try with a list of messages for a chat-like interaction:
# messages = [
#     HumanMessage(content="Hello!"),
#     AIMessage(content="Hello! How can I help you today?"),
#     HumanMessage(content="What is the capital of France?"),
# ]
# chat_response = llm.invoke(messages)
# print("\n--- LLM Chat Response ---")
# print(chat_response.content)
# print("-------------------------")