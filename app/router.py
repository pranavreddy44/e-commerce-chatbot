from semantic_router import Route, Router
from semantic_router.encoders import HuggingFaceEncoder

encoder = HuggingFaceEncoder(
    name="sentence-transformers/all-MiniLM-L6-v2"
)

faq = Route(
    name='faq',
    utterances=[
        "What is the return policy of the products?",
        "Do I get discount with the HDFC credit card?",
        "How can I track my order?",
        "What payment methods are accepted?",
        "How long does it take to process a refund?",
        # Added broader Flipkart-style FAQs
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
        # Added diverse ecommerce product queries
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
    ]
)

# created a the route for small talk and added it in the routee layer
small_talk = Route(
    name='small-talk',
    utterances=[
        "How are you?",
        "What is your name?",
        "Are you a robot?",
        "What are you?",
        "What do you do?",
        # Added common chit-chat variations
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

router = Router(routes=[faq, sql, small_talk], encoder=encoder)

if __name__ == "__main__":
    print(router("What is your policy on defective product?").name)
    print(router("Pink Puma shoes in price range 5000 to 1000").name)
    print(router("How are you?").name)
