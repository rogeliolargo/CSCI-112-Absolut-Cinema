"""
MongoDB connection helper for Absolut Cinema.

This module connects to MongoDB Atlas and provides a `db` object for querying collections.
Django's SQL database remains untouched for auth/sessions.

Usage:
    from booking.mongo_db import db
    movies = list(db.movies.find())
"""

import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get MongoDB URI and database name from .env
MONGO_URI = os.getenv('MONGODB_URI') or os.getenv('MONGO_URI')
MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', 'absolut_cinema_db')

if not MONGO_URI:
    raise RuntimeError(
        "MONGODB_URI not set in .env. "
        "Add: MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/"
    )

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]

# Collection references
movies = db.movies
showtimes = db.showtimes
seats = db.seats
reservations = db.reservations
bookings = db.bookings


def test_mongo_connection():
    """Test MongoDB connection."""
    try:
        client.admin.command('ping')
        print('✓ Connected to MongoDB Atlas')
        return True
    except Exception as e:
        print(f'✗ MongoDB connection failed: {e}')
        return False


if __name__ == '__main__':
    test_mongo_connection()
