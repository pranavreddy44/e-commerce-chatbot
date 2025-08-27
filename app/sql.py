from groq import Groq
import os
import re
import sqlite3
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from pandas import DataFrame

# 🔹 Load env variables
load_dotenv()
GROQ_MODEL = os.getenv("GROQ_MODEL")
DEFAULT_LIMIT = int(os.getenv("DEFAULT_LIMIT", "10"))

# ✅ Resolve correct db.sqlite (using cwd for deployment reliability)
BASE_DIR = Path(os.getcwd())
DB_PATH = BASE_DIR / "db.sqlite"

# Logging after resolving DB_PATH
print(f"🔗 Resolved DB_PATH: {DB_PATH}")
if not DB_PATH.exists():
    print("⚠️ DB file not found! Path resolution failed.")
else:
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print(f"📋 Tables in DB: {tables}")
    except Exception as e:
        print(f"❌ DB inspection error: {e}")

def init_db():
    if not DB_PATH.exists():
        print("⚠️ DB file missing. Creating new one.")
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            # Create table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS product (
                    product_link TEXT,
                    title TEXT,
                    brand TEXT,
                    price INTEGER,
                    discount FLOAT,
                    avg_rating FLOAT,
                    total_ratings INTEGER
                );
            """)
            conn.commit()
            # Check if empty and insert sample data
            cursor.execute("SELECT COUNT(*) FROM product")
            if cursor.fetchone()[0] == 0:
                print("📝 DB is empty. Inserting sample data.")
                sample_data = [
                    ('https://example.com/nike1', 'Nike Air Max', 'Nike', 5000, 0.2, 4.5, 150),
                    ('https://example.com/nike2', 'Nike Running Shoe', 'Nike', 3000, 0.3, 4.2, 200),
                    ('https://example.com/adidas1', 'Adidas Ultraboost', 'Adidas', 4000, 0.1, 4.7, 100),
                    # Add more samples as needed for testing
                ]
                cursor.executemany("INSERT INTO product VALUES (?, ?, ?, ?, ?, ?, ?)", sample_data)
                conn.commit()
            print("✅ DB initialized with 'product' table.")
    except Exception as e:
        print(f"❌ DB init error: {e}")

# Call on startup
init_db()

# 🔹 Initialize Groq client
client_sql = Groq()

# ---------- SQL Prompt ----------
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
2. **Discounts:** When a user mentions a percentage like "20 percent" or "20%", convert it to decimal (e.g., `discount > 0.2`).
3. **Brands:** For brand names, make the search case-insensitive and flexible. Use `LOWER(brand) LIKE '%brandname%'`.
4. **No Brand:** If the user's question does NOT mention a brand, do NOT include brand condition in WHERE.
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

# ---------- Comprehension Prompt ----------
comprehension_prompt = """
You are an expert in understanding the context of the question and replying based on the data provided. 
Always reply in simple natural language, not technical terms.
When asked about products, always list them like this:
1. Product title: Rs. PRICE (X percent off), Rating: Y <link>
2. Product title: Rs. PRICE (X percent off), Rating: Y <link>
"""

# ---------- Functions ----------
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
                cursor = conn.cursor()
                cursor.execute("SELECT 1 FROM product LIMIT 1")  # Quick table check
                df = pd.read_sql_query(query, conn)
                return df
        except sqlite3.OperationalError as e:
            if "no such table" in str(e):
                print("❌ Table 'product' not found.")
                return None
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

# ---------- Main ----------
if __name__ == "__main__":
    question = "Give me top 5 nike shoes"
    print(sql_chain(question))
