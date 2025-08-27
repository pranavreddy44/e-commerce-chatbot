from groq import Groq
import os
import re
import sqlite3
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from pandas import DataFrame

load_dotenv()

GROQ_MODEL = os.getenv("GROQ_MODEL")
DEFAULT_LIMIT = int(os.getenv("DEFAULT_LIMIT", "10"))

# ✅ Resolve absolute path for db.sqlite (works in local + deployment)
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "db.sqlite"

print(f"🔗 Using SQLite DB at: {DB_PATH}")

client_sql = Groq()

sql_prompt = f"""
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
1. The SELECT clause must always be `SELECT *`.
2. **Discounts:** When a user mentions a percentage like "20 percent" or "20%", you must convert it to a decimal in the query (e.g., `discount > 0.2`).
3. **Brands:** For brand names, make the search case-insensitive and flexible. Use `LOWER(brand) LIKE '%brandname%'`.
4. **No Brand:** If the user's question does NOT mention a brand, do NOT include a brand condition in the WHERE clause.
5. Always enclose the final query in <SQL></SQL> tags.
6. Always include a LIMIT {DEFAULT_LIMIT} clause unless the question explicitly asks for ALL results.
---
Examples:

Question: show me adidas shoes under rs 3000 with a rating above 4.
<SQL>SELECT * FROM product WHERE LOWER(brand) LIKE '%adidas%' AND price < 3000 AND avg_rating > 4.0 LIMIT {DEFAULT_LIMIT};</SQL>

Question: give shoes that have rating more than 4.2 and discount more than 20 percent
<SQL>SELECT * FROM product WHERE avg_rating > 4.2 AND discount > 0.2 LIMIT {DEFAULT_LIMIT};</SQL>

Question: nike shoes
<SQL>SELECT * FROM product WHERE LOWER(brand) LIKE '%nike%' LIMIT {DEFAULT_LIMIT};</SQL>
---
Now, generate the SQL query for the user's question below.
"""

comprehension_prompt = """
You are an expert in understanding the context of the question and replying based on the data provided. 
Always reply in simple natural language, not technical terms.

When asked about products, always list them like this:
1. Product title: Rs. PRICE (X percent off), Rating: Y <link>
2. Product title: Rs. PRICE (X percent off), Rating: Y <link>
"""

def generate_sql_query(question: str) -> str:
    chat_completion = client_sql.chat.completions.create(
        messages=[
            {"role": "system", "content": sql_prompt},
            {"role": "user", "content": question},
        ],
        model=GROQ_MODEL,
        temperature=0.2,
        max_tokens=512,
    )
    return chat_completion.choices[0].message.content

def run_query(query: str):
    if query.strip().upper().startswith("SELECT"):
        try:
            with sqlite3.connect(DB_PATH) as conn:
                df = pd.read_sql_query(query, conn)
                return df
        except Exception as e:
            print(f"❌ SQL Execution Error: {e}")
            return None

def data_comprehension(question, context):
    chat_completion = client_sql.chat.completions.create(
        messages=[
            {"role": "system", "content": comprehension_prompt},
            {"role": "user", "content": f"QUESTION: {question}. DATA: {context}"},
        ],
        model=GROQ_MODEL,
        temperature=0.2,
        max_tokens=768,
    )
    return chat_completion.choices[0].message.content

def sql_chain(question: str):
    sql_query = generate_sql_query(question)
    matches = re.findall(r"<SQL>(.*?)</SQL>", sql_query, re.DOTALL)

    if not matches:
        return "❌ Sorry, LLM could not generate a SQL query."

    final_query = matches[0].strip()
    print(f"📝 Generated SQL: {final_query}")

    response = run_query(final_query)
    if response is None or response.empty:
        return "❌ Sorry, no results found."

    # Select only useful columns
    essential_columns = [
        col for col in ["title", "price", "discount", "avg_rating", "product_link"]
        if col in response.columns
    ]
    response_small = response[essential_columns].head(DEFAULT_LIMIT)
    context = response_small.to_dict(orient="records")

    return data_comprehension(question, context)

if __name__ == "__main__":
    question = "Give me top 5 nike shoes"
    print(sql_chain(question))
