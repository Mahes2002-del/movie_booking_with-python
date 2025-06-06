import streamlit as st
from pages import show_home_page, show_booking_page, show_my_bookings_page, show_about_page

st.set_page_config(page_title="Movie Booking System", page_icon="🎬", layout="wide")

# Initialize session state
if 'bookings' not in st.session_state:
    st.session_state.bookings = []

st.markdown("""
    <style>
    .stApp {
        font-size: 20px;
    }
    .stButton>button {
        font-size: 1.2rem !important;
        padding: 0.5rem 1.5rem !important;
        border-radius: 8px !important;
    }
    .stTextInput>div>input {
        font-size: 1.1rem !important;
    }
    .stSelectbox>div>div {
        font-size: 1.1rem !important;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar for navigation
page = st.sidebar.selectbox(
    "Navigation",
    ["Home", "Book Tickets", "My Bookings", "About"]
)

if page == "Home":
    show_home_page()
elif page == "Book Tickets":
    show_booking_page()
elif page == "My Bookings":
    show_my_bookings_page()
else:
    show_about_page()

if __name__ == "__main__":
    pass 

