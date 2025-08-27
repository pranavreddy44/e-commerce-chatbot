try:
    from semantic_router import Route
    from semantic_router.routers import SemanticRouter
    from semantic_router.encoders import HuggingFaceEncoder
    
    # Load encoder
    encoder = HuggingFaceEncoder(
        name="sentence-transformers/all-MiniLM-L6-v2"
    )
    
    # FAQ Route
    faq = Route(
        name='faq',
        utterances=[
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
    )
    
    # SQL/Product Query Route
    sql = Route(
        name='sql',
        utterances=[
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
    )
    
    # Small Talk Route
    small_talk = Route(
        name='small-talk',
        utterances=[
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
    )
    
    # Router
    router = SemanticRouter(routes=[faq, sql, small_talk], encoder=encoder)
    
except ImportError:
    # Fallback to simple keyword-based router if semantic-router fails
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
    print("FAQ →", router("What is your policy on defective product?").name)
    print("SQL →", router("Pink Puma shoes in price range 1000 to 5000").name)
    print("Small Talk →", router("How are you?").name)
