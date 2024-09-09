from database.db import get_db_connection
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('OPENAI_API_KEY') or os.environ.get('OPENAI_API_KEY')
if not api_key:
    raise ValueError("No OpenAI API key found. Please set the OPENAI_API_KEY environment variable.")
try:
    client = OpenAI(api_key=api_key)
except Exception as e:
    print(f"Error initializing OpenAI client: {e}")
    raise

def get_character_by_id(character_id):
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute('SELECT * FROM characters WHERE id = ?', (character_id,))
    character = c.fetchone()
    
    conn.close()
    return character

def combine_and_summarize(memories):
    """
    Function to send the memories to ChatGPT for summarization.
    """
    prompt = (
        f"Here are 3 memories:\n"
        f"1. {memories[0]}\n"
        f"2. {memories[1]}\n"
        f"3. {memories[2]}\n\n"
        f"Summarize and combine them into one cohesive memory, keeping the key details."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Or another GPT model
            messages=[
                {"role": "system", "content": "You are summarizing memories for a character."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.7
        )

        summary = response.choices[0].message.content.strip()
        return summary

    except Exception as e:
        print(f"Error during memory summarization: {e}")
        return None


# Fetch all memories for a character
def get_memories(character_id, player_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT memory_log FROM memories WHERE character_id = ? AND player_id = ?', (character_id, player_id))
    # Fetch as list of dictionaries or just memory logs
    memories = [row['memory_log'] for row in c.fetchall()]
    conn.close()
    return memories


# Get the count of interactions between player and character
def get_chat_count(character_id, player_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM memories WHERE character_id = ? AND player_id = ?', (character_id, player_id))
    count = c.fetchone()[0]
    conn.close()
    return count

# Level up the character after certain interactions
def level_up_character(character_id):
    conn = get_db_connection()
    c = conn.cursor()
    # Increment character's level and award available stat points
    c.execute('UPDATE characters SET level = level + 1, available_points = available_points + 1 WHERE id = ?', (character_id,))
    conn.commit()
    conn.close()


def set_personality_description(character_id, description):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('UPDATE characters SET personality_description = ? WHERE id = ?', (description, character_id))
    conn.commit()
    conn.close()


def get_personality_description(character_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT personality_description FROM characters WHERE id = ?', (character_id,))
    description = c.fetchone()
    conn.close()
    return description[0] if description else None

def summarize_memories(character_id):
    conn = get_db_connection()
    c = conn.cursor()

    # Fetch the last 3 unsummarized memories for the character
    c.execute('''
        SELECT id, memory_log, player_id FROM memories 
        WHERE character_id = ? AND summarized = 0 
        ORDER BY timestamp ASC LIMIT 3
    ''', (character_id,))
    
    memories = c.fetchall()

    if len(memories) == 3:
        memory_logs = [mem[1] for mem in memories]
        player_id = memories[0][2]  # Fetch the player_id from one of the memories
        print(f"Memories to summarize: {memory_logs}")
        
        # Summarize the memories
        try:
            summarized_memory = combine_and_summarize(memory_logs)
            print(f"Summarized Memory: {summarized_memory}")

            # Delete the original 3 memories
            memory_ids = tuple([mem[0] for mem in memories])
            c.execute(f'DELETE FROM memories WHERE id IN {memory_ids}')

            # Insert the summarized memory
            c.execute('''
                INSERT INTO memories (character_id, player_id, memory_log, summarized, timestamp) 
                VALUES (?, ?, ?, 1, CURRENT_TIMESTAMP)
            ''', (character_id, player_id, summarized_memory))

            conn.commit()
            print("Memories summarized successfully and saved.")

        except Exception as e:
            print(f"Error while summarizing memories: {e}")
    
    conn.close()
