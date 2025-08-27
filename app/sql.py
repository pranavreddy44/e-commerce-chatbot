from groq import Groq
import os
import re
import sqlite3
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from pandas import DataFrame

load_dotenv()

GROQ_MODEL = os.getenv('GROQ_MODEL')
# Limit rows sent to LLM to keep requests small
DEFAULT_LIMIT = int(os.getenv('DEFAULT_LIMIT', '10'))

db_path = Path(__file__).parent / "db.sqlite"

client_sql = Groq()

sql_prompt = """
You are an expert SQL analyst. Your task is to generate a single, valid SQL query based on a user's question about products.

<schema> 
table: product 

fields: 
product_link - string (hyperlink to product)
title - string (name of the product)
brand - string (brand of the product)
price - integer (price of the product in Indian Rupees)
discount - float (discount on the product. 10 percent discount is represented as 0.1, 20 percent as 0.2, and such.)
avg_rating - float (average rating of the product. Range 0-5, 5 is the highest.)
total_ratings - integer (total number of ratings for the product)
</schema>

---
Here are the rules you MUST follow:
1.  The SELECT clause must always be `SELECT *`.
2.  **Discounts:** When a user mentions a percentage like "20 percent" or "20%", you must convert it to a decimal in the query (e.g., `discount > 0.2`).
3.  **Brands:** For brand names, make the search case-insensitive and flexible. Use `LOWER(brand) LIKE '%brandname%'` (e.g., `LOWER(brand) LIKE '%nike%'`).
4.  **No Brand:** If the user's question does NOT mention a brand (e.g., "show me shoes"), do NOT include a brand condition in the WHERE clause.
5.  Always enclose the final query in `<SQL></SQL>` tags.
6.  Prefer including a LIMIT clause (e.g., LIMIT {DEFAULT_LIMIT}) to keep results concise.

---
Here are some examples:

Question: show me adidas shoes under rs 3000 with a rating above 4.
<SQL>SELECT * FROM product WHERE LOWER(brand) LIKE '%adidas%' AND price < 3000 AND avg_rating > 4.0;</SQL>

Question: give shoes that have rating more than 4.2 and discount more than 20 percent
<SQL>SELECT * FROM product WHERE avg_rating > 4.2 AND discount > 0.2;</SQL>

Question: nike shoes
<SQL>SELECT * FROM product WHERE LOWER(brand) LIKE '%nike%';</SQL>
---
Now, generate the SQL query for the user's question below.  
""".format(DEFAULT_LIMIT=DEFAULT_LIMIT)



comprehension_prompt = """You are an expert in understanding the context of the question and replying based on the data pertaining to the question provided. You will be provided with Question: and Data:. The data will be in the form of an array or a dataframe or dict. Reply based on only the data provided as Data for answering the question asked as Question. Do not write anything like 'Based on the data' or any other technical words. Just a plain simple natural language response.
The Data would always be in context to the question asked. For example is the question is “What is the average rating?” and data is “4.3”, then answer should be “The average rating for the product is 4.3”. So make sure the response is curated with the question and data. Make sure to note the column names to have some context, if needed, for your response.
There can also be cases where you are given an entire dataframe in the Data: field. Always remember that the data field contains the answer of the question asked. All you need to do is to always reply in the following format when asked about a product: 
Produt title, price in indian rupees, discount, and rating, and then product link. Take care that all the products are listed in list format, one line after the other. Not as a paragraph.
For example:
1. Campus Women Running Shoes: Rs. 1104 (35 percent off), Rating: 4.4 <link>
2. Campus Women Running Shoes: Rs. 1104 (35 percent off), Rating: 4.4 <link>
3. Campus Women Running Shoes: Rs. 1104 (35 percent off), Rating: 4.4 <link>

"""


def generate_sql_query(question):
    chat_completion = client_sql.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": sql_prompt,
            },
            {
                "role": "user",
                "content": question,
            }
        ],
        model=os.environ['GROQ_MODEL'],
        temperature=0.2,
        max_tokens=512
    )

    return chat_completion.choices[0].message.content



def run_query(query):
    if query.strip().upper().startswith('SELECT'):
        with sqlite3.connect(db_path) as conn:
            df = pd.read_sql_query(query, conn)
            return df


def data_comprehension(question, context):
    chat_completion = client_sql.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": comprehension_prompt,
            },
            {
                "role": "user",
                "content": f"QUESTION: {question}. DATA: {context}",
            }
        ],
        model=os.environ['GROQ_MODEL'],
        temperature=0.2,
        max_tokens=768
    )

    return chat_completion.choices[0].message.content



def sql_chain(question):
    sql_query = generate_sql_query(question)
    pattern = "<SQL>(.*?)</SQL>"
    matches = re.findall(pattern, sql_query, re.DOTALL)

    if len(matches) == 0:
        return "Sorry, LLM is not able to generate a query for your question"

    print(matches[0].strip())

    response = run_query(matches[0].strip())
    if response is None:
        return "Sorry, there was a problem executing SQL query"

    # Reduce payload: select essential columns and cap rows
    essential_columns = [
        col for col in ["title", "price", "discount", "avg_rating", "product_link"]
        if col in response.columns
    ]
    if essential_columns:
        response_small = response[essential_columns]
    else:
        response_small = response
    response_small = response_small.head(DEFAULT_LIMIT)

    context = response_small.to_dict(orient='records')

    answer = data_comprehension(question, context)
    return answer


if __name__ == "__main__":
    # question = "All shoes with rating higher than 4.5 and total number of reviews greater than 500"
    # sql_query = generate_sql_query(question)
    # print(sql_query)
    question = "Show top 3 shoes in descending order of rating"
    # question = "Show me 3 running shoes for woman"
    # question = "sfsdfsddsfsf"
    answer = sql_chain(question)
    print(answer)
