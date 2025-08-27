import streamlit as st
from faq import ingest_faq_data, faq_chain
from sql import sql_chain
from smalltalk import talk
from pathlib import Path
from router import route_query  # Import the safer routing function

# Cache the router initialization to prevent re-initialization on every app reload
@st.cache_resource
def initialize_components():
    """Initialize FAQ data and ensure router is ready"""
    # Load FAQ data
    faqs_path = Path(__file__).parent / "resources/faq_data.csv"
    ingest_faq_data(faqs_path)
    return True

# Initialize components
initialize_components()

# Routing Function
def ask(query: str) -> str:
    """Route the query to appropriate handler"""
    try:
        route = route_query(query)  # Use the safer routing function
        
        if route == 'faq':
            return faq_chain(query)
        elif route == 'sql':
            return sql_chain(query)
        elif route == 'small-talk':
            return talk(query)
        else:
            return f"❌ Route '{route}' not implemented yet"
    
    except Exception as e:
        return f"❌ Error processing your request: {str(e)}"

# Streamlit UI
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
    with st.spinner("Thinking..."):
        response = ask(query)
    
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
