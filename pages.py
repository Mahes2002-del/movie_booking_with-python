import streamlit as st
from datetime import datetime
from movies_data import movies
from booking_utils import save_booking, load_bookings

def show_home_page():
    st.header("Welcome to Movie Booking System")
    
    # Advanced Search and filter options
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        search_query = st.text_input("🔍 Search movies", "")
    with col2:
        genre_filter = st.selectbox(
            "🎭 Genre",
            ["All"] + sorted(list(set(movie["genre"] for movie in movies)))
        )
    with col3:
        showtime_options = sorted({show for movie in movies for show in movie["showtimes"]})
        showtime_filter = st.selectbox(
            "⏰ Showtime",
            ["All"] + showtime_options
        )
    
    # Filter movies based on search and filters
    filtered_movies = movies
    if search_query:
        filtered_movies = [m for m in filtered_movies if search_query.lower() in m["title"].lower()]
    if genre_filter != "All":
        filtered_movies = [m for m in filtered_movies if m["genre"] == genre_filter]
    if showtime_filter != "All":
        filtered_movies = [m for m in filtered_movies if showtime_filter in m["showtimes"]]
    
    # Display movies in a grid
    cols = st.columns(3)
    for idx, movie in enumerate(filtered_movies):
        with cols[idx % 3]:
            poster_url = movie.get('poster_url', None)
            if poster_url:
                st.image(poster_url, use_container_width=True)
            else:
                st.image(f"https://via.placeholder.com/300x450?text={movie['title']}", use_container_width=True)
            st.markdown(f"<h3 style='font-size: 1.5rem; margin-bottom: 0.5rem;'>{movie['title']}</h3>", unsafe_allow_html=True)
            st.markdown(f"<span style='font-size: 1.1rem;'>Genre: <b>{movie['genre']}</b></span>", unsafe_allow_html=True)
            st.markdown(f"<span style='font-size: 1.1rem;'>Duration: <b>{movie['duration']}</b></span>", unsafe_allow_html=True)
            st.markdown(f"<span style='font-size: 1.1rem;'>Rating: <b>⭐ {movie['rating']}</b></span>", unsafe_allow_html=True)
            st.markdown(f"<span style='font-size: 1.1rem;'>Price: <b>₹ {movie['price']:.2f}</b></span>", unsafe_allow_html=True)
            if st.button(f"Book Now", key=f"book_{movie['id']}"):
                st.session_state.selected_movie = movie
                st.session_state.current_page = "Book Tickets"
                st.session_state.booking_step = 1
                st.rerun()

def show_booking_page():
    st.header("Book Tickets")
    if 'selected_movie' not in st.session_state:
        st.warning("Please select a movie from the home page first.")
        return
    movie = st.session_state.selected_movie
    st.subheader(movie["title"])
    st.write(f"Genre: {movie['genre']}")
    st.write(f"Duration: {movie['duration']}")
    st.write(f"Rating: ⭐ {movie['rating']}")
    poster_url = movie.get('poster_url', None)
    if poster_url:
        st.image(poster_url, width=250)
    else:
        st.image(f"https://via.placeholder.com/300x450?text=No+Image", width=250)
        st.info("No poster available for this movie.")

    if 'booking_step' not in st.session_state:
        st.session_state.booking_step = 1
    if 'booking_data' not in st.session_state:
        st.session_state.booking_data = {}

    # Step 1: Select seats and showtime
    if st.session_state.booking_step == 1:
        showtime = st.selectbox("Showtime", movie["showtimes"])
        num_tickets = st.number_input("Number of tickets", min_value=1, max_value=10, value=1)
        
        st.write("Select your seats:")
        if 'selected_seats' not in st.session_state:
            st.session_state.selected_seats = set()
            
        seat_rows = 10
        seat_cols = 10
        booked_seats = {"1A", "2B", "3C", "4D", "5E", "6F", "7G", "8H", "9I", "10J"}
        col_labels = [chr(65+col) for col in range(seat_cols)]
        
        st.markdown('<div style="display:flex;gap:8px;margin-left:40px;">' + ''.join([f'<span style="width:40px;display:inline-block;text-align:center;font-weight:bold;">{label}</span>' for label in col_labels]) + '</div>', unsafe_allow_html=True)
        
        # Display seat grid
        for row in range(seat_rows):
            cols = st.columns(seat_cols+1)
            cols[0].markdown(f"<span style='font-weight:bold;'>{row+1}</span>", unsafe_allow_html=True)
            for col in range(seat_cols):
                seat_num = f"{row+1}{chr(65+col)}"
                is_selected = seat_num in st.session_state.selected_seats
                is_booked = seat_num in booked_seats
                
                if is_booked:
                    seat_color = "#888"
                    seat_style = f"background-color:{seat_color};color:#fff;border-radius:5px;padding:6px 10px;margin:2px;border:1px solid #444;cursor:not-allowed;opacity:0.6;"
                    cols[col+1].markdown(f"<span style='{seat_style}'>{seat_num}</span>", unsafe_allow_html=True)
                else:
                    seat_color = "#ff4b4b" if is_selected else "#e0e0e0"
                    if cols[col+1].button(f"Select {seat_num}", key=f"seat_{seat_num}"):
                        if is_selected:
                            st.session_state.selected_seats.remove(seat_num)
                        else:
                            if len(st.session_state.selected_seats) < num_tickets:
                                st.session_state.selected_seats.add(seat_num)
                        st.rerun()
                    
                    seat_style = f"background-color:{seat_color};color:#000;border-radius:5px;padding:6px 10px;margin:2px;border:1px solid #888;"
                    cols[col+1].markdown(f"<span style='{seat_style}'>{seat_num}</span>", unsafe_allow_html=True)
        
        # Confirmation form
        with st.form("booking_confirmation"):
            st.write(f"Selected seats: {', '.join(sorted(st.session_state.selected_seats))}")
            proceed_button = st.form_submit_button("Proceed to Payment")
            if proceed_button:
                if len(st.session_state.selected_seats) != num_tickets:
                    st.error(f"Please select exactly {num_tickets} seat(s).")
                else:
                    st.session_state.booking_data = {
                        'showtime': showtime,
                        'num_tickets': num_tickets,
                        'seats': list(st.session_state.selected_seats)
                    }
                    st.session_state.selected_seats = set()
                    st.session_state.booking_step = 2
                    st.rerun()

    # Step 2: Payment options
    elif st.session_state.booking_step == 2:
        with st.form("payment_form"):
            st.write("Enter your details:")
            name = st.text_input("Full Name")
            email = st.text_input("Email")
            phone = st.text_input("Phone Number")
            payment_method = st.selectbox(
                "Payment Method",
                ["Credit Card", "Debit Card", "UPI", "Net Banking", "Wallet"]
            )
            
            col1, col2 = st.columns([1, 4])
            with col1:
                back = st.form_submit_button("Back")
            with col2:
                pay = st.form_submit_button("Simulate Payment")
                
            if back:
                st.session_state.booking_step = 1
                st.rerun()
                
            if pay:
                if not all([name, email, phone]):
                    st.error("Please fill in all customer details.")
                    return
                st.session_state.booking_data['name'] = name
                st.session_state.booking_data['email'] = email
                st.session_state.booking_data['phone'] = phone
                st.session_state.booking_data['payment_method'] = payment_method
                st.session_state.booking_step = 3
                st.success("Payment simulated successfully! Booking confirmed.")
                st.rerun()

    # Step 3: Ticket confirmation (after payment)
    elif st.session_state.booking_step == 3:
        data = st.session_state.booking_data
        total_price = movie["price"] * data['num_tickets']
        booking = {
            "movie": movie["title"],
            "showtime": data['showtime'],
            "seats": data['seats'],
            "num_tickets": data['num_tickets'],
            "total_price": total_price,
            "customer": {
                "name": data['name'],
                "email": data['email'],
                "phone": data['phone']
            },
            "payment_method": data['payment_method'],
            "booking_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        save_booking(booking)
        st.success("Booking confirmed! Here is your ticket:")
        st.write(f"**Movie:** {booking['movie']}")
        st.write(f"**Showtime:** {booking['showtime']}")
        st.write(f"**Seats:** {', '.join(booking['seats'])}")
        st.write(f"**Number of tickets:** {booking['num_tickets']}")
        st.write(f"**Total price:** ₹ {booking['total_price']:.2f}")
        st.write(f"**Name:** {booking['customer']['name']}")
        st.write(f"**Email:** {booking['customer']['email']}")
        st.write(f"**Phone:** {booking['customer']['phone']}")
        st.write(f"**Payment method:** {booking['payment_method']}")
        st.balloons()
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Book Another Ticket"):
                st.session_state.booking_step = 1
                st.session_state.booking_data = {}
                st.rerun()
        with col2:
            if st.button("Go to My Bookings"):
                st.session_state.current_page = "My Bookings"
                st.session_state.booking_step = 1
                st.session_state.booking_data = {}
                st.rerun()

def show_my_bookings_page():
    st.header("My Bookings")
    
    # Load bookings
    bookings = load_bookings()
    
    if not bookings:
        st.info("You haven't made any bookings yet.")
        return
    
    # Display bookings
    for booking in bookings[::-1]:
        with st.expander(f"Booking for {booking['movie']} - {booking['showtime']}"):
            st.write(f"Date: {booking['booking_date']}")
            st.write(f"Seats: {', '.join(booking['seats'])}")
            st.write(f"Number of tickets: {booking['num_tickets']}")
            st.write(f"Total price: ₹ {booking['total_price']:.2f}")
            st.write("Customer details:")
            st.write(f"Name: {booking['customer']['name']}")
            st.write(f"Email: {booking['customer']['email']}")
            st.write(f"Phone: {booking['customer']['phone']}")
            st.write(f"Payment method: {booking['payment_method']}")

def show_about_page():
    st.header("About Movie Booking System")
    st.write("""
    Welcome to our Movie Booking System! This application allows you to:
    
    - Browse available movies
    - Book tickets for your favorite movies
    - Select your preferred seats
    - Manage your bookings
    - View booking history
    
    We strive to provide the best movie booking experience with a user-friendly interface
    and secure payment processing.
    """)
    
    st.subheader("Contact Us")
    st.write("""
    For any queries or support, please contact us at:
    - Email: support@moviebooking.com
    - Phone: (555) 123-4567
    - Address: 123 Movie Street, Cinema City
    """) 