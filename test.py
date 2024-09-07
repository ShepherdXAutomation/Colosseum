import os
from dotenv import load_dotenv
import openai

# Load environment variables from the .env file
load_dotenv()

# Access the API key using os.environ
openai_api_key = os.getenv('OPENAI_API_KEY')

# Now you can use the API key in your OpenAI calls
openai.api_key = openai_api_key
