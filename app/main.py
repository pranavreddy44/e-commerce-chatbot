import streamlit as st
from faq import ingest_faq_data, faq_chain
from sql import sql_chain
from smalltalk import talk
from pathlib import Path
from router import router

# Load FAQ data
faqs_path = Path(__file__).parent / "resources/faq_data.csv"
ingest_faq_data(faqs_path)

# Routing Function
def ask(query: str) -> str:
    route = router(query).name
    if route == 'faq':
        return faq_chain(query)
    elif route == 'sql':
        return sql_chain(query)
    elif route == 'small-talk':
        return talk(query)
    else:
        return f"❌ Route '{route}' not implemented yet"

# Streamlit UI
st.title("🛒 E-commerce Chatbot")

query = st.chat_input("Ask me anything about products, orders, or FAQs...")

# Store chat history
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Display past messages
for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

# Process new query
if query:
    # User message
    with st.chat_message("user"):
        st.markdown(query)
    st.session_state.messages.append({"role": "user", "content": query})

    # Bot response
    response = ask(query)
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
