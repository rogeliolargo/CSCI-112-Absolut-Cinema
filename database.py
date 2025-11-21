from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os

load_dotenv()
uri = os.getenv("MONGODB_URI")

# Create client
client = MongoClient(uri, server_api=ServerApi('1'))

# Access database
db = client.absolutcinema

# Export collections
venues = db.venues
movies = db.movies
users = db.users
showtimes = db.showtimes
bookings = db.bookings

# Test connection
try:
    client.admin.command('ping')
    print("✓ Connected to MongoDB Atlas")
except Exception as e:
    print(f"✗ Error: {e}")