import os
from flask import session
from openai import OpenAI
from dotenv import load_dotenv
from database.db import save_memory

# Load environment variables from .env file if it exists
load_dotenv()

# Try to get the API key from different sources
api_key = os.getenv('OPENAI_API_KEY') or os.environ.get('OPENAI_API_KEY')

if not api_key:
    raise ValueError("No OpenAI API key found. Please set the OPENAI_API_KEY environment variable.")


try:
    client = OpenAI(api_key=api_key)
except Exception as e:
    print(f"Error initializing OpenAI client: {e}")
    raise

def send_chatgpt_api(character, chat_input, memories):
    """
    Sends chat input and memories to OpenAI's API and returns the response.

    :param character: The character's data (name, personality, etc.)
    :param chat_input: The player's input message.
    :param memories: A list of memories for context in the chat.
    :return: The response from the OpenAI API.
    """
    player_id = session.get('user_id')  
    if not player_id:
        raise ValueError("No player_id found in session. Please ensure the player is logged in.")

    # System message to set the tone of the assistant
    system_message = f"You are {character['name']}, a character with the personality: {character['personality']}."

    # Combine the memories into a single context string
    memory_context = "\n".join([f"Memory {i+1}: {memory}" for i, memory in enumerate(memories)])

    # Print the data being sent to the API
    print("Sending to OpenAI API:")
    print(f"System Message: {system_message}")
    print(f"Memory Context: {memory_context}")
    print(f"User Input: {chat_input}")

    try:
        # Call to OpenAI's ChatCompletion API with the new format
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # or "gpt-4" if you're using GPT-4
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"{memory_context}\n\n{chat_input}"}
            ],
            max_tokens=150,  # Adjust based on the length of response you want
            temperature=0.7  # Adjust based on desired creativity level
        )

        # Extracting the text of the assistant's reply
        assistant_reply = response.choices[0].message.content.strip()
        
    # Now we evaluate how important this memory is
        importance_level = evaluate_memory_importance(assistant_reply, memory_context)
        
        # Check if the importance level justifies saving the memory
        if importance_level >= 3:  # Threshold for saving memory
            print("Saving this memory since it is deemed important.")
            save_memory(character['id'], player_id, assistant_reply)  # Assuming you pass character_id, player_id, etc.

        return assistant_reply

    except Exception as e:
        print(f"An error occurred while calling the OpenAI API: {e}")
        return None



def evaluate_memory_importance(assistant_reply, memory_context):
    """
    Sends the assistant reply and memory context to ChatGPT for evaluation.

    :param assistant_reply: The generated response from ChatGPT.
    :param memory_context: The previous memories for context.
    :return: An importance level (1 to 5).
    """
    evaluation_prompt = (
        f"Here's a chat interaction: {assistant_reply}\n\n"
        f"Based on the context and interaction, rate the importance of this memory for character development on a scale of 1 to 5, "
        f"where 1 is trivial and 5 is highly important."
    )

    try:
        # Call to evaluate importance level
        importance_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an assistant helping evaluate the importance of conversations for an RPG game."},
                {"role": "user", "content": evaluation_prompt}
            ],
            max_tokens=50
        )

        # Extracting the importance level
        importance_level = int(importance_response.choices[0].message.content.strip())
        print(f"Memory importance evaluated as: {importance_level}")
        return importance_level

    except Exception as e:
        print(f"An error occurred while evaluating memory importance: {e}")
        return 1  # Default to trivial if something goes wrong