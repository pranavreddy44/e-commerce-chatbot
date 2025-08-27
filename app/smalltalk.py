import os
from groq import Groq

groq_client = Groq()

def talk(query):
    prompt = f'''You are a helpful and friendly chatbot designed for small talk  like name, your purpose, and more.
    you are basically designed for my project flipkart chatbot give answers related to flipkart e-commerce and don't go out of box and you can take help of internet for knowing about flipkart
    QUESTION: {query}
    '''
    completion = groq_client.chat.completions.create(
        model=os.environ['GROQ_MODEL'],
        messages=[
            {
                'role': 'user',
                'content': prompt
            }
        ]
    )
    return completion.choices[0].message.content