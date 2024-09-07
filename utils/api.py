import os
from flask import session
from openai import OpenAI
from dotenv import load_dotenv
from database.db import get_db_connection, save_memory, update_disposition_points, update_name_asked
import requests

import logging


# Set logging level to suppress DEBUG messages

# Load environment variables from .env file if it exists
load_dotenv()

randommer_api_key = os.getenv('RANDOMMER_API_KEY')

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
    print("----------------------------------------------------------------------new chat------------------------------------------------------------------")
    player_id = session.get('user_id')  
    if not player_id:
        raise ValueError("No player_id found in session. Please ensure the player is logged in.")
    positive_points = character['positive_points']  # default to 0 if not found
    neutral_points = character['neutral_points'] / 3
    print(f"Because of their commonality, neutral points are weighed down:  {neutral_points}")
    negative_points = character['negative_points']
    response_tone = "normal"

    if positive_points > neutral_points and positive_points > negative_points:
        response_tone = f"You trust this person. Respond positively to them."
    elif negative_points > neutral_points and negative_points > positive_points:
        response_tone = f"You do not like this person. Respond terse with them."
    else:
        response_tone = f"You do not feel a particular way towards this person. Respond indifferently to them."

    
    # System message to set the tone of the assistant
        # System message to set the tone of the assistant


    # Combine the memories into a single context string
    memory_context = "\n".join([f"Memory {i+1}: {memory}" for i, memory in enumerate(memories)])
    
    system_message = (
       f"You are {character['name']}, a character with the personality: {character['personality_description']}. {response_tone}"
       f"These encounters are happening in a medieval tavern. You don't need to mention the tavern unless it comes up in chat."
       f"All characters speak with a medieval accent and are not overly polite. They are living their daily lives and may not be helpful."
       f"Use the following memory context to guide your response: {memory_context}"
       f"Based on the context of this interaction, determine if the user is explicitly asking for the character's name."
       f"Respond with a single word: 'Yes' if it's clear the user is asking for the name, and 'No' otherwise."
       f"Be sure to only say 'Yes' if the user explicitly asks for the name or implies it very clearly."
       f"The 'Yes' or 'No' go after the message you send back."
       f"Every response should end with a period."
    )
    # Print the data being sent to the API
    print("Sending to OpenAI API:")
    print(f"Memory Context: {memory_context}")
    print(f"User Input: {chat_input}")
    print(f"Response Tone: {response_tone}")

    try:
        # Call to OpenAI's ChatCompletion API with the new format
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # or "gpt-4" if you're using GPT-4
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"{memory_context}\n\n{chat_input}\n\nRespond with your message, followed by 'yes' if the user is asking for your name, or 'no' if they are not asking your name. If they are saying hi, they are not asking your name. Usually, they are not asking your name unless they directly ask you 'what is your name'"}
            ],
            max_tokens=500,  # Adjust based on the length of response you want
            temperature=0.6  # Adjust based on desired creativity level
        )

        # Extracting the text of the assistant's reply
        assistant_reply = response.choices[0].message.content.strip()
        message, has_name_question = parse_response(assistant_reply)

        print(f"Message: {message}")
        print(f"Asked Name: {has_name_question}")

        if has_name_question and character['name_asked'] != 'yes':
            update_name_asked(character['id'])
            handle_name_request(character['id'])
        
    # Now we evaluate how important this memory is
        importance_result = evaluate_memory_importance(chat_input, message, memory_context)
        importance_level_str, tone = importance_result
        importance_level = int(importance_level_str)
        update_disposition_points(character['id'], tone)
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
    Sends the user input, assistant reply, and memory context to ChatGPT for evaluation.

    :param user_input: The input provided by the player.
    :param assistant_reply: The generated response from GPT.
    :param memory_context: The previous memories for context.
    :return: A tuple with importance level and tone (e.g., '7', 'positive').
    """
    print(f"{assistant_reply}")
    evaluation_prompt = (
        f"Here's a chat interaction:\n\n"
        f"User Input: {user_input}\n\n"
        f"GPT Response: {assistant_reply}\n\n"
        f"Based on the context of this interaction, rate the importance of this memory for character development on a scale of 1 to 10. All names are considered important."
        f"Also, determine the tone of the interaction and return one of these three options: neutral, positive, or negative.\n"
        f"You should respond with a single number indicating the importance level, followed by a comma, then the tone as a single word (neutral, positive, or negative)."
        
    )

    try:
        # Call to evaluate importance level
        importance_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an assistant helping evaluate the importance and tone of conversations for an RPG game."},
                {"role": "user", "content": evaluation_prompt}
            ],
            max_tokens=100
        )

        # Extracting the full response (e.g., '7, positive')
        full_response = importance_response.choices[0].message.content.strip()

        # Split the response to get both the importance level and tone
        importance_level, tone = full_response.split(',')

        # Remove any extra spaces around the values
        importance_level = importance_level.strip()
        tone = tone.strip()

        print(f"Memory importance evaluated as: {importance_level}, Tone: {tone}")
        
        
        return importance_level, tone

    except Exception as e:
        print(f"An error occurred while evaluating memory importance: {e}")
        return 1, "neutral"  # Default to trivial and neutral if something goes wrong


def parse_response(response):
    # Split the response into individual sentences
    sentences = response.strip().split(". ")

    # The last sentence should contain 'Yes' or 'No'
    last_sentence = sentences[-1].strip()

    # Combine the remaining sentences back into a message
    message = ". ".join(sentences[:-1]).strip()

    return message, last_sentence


def get_random_name():
    """
    Calls the Randommer API to fetch a random name.
    :return: A string representing the randomly generated name.
    """
    try:
        url = "https://randommer.io/api/Name"
        headers = {
            'X-Api-Key': randommer_api_key,
        }
        params = {
            'nameType': 'firstname',
            'quantity': 1
        }
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            # The API returns a list of names, take the first one
            random_name = response.json()[0]
            print(f"Generated Random Name: {random_name}")
            return random_name
        else:
            print(f"Failed to fetch random name. Status Code: {response.status_code}")
            return None
    except Exception as e:
        print(f"An error occurred while fetching the random name: {e}")
        return None

def update_character_name(character_id, new_name):
    """
    Updates the character's name in the SQLite database.
    :param character_id: The ID of the character whose name will be updated.
    :param new_name: The new name to assign to the character.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('UPDATE characters SET name = ? WHERE id = ?', (new_name, character_id))
        conn.commit()
        print(f"Character ID {character_id} name updated to {new_name}.")
    except Exception as e:
        print(f"An error occurred while updating the character's name: {e}")
    finally:
        conn.close()

def handle_name_request(character_id):
    """
    Handles the logic when the player asks for the character's name.
    Calls the Randommer API and updates the database with the new name.
    :param character_id: The ID of the character whose name is being requested.
    """
    # Step 1: Fetch a random name using the Randommer API
    random_name = get_random_name()
    
    if random_name:
        # Step 2: Update the character's name in the database
        update_character_name(character_id, random_name)
        return random_name
    else:
        print("No random name was generated. Keeping the original name.")
        return None