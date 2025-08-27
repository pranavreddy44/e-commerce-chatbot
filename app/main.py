import streamlit as st
from faq import ingest_faq_data, faq_chain
from sql import sql_chain
from smalltalk import talk
from pathlib import Path
from router import route_query

# Cache the FAQ data initialization
@st.cache_resource
def initialize_components():
    """Initialize FAQ data"""
    try:
        faqs_path = Path(__file__).parent / "resources/faq_data.csv"
        ingest_faq_data(faqs_path)
        print("✅ FAQ data loaded successfully")
        return True
    except Exception as e:
        print(f"❌ Error loading FAQ data: {e}")
        return False

# Initialize components
components_ready = initialize_components()

# Routing Function
def ask(query: str) -> str:
    """Route the query to appropriate handler"""
    if not components_ready:
        return "❌ System is still initializing. Please wait a moment and try again."
    
    if not query or not query.strip():
        return "Please ask me something! I can help with product searches, FAQs, or just chat."
    
    try:
        route = route_query(query.strip())
        
        if route == 'faq':
            return faq_chain(query)
        elif route == 'sql':
            return sql_chain(query)
        elif route == 'small-talk':
            return talk(query)
        else:
            return f"I'm not sure how to handle that type of query yet. Could you try rephrasing?"
    
    except Exception as e:
        print(f"Error in ask function: {e}")
        return "❌ Sorry, I encountered an error processing your request. Please try again."

# Streamlit UI
st.set_page_config(
    page_title="E-commerce Chatbot",
    page_icon="🛒",
    layout="centered"
)

st.title("🛒 E-commerce Chatbot")
st.write("Ask me anything about products, orders, or just chat!")

# Store chat history
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Display past messages
for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

# Process new query
query = st.chat_input("Ask me anything about products, orders, or FAQs...")

if query:
    # User message
    with st.chat_message("user"):
        st.markdown(query)
    st.session_state.messages.append({"role": "user", "content": query})
    
    # Bot response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = ask(query)
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})

# Sidebar with info
with st.sidebar:
    st.header("ℹ️ About")
    st.write("This chatbot can help you with:")
    st.write("• Product searches and recommendations")
    st.write("• Frequently asked questions")
    st.write("• General conversation")
    
    if not components_ready:
        st.warning("⚠️ Some features may be limited while the system initializes.")
    else:
        st.success("✅ All systems ready!")
