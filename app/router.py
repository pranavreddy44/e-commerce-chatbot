def simple_router(query):
    """
    Simple keyword-based router that doesn't require external dependencies.
    Returns route name based on keywords in the query.
    """
    query_lower = query.lower()
    
    # FAQ keywords - policy, support, delivery, payment related
    faq_keywords = [
        'return', 'policy', 'emi', 'delivery', 'payment', 'refund', 'warranty', 
        'flipkart', 'track', 'order', 'cancel', 'modify', 'damaged', 'promo', 
        'code', 'international', 'shipping', 'installation', 'exchange', 
        'invoice', 'gift', 'card', 'counterfeit', 'schedule', 'cod', 'cash',
        'open-box', 'plus', 'bnpl', 'buy now pay later'
    ]
    
    # SQL keywords - product search, shopping related
    sql_keywords = [
        'shoes', 'nike', 'adidas', 'puma', 'reebok', 'campus', 'price', 
        'rating', 'discount', 'buy', 'purchase', 'show', 'find', 'search',
        'top', 'best', 'under', 'above', 'between', 'size', 'color', 'black',
        'white', 'red', 'blue', 'women', 'men', 'kids', 'running', 'formal',
        'sports', 'sneakers', 'boots', 'sandals', 'percent', 'rs', 'rupees'
    ]
    
    # Small talk keywords - greetings, general chat
    smalltalk_keywords = [
        'hi', 'hello', 'hey', 'how are you', 'what is your name', 'robot',
        'human', 'who made you', 'tell me about yourself', 'what can you do',
        'help', 'thanks', 'thank you', 'bye', 'goodbye', 'what are you'
    ]
    
    # Count matches for each category
    faq_score = sum(1 for keyword in faq_keywords if keyword in query_lower)
    sql_score = sum(1 for keyword in sql_keywords if keyword in query_lower)
    smalltalk_score = sum(1 for keyword in smalltalk_keywords if keyword in query_lower)
    
    # Return the category with highest score, default to small-talk
    scores = {'faq': faq_score, 'sql': sql_score, 'small-talk': smalltalk_score}
    return max(scores, key=scores.get)

# Create a router object that mimics the semantic-router interface
class SimpleRouter:
    def __init__(self):
        pass
    
    def __call__(self, query):
        route_name = simple_router(query)
        return type('Route', (), {'name': route_name})()

router = SimpleRouter()

if __name__ == "__main__":
    print(router("What is your policy on defective product?").name)
    print(router("Pink Puma shoes in price range 5000 to 1000").name)
    print(router("How are you?").name)
