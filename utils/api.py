import openai

openai.api_key = 'your-openai-api-key'

def send_chatgpt_api(character, chat_input, memories):
    memory_context = "\n".join([memory['memory_log'] for memory in memories])
    
    prompt = f"You are {character['name']}. Here's a summary of your past interactions:\n\n{memory_context}\n\nNow the player says: '{chat_input}'. How do you respond?"

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"You are {character['name']}, a character in an RPG game."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.8,
        )
        gpt_response = response['choices'][0]['message']['content'].strip()
        return gpt_response

    except Exception as e:
        print(f"An error occurred while calling the OpenAI API: {e}")
        return "I'm having trouble responding right now, please try again later."
