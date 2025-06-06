import json
import os

def save_booking(booking):
    """Save booking to a JSON file"""
    bookings = []
    if os.path.exists('bookings.json'):
        with open('bookings.json', 'r') as f:
            bookings = json.load(f)
    
    bookings.append(booking)
    
    with open('bookings.json', 'w') as f:
        json.dump(bookings, f, indent=4)

def load_bookings():
    """Load bookings from JSON file"""
    if os.path.exists('bookings.json'):
        with open('bookings.json', 'r') as f:
            return json.load(f)
    return [] 