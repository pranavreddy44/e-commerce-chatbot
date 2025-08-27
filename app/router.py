"""
Simple and robust router with keyword-based fallback
This version prioritizes reliability over semantic routing
"""
# Global variables
semantic_router = None
use_semantic = False

def create_router():
    global semantic_router, use_semantic
    for attempt in range(3):
        print(f"Creating semantic router (attempt {attempt+1}/3)...")
        try:
            from semantic_router import Route
            from semantic_router.routers import SemanticRouter
            from semantic_router.encoders import HuggingFaceEncoder
            from semantic_router.indexes.local import LocalIndex  # Explicit import

            print("Loading encoder...")
            encoder = HuggingFaceEncoder(name="sentence-transformers/all-MiniLM-L6-v2")

            # Define routes
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
            
            index = LocalIndex()  # Explicitly create index
            router = SemanticRouter(routes=[faq, sql, small_talk], encoder=encoder, index=index)

            # Test with delay to allow index readiness
            import time
            time.sleep(2)  # Give index time to settle
            result = router("Hello")
            if result and hasattr(result, 'name'):
                print(f"✅ Semantic router test passed on attempt {attempt+1}")
                semantic_router = router
                use_semantic = True
                return router
            else:
                print(f"❌ Test 'Hello' failed: Index may not be ready.")
        except Exception as e:
            print(f"❌ Initialization failed on attempt {attempt+1}: {e}")
        time.sleep(1)  # Retry delay

    print("⚠️ Semantic router failed all attempts. Falling back to keyword routing.")
    return None  # No raise; just return None

# Initialize (call this once)
create_router()

def keyword_based_routing(query: str) -> str:
    """Fallback keyword-based routing that always works"""
    query_lower = query.lower().strip()
    
    # FAQ keywords - these trigger FAQ responses
    faq_keywords = [
        'return', 'policy', 'payment', 'delivery', 'refund', 'discount', 
        'warranty', 'track', 'order', 'emi', 'installation', 'exchange',
        'flipkart', 'plus', 'invoice', 'gift', 'card', 'damaged', 'counterfeit',
        'cash', 'cod', 'delivery', 'pincode', 'open-box', 'international',
        'promo', 'code', 'defective', 'hdfc', 'credit'
    ]
    
    # Product/SQL keywords - these trigger product searches
    product_keywords = [
        'shoes', 'nike', 'adidas', 'puma', 'reebok', 'price', 'buy', 'show',
        'size', 'formal', 'running', 'sneakers', 'rating', 'sale', 'women',
        'men', 'kids', 'black', 'white', 'pink', 'sports', 'bestselling',
        'discount', 'under', 'below', 'above', 'between', 'top', 'sort'
    ]
    
    # Small talk keywords
    smalltalk_keywords = [
        'hi', 'hello', 'hey', 'how are you', 'what is your name', 'name',
        'robot', 'what are you', 'what do you do', 'who made you',
        'tell me about yourself', 'what can you do', 'can you help',
        'thanks', 'thank you', 'bye', 'goodbye', 'human'
    ]
    
    # Check for product/SQL keywords first (more specific)
    if any(keyword in query_lower for keyword in product_keywords):
        return 'sql'
    
    # Check for FAQ keywords
    if any(keyword in query_lower for keyword in faq_keywords):
        return 'faq'
    
    # Check for small talk keywords
    if any(keyword in query_lower for keyword in smalltalk_keywords):
        return 'small-talk'
    
    # Default: if query contains numbers or brands, likely product search
    if any(char.isdigit() for char in query) or any(brand in query_lower for brand in ['nike', 'adidas', 'puma', 'reebok']):
        return 'sql'
    
    # Otherwise, small talk
    return 'small-talk'

def route_query(query: str) -> str:
    """Main routing function with semantic router and keyword fallback"""
    if use_semantic and semantic_router:
        try:
            result = semantic_router(query)
            if result and hasattr(result, 'name'):
                print(f"🔄 Semantic route: {result.name}")
                return result.name
        except Exception as e:
            print(f"⚠️ Semantic routing error: {e}. Using keyword fallback.")
    route = keyword_based_routing(query)
    print(f"🔍 Keyword route: {route}")
    return route

print("✅ Router module ready!")

# Test function
if __name__ == "__main__":
    test_queries = [
        "What is your policy on defective product?",
        "Pink Puma shoes in price range 1000 to 5000", 
        "How are you?",
        "Hi there!",
        "Show me Nike shoes under 3000"
    ]
    
    print("\n🧪 Testing router:")
    for query in test_queries:
        route = route_query(query)
        print(f"'{query}' -> {route}")
