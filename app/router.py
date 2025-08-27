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

# Initialize the router index - THIS IS THE KEY FIX
print("Initializing semantic router...")
router.fit()
print("Semantic router initialized successfully!")

if __name__ == "__main__":
    print("FAQ →", router("What is your policy on defective product?").name)
    print("SQL →", router("Pink Puma shoes in price range 1000 to 5000").name)
    print("Small Talk →", router("How are you?").name)
