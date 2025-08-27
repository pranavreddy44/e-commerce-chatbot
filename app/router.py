import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Load the embedding model
try:
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    print("Sentence transformer model loaded successfully")
except Exception as e:
    print(f"Failed to load sentence transformer: {e}")
    model = None

# Define route utterances
faq_utterances = [
    "What is the return policy of the products?",
    "Do I get discount with the HDFC credit card?",
    "How can I track my order?",
    "What payment methods are accepted?",
    "How long does it take to process a refund?",
    "What are the delivery charges?",
    "When will my order be delivered?",
    "Do you offer no-cost EMI?",
    "Is installation available for appliances?",
    "Can I exchange a product if the size is wrong?",
    "How do I claim warranty for a product?",
    "What is Flipkart Plus?",
    "Do you have Buy Now Pay Later?",
    "How can I download my invoice?",
    "Are gift cards available?",
    "How do I report a damaged or counterfeit product?",
    "Is Cash on Delivery available at my pincode?",
    "Do you provide open-box delivery?",
    "Do you ship internationally?",
    "How do I apply a promo code?",
    "What is your policy on defective product?",
]

sql_utterances = [
    "I want to buy nike shoes that have 50% discount.",
    "Are there any shoes under Rs. 3000?",
    "Do you have formal shoes in size 9?",
    "Are there any Puma shoes on sale?",
    "What is the price of puma running shoes?",
    "Show me adidas sneakers below 2500 with rating above 4.",
    "Top 5 nike running shoes by rating",
    "Shoes with discount more than 30 percent",
    "Women's running shoes under 2000",
    "Black formal shoes size 8",
    "Sort sports shoes by highest rating",
    "Bestselling shoes with more than 500 ratings",
    "Reebok shoes between 2000 and 4000",
    "Kids shoes with rating over 4.2",
    "Show 3 Puma shoes with highest discount",
    "Pink Puma shoes in price range 1000 to 5000",
]

smalltalk_utterances = [
    "How are you?",
    "What is your name?",
    "Are you a robot?",
    "What are you?",
    "What do you do?",
    "Hi",
    "Hello",
    "Hey there",
    "Who made you?",
    "Tell me about yourself",
    "What can you do?",
    "Can you help me?",
    "Thanks",
    "Thank you",
    "Bye",
    "Goodbye",
    "Are you human?",
]

# Pre-compute embeddings for all utterances
def get_embeddings():
    if model is None:
        return None, None, None
    
    try:
        faq_embeddings = model.encode(faq_utterances)
        sql_embeddings = model.encode(sql_utterances)
        smalltalk_embeddings = model.encode(smalltalk_utterances)
        return faq_embeddings, sql_embeddings, smalltalk_embeddings
    except Exception as e:
        print(f"Failed to compute embeddings: {e}")
        return None, None, None

# Initialize embeddings
faq_embeddings, sql_embeddings, smalltalk_embeddings = get_embeddings()

def vector_router(query, threshold=0.3):
    """
    Vector-based router using sentence transformers and cosine similarity.
    Returns route name based on semantic similarity to pre-defined utterances.
    """
    if model is None or faq_embeddings is None:
        # Fallback to keyword-based routing
        return keyword_router(query)
    
    try:
        # Encode the query
        query_embedding = model.encode([query])
        
        # Calculate similarities with each route
        faq_similarities = cosine_similarity(query_embedding, faq_embeddings).flatten()
        sql_similarities = cosine_similarity(query_embedding, sql_embeddings).flatten()
        smalltalk_similarities = cosine_similarity(query_embedding, smalltalk_embeddings).flatten()
        
        # Get max similarity for each route
        max_faq_sim = np.max(faq_similarities)
        max_sql_sim = np.max(sql_similarities)
        max_smalltalk_sim = np.max(smalltalk_similarities)
        
        # Find the route with highest similarity above threshold
        similarities = {
            'faq': max_faq_sim,
            'sql': max_sql_sim,
            'small-talk': max_smalltalk_sim
        }
        
        best_route = max(similarities, key=similarities.get)
        best_score = similarities[best_route]
        
        # If best score is below threshold, default to small-talk
        if best_score < threshold:
            return 'small-talk'
        
        return best_route
        
    except Exception as e:
        print(f"Vector routing failed: {e}")
        return keyword_router(query)

def keyword_router(query):
    """
    Simple keyword-based router as fallback.
    """
    query_lower = query.lower()
    
    # FAQ keywords
    faq_keywords = [
        'return', 'policy', 'emi', 'delivery', 'payment', 'refund', 'warranty', 
        'flipkart', 'track', 'order', 'cancel', 'modify', 'damaged', 'promo', 
        'code', 'international', 'shipping', 'installation', 'exchange', 
        'invoice', 'gift', 'card', 'counterfeit', 'schedule', 'cod', 'cash',
        'open-box', 'plus', 'bnpl', 'buy now pay later'
    ]
    
    # SQL keywords
    sql_keywords = [
        'shoes', 'nike', 'adidas', 'puma', 'reebok', 'campus', 'price', 
        'rating', 'discount', 'buy', 'purchase', 'show', 'find', 'search',
        'top', 'best', 'under', 'above', 'between', 'size', 'color', 'black',
        'white', 'red', 'blue', 'women', 'men', 'kids', 'running', 'formal',
        'sports', 'sneakers', 'boots', 'sandals', 'percent', 'rs', 'rupees'
    ]
    
    # Count matches
    faq_score = sum(1 for keyword in faq_keywords if keyword in query_lower)
    sql_score = sum(1 for keyword in sql_keywords if keyword in query_lower)
    
    if faq_score > sql_score and faq_score > 0:
        return 'faq'
    elif sql_score > 0:
        return 'sql'
    else:
        return 'small-talk'

# Create router object with the same interface
class CustomRouter:
    def __init__(self):
        self.use_vector = model is not None and faq_embeddings is not None
    
    def __call__(self, query):
        if self.use_vector:
            route_name = vector_router(query)
        else:
            route_name = keyword_router(query)
        return type('Route', (), {'name': route_name})()

router = CustomRouter()

if __name__ == "__main__":
    print("FAQ →", router("What is your policy on defective product?").name)
    print("SQL →", router("Pink Puma shoes in price range 1000 to 5000").name)
    print("Small Talk →", router("How are you?").name)
