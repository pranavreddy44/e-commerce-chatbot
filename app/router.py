from semantic_router import Route
from semantic_router.routers import SemanticRouter
from semantic_router.encoders import HuggingFaceEncoder
import time

# Load encoder
print("Loading encoder...")
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

def create_router():
    """Create and initialize router with retries"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            print(f"Creating semantic router (attempt {attempt + 1}/{max_retries})...")
            
            # Create router
            router = SemanticRouter(routes=[faq, sql, small_talk], encoder=encoder)
            
            # Wait a moment for initialization
            time.sleep(1)
            
            # Test the router with multiple test queries
            test_queries = [
                ("Hello", "small-talk"),
                ("What is your return policy?", "faq"),
                ("Show me Nike shoes", "sql")
            ]
            
            all_tests_passed = True
            for test_query, expected_route in test_queries:
                try:
                    result = router(test_query)
                    if result and result.name:
                        print(f"✅ Test '{test_query}' -> '{result.name}'")
                    else:
                        print(f"⚠️  Test '{test_query}' -> No route returned")
                        all_tests_passed = False
                except Exception as e:
                    print(f"❌ Test '{test_query}' failed: {e}")
                    all_tests_passed = False
                    break
            
            if all_tests_passed:
                print("🎉 Router initialization successful!")
                return router
            else:
                print(f"❌ Router tests failed on attempt {attempt + 1}")
                if attempt < max_retries - 1:
                    print("Retrying...")
                    time.sleep(2)
                
        except Exception as e:
            print(f"❌ Router creation failed on attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                print("Retrying...")
                time.sleep(2)
    
    # If all attempts failed, return a dummy router or raise an error
    print("❌ All router initialization attempts failed!")
    raise RuntimeError("Could not initialize semantic router after multiple attempts")

# Initialize router
router = create_router()

# Wrapper function for safer routing
def route_query(query: str):
    """Safely route a query with fallback handling"""
    try:
        result = router(query)
        if result and hasattr(result, 'name'):
            return result.name
        else:
            # Fallback: simple keyword matching
            query_lower = query.lower()
            
            # FAQ keywords
            faq_keywords = ['return', 'policy', 'payment', 'delivery', 'refund', 'discount', 'warranty', 'track', 'order']
            if any(keyword in query_lower for keyword in faq_keywords):
                return 'faq'
            
            # SQL/Product keywords
            product_keywords = ['shoes', 'nike', 'adidas', 'puma', 'reebok', 'price', 'buy', 'show', 'size']
            if any(keyword in query_lower for keyword in product_keywords):
                return 'sql'
            
            # Small talk keywords
            smalltalk_keywords = ['hi', 'hello', 'how are you', 'what is your name', 'thanks', 'thank you', 'bye']
            if any(keyword in query_lower for keyword in smalltalk_keywords):
                return 'small-talk'
            
            # Default fallback
            return 'small-talk'
            
    except Exception as e:
        print(f"Routing error: {e}")
        # Fallback to keyword-based routing
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['policy', 'return', 'payment', 'delivery', 'warranty']):
            return 'faq'
        elif any(word in query_lower for word in ['shoes', 'nike', 'adidas', 'puma', 'price', 'buy']):
            return 'sql'
        else:
            return 'small-talk'

if __name__ == "__main__":
    # Test the router
    test_queries = [
        "What is your policy on defective product?",
        "Pink Puma shoes in price range 1000 to 5000",
        "How are you?"
    ]
    
    for query in test_queries:
        route = route_query(query)
        print(f"'{query}' -> {route}")
