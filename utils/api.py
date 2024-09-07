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
    positive_points = character.get('positive_points', 0)  # default to 0 if not found
    neutral_points = character.get('neutral_points', 0)
    negative_points = character.get('negative_points', 0)
    response_tone = "normal"

    if positive_points > neutral_points and positive_points > negative_points:
        response_tone = f"You trust this person. Respond positively to them."
    elif negative_points > neutral_points and negative_points > positive_points:
        response_tone = f"You do not like this person. Respond terse with them."
    else:
        response_tone = f"You do not feel a particular way towards this person. Respond indifferently to them."

    
    # System message to set the tone of the assistant
    system_message = f"You are {character['name']}, a character with the personality: {character['personality_description']}. {response_tone} These encounters are occuring at a medieval tavern. You don't have to the tavern, unless it comes up in chat. All characters speak in a medieval accent. They are not helpful assistants. Just normal people you would meet in medieval times. They are not trying to be overly helpful to the user. No need to be overly polite. Just living their daily lives. Try to make the responses consice and short unless they are important."

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
            temperature=0.8  # Adjust based on desired creativity level
        )

        # Extracting the text of the assistant's reply
        assistant_reply = response.choices[0].message.content.strip()
        
    # Now we evaluate how important this memory is
        importance_level = evaluate_memory_importance(chat_input, assistant_reply, memory_context)
        
        # Check if the importance level justifies saving the memory
        if importance_level >= 5:  # Threshold for saving memory
            print("Saving this memory since it is deemed important.")
            save_memory(character['id'], player_id, assistant_reply)  # Assuming you pass character_id, player_id, etc.

        return assistant_reply

    except Exception as e:
        print(f"An error occurred while calling the OpenAI API: {e}")
        return None



def evaluate_memory_importance(user_input, assistant_reply, memory_context):
    """
    Sends the assistant reply and memory context to ChatGPT for evaluation.

    :param assistant_reply: The generated response from ChatGPT.
    :param memory_context: The previous memories for context.
    :return: An importance level (1 to 5).
    """
    evaluation_prompt = (
        f"Here's a chat interaction:\n\n"
        f"User Input: {user_input}\n\n"
        f"GPT Response: {assistant_reply}\n\n"
        f"Based on the context of this interaction, rate the importance of this memory for character development on a scale of 1 to 10. "
        f"Based on the context of this interaction, determine the disposition of the interaction and return one of these three options neutral, positive or negative."
        f"where 1 is trivial and 10 is highly important."
        f"Names are always important."
        f"You respond with only a number followed by a comma then the disposition as a single word."
        
        
    )

    try:
        # Call to evaluate importance level
        importance_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an assistant helping evaluate the importance of conversations for an RPG game. Only respond with a single number followed by a comma dn then the disposition as a single word."} 
            ],
            max_tokens=100
        )

        # Extracting the importance level
        importance_level = int(importance_response.choices[0].message.content.strip())
        print(f"Memory importance evaluated as: {importance_level}")
        return importance_level

    except Exception as e:
        print(f"An error occurred while evaluating memory importance: {e}")
        return 1  # Default to trivial if something goes wrong