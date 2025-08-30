# E-commerce Chatbot – Intelligent Shopping Assistant

![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-FF4B4B?logo=streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.8+-3776AB?logo=python&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-LLM-FF6B35?logo=groq&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_DB-FF6B35?logo=chromadb&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?logo=sqlite&logoColor=white)
![Sentence_Transformers](https://img.shields.io/badge/Sentence_Transformers-Embeddings-FF6B35?logo=sentence-transformers&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-Data_Analysis-130654?logo=pandas&logoColor=white)
![Scikit-learn](https://img.shields.io/badge/Scikit--learn-ML-F7931E?logo=scikit-learn&logoColor=white)

Live demo: https://e-commerce-chatbot-pranav.streamlit.app/

E-commerce Chatbot is an intelligent conversational AI assistant designed specifically for e-commerce platforms like Flipkart. It features a sophisticated routing system that intelligently directs user queries to specialized modules for FAQ handling, product search, and casual conversation. The chatbot leverages vector embeddings, semantic similarity, and natural language processing to provide accurate and contextual responses.

## 🏗️ Project Architecture

```
E-commerce-Chatbot/
├── app/                          # Main application directory
│   ├── main.py                   # Streamlit web interface
│   ├── router.py                 # Intelligent query routing system
│   ├── faq.py                    # FAQ handling with vector search
│   ├── sql.py                    # Product search and database queries
│   ├── smalltalk.py              # Casual conversation handling
│   └── resources/                # Data and assets
│       ├── faq_data.csv          # FAQ dataset
│       ├── ecommerce_data_final.csv
│       └── db.sqlite             # Product database
├── web_scrapping/                # Data collection and processing
│   ├── flipkart_data_extraction.ipynb
│   ├── csv_to_sqlite.py          # Database setup script
│   └── flipkart_product_data.csv # Product dataset
└── requirements.txt              # Python dependencies
```
<img width="2320" height="856" alt="image" src="https://github.com/user-attachments/assets/b9f04dfd-0aa7-4dde-91ab-e82e6ca7388c" />

## 🚀Features

### Intelligent Query Routing
- **Vector-based Routing**: Uses sentence transformers and cosine similarity for semantic query classification
- **Fallback System**: Keyword-based routing when vector embeddings fail
- **Multi-modal Support**: Handles FAQ, product search, and casual conversation queries

### FAQ Management System
- **Vector Search**: ChromaDB with sentence transformers for semantic FAQ matching
- **Context-aware Responses**: Groq LLM generates contextual answers based on retrieved FAQ data
- **Comprehensive Coverage**: 25+ FAQ categories including returns, payments, delivery, and policies

### Product Search & Recommendations
- **Natural Language Queries**: Convert user questions to SQL queries using Groq LLM
- **Advanced Filtering**: Support for price ranges, ratings, discounts, brands, and categories
- **Structured Responses**: Formatted product listings with links, prices, and ratings
- **Database Integration**: SQLite database with 1000+ product entries

### Casual Conversation
- **Friendly Interface**: Natural small talk capabilities
- **E-commerce Context**: Responses tailored to Flipkart and shopping context
- **Personality**: Helpful and informative chatbot personality

## 🛠️ Tech Stack

### Core Technologies
- **Frontend**: Streamlit 1.28+ (Web interface)
- **Backend**: Python 3.8+ (Application logic)
- **AI/LLM**: Groq API (Natural language processing)
- **Vector Database**: ChromaDB (Semantic search)
- **Database**: SQLite (Product data storage)
- **Embeddings**: Sentence Transformers (all-MiniLM-L6-v2)

### Key Libraries
- **Data Processing**: Pandas, NumPy
- **Machine Learning**: Scikit-learn (Cosine similarity)
- **NLP**: Transformers, Sentence Transformers
- **Database**: PySQLite3
- **Environment**: Python-dotenv

## 📊 Data Schema

### Product Database Schema
```sql
CREATE TABLE product (
    product_link TEXT,      -- Product URL
    title TEXT,            -- Product name
    brand TEXT,            -- Brand name
    price INTEGER,         -- Price in INR
    discount FLOAT,        -- Discount percentage (0.0-1.0)
    avg_rating FLOAT,      -- Average rating (0-5)
    total_ratings INTEGER  -- Number of ratings
);
```
## 🔄 Query Routing Logic

### Vector Router
1. **Embedding Generation**: Converts user query to vector using sentence transformers
2. **Similarity Calculation**: Computes cosine similarity with pre-defined utterance embeddings
3. **Route Selection**: Routes to FAQ, SQL, or small-talk based on highest similarity score
4. **Threshold Check**: Falls back to small-talk if similarity is below threshold (0.3)

## 📈 Performance Features
- **Semantic Understanding**: Vector embeddings for context-aware routing
- **Fast Response**: Optimized database queries with result limiting
- **Scalable Architecture**: Modular design for easy feature additions
- **Error Handling**: Graceful fallbacks for failed operations
- **Memory Efficient**: Pre-computed embeddings and optimized data structures

## 🙏 Acknowledgements

- **Groq** for fast LLM inference
- **ChromaDB** for vector database capabilities
- **Sentence Transformers** for semantic embeddings
- **Streamlit** for the web interface framework
- **Flipkart** for the e-commerce context and data inspiration
