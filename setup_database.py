from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
from datetime import datetime
from bson import ObjectId
import os

# Load environment variables
load_dotenv()
uri = os.getenv("MONGODB_URI")

# Create client
client = MongoClient(uri, server_api=ServerApi('1'))

# Create/access database
db = client.absolutcinema

print("🎬 Setting up Absolut Cinema database...\n")

# ============================================
# 1. CREATE VENUES COLLECTION
# ============================================
print("Creating Venues...")
venues_collection = db.venues

venues_data = [
    {
        "_id": ObjectId("612345abcdef678901234567"),
        "name": "Absolut Cinema - Katipunan",
        "city": "Quezon City",
        "address": "123 Katipunan Avenue",
        "contact_number": "09171234567",
        "email": "info@absolutcinema.com",
        "features": ["Dolby Surround", "VIP Lounge", "Snacks Available"]
    },
    {
        "_id": ObjectId("612345abcdef678901234568"),
        "name": "Absolut Cinema - SM North",
        "city": "Quezon City",
        "address": "SM North EDSA Complex",
        "contact_number": "09285554433",
        "email": "north@absolutcinema.com",
        "features": ["IMAX", "Airconditioned", "Wheelchair Accessible"]
    },
    {
        "_id": ObjectId("612345abcdef678901234569"),
        "name": "Absolut Cinema - Glorietta",
        "city": "Makati City",
        "address": "2nd Floor, Glorietta 4 Mall",
        "contact_number": "09391234567",
        "email": "glorietta@absolutcinema.com",
        "features": ["4DX", "Premium Recliners"]
    }
]

venues_collection.delete_many({})
venues_collection.insert_many(venues_data)
print(f"✓ Inserted {len(venues_data)} venues\n")

# ============================================
# 2. CREATE MOVIES COLLECTION
# ============================================
print("Creating Movies...")
movies_collection = db.movies

movies_data = [
    {
        "_id": ObjectId("654321abcdef123456789012"),
        "title": "White Chicks",
        "description": "A film about two African-American FBI agent brothers who go undercover as two blonde white women.",
        "genre": "Comedy",
        "runtime_mins": 109,
        "rated": "PG-13",
        "release_date": datetime(2004, 6, 23),
        "director": "Keenen Ivory Wayans"
    },
    {
        "_id": ObjectId("654321abcdef123456789013"),
        "title": "Interstellar",
        "description": "A team of explorers travel through a wormhole in space in an attempt to ensure humanity's survival.",
        "genre": "Sci-Fi",
        "runtime_mins": 169,
        "rated": "PG-13",
        "release_date": datetime(2014, 11, 7),
        "director": "Christopher Nolan"
    },
    {
        "_id": ObjectId("654321abcdef123456789014"),
        "title": "The Dark Knight",
        "description": "Batman faces the Joker, a criminal mastermind spreading chaos in Gotham City.",
        "genre": "Action",
        "runtime_mins": 152,
        "rated": "PG-13",
        "release_date": datetime(2008, 7, 18),
        "director": "Christopher Nolan"
    }
]

movies_collection.delete_many({})
movies_collection.insert_many(movies_data)
print(f"✓ Inserted {len(movies_data)} movies\n")

# ============================================
# 3. CREATE USERS COLLECTION
# ============================================
print("Creating Users...")
users_collection = db.users

users_data = [
    {
        "_id": ObjectId("654321abcdef123456789013"),
        "name": "Juan dela Cruz",
        "email": "juandelacruz@gmail.com",
        "gcash_number": "09171234567",
        "card_number": "1111 2222 3333 4444",
        "tickets": [
            ObjectId("654321abcdef123456789014")  # Reference to booking/ticket
        ]
    }
]

users_collection.delete_many({})
users_collection.insert_many(users_data)
print(f"✓ Inserted {len(users_data)} users\n")



# ============================================
# 3B. CREATE SYSTEM USERS (Admin + Customer)
# ============================================
print("Creating System Login Users (Admin + Customer)...")

system_users_collection = db.system_users   # new collection for login accounts

# Clear existing users (optional)
system_users_collection.delete_many({})

# Simple password hashing (recommended)
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

system_users_data = [
    {
        "_id": ObjectId(),
        "username": "admin",
        "password": hash_password("admin123"),
        "role": "admin",
        "created_at": datetime.utcnow()
    },
    {
        "_id": ObjectId(),
        "username": "customer",
        "password": hash_password("customer123"),
        "role": "customer",
        "created_at": datetime.utcnow()
    }
]

system_users_collection.insert_many(system_users_data)
print("✓ Created admin (admin/admin123) and customer (customer/customer123)\n")

# ============================================
# 4. CREATE SHOWTIMES COLLECTION
# ============================================
print("Creating Showtimes...")
showtimes_collection = db.showtimes
showtimes_data = [
    # White Chicks — Showtime 1
    {
        "_id": ObjectId("612345abcdef678901234570"),
        "movie_id": ObjectId("654321abcdef123456789012"),
        "venue_id": ObjectId("612345abcdef678901234567"),
        "screen_name": "Cinema 2",
        "schedule": datetime(2025, 12, 10, 18, 0, 0),
        "price": 400,
        "seats": [
            {"seat": f"A{i}", "status": "sold" if i in [5,6,12] else "available"}
            for i in range(1,16)
        ]
    },

    # White Chicks — Showtime 2
    {
        "_id": ObjectId("612345abcdef678901234571"),
        "movie_id": ObjectId("654321abcdef123456789012"),
        "venue_id": ObjectId("612345abcdef678901234568"),
        "screen_name": "Cinema 1",
        "schedule": datetime(2025, 12, 10, 21, 0, 0),
        "price": 420,
        "seats": [
            {"seat": f"B{i}", "status": "sold" if i in [3,9] else "available"}
            for i in range(1,16)
        ]
    },

    # White Chicks — Showtime 3
    {
        "_id": ObjectId("612345abcdef678901234572"),
        "movie_id": ObjectId("654321abcdef123456789012"),
        "venue_id": ObjectId("612345abcdef678901234569"),
        "screen_name": "Cinema 4",
        "schedule": datetime(2025, 12, 11, 17, 30, 0),
        "price": 450,
        "seats": [
            {"seat": f"C{i}", "status": "sold" if i == 4 else "available"}
            for i in range(1,16)
        ]
    },
    # Interstellar — Showtime 1
    {
        "_id": ObjectId("612345abcdef678901234573"),
        "movie_id": ObjectId("654321abcdef123456789013"),
        "venue_id": ObjectId("612345abcdef678901234567"),
        "screen_name": "Cinema 3",
        "schedule": datetime(2025, 12, 12, 16, 0, 0),
        "price": 480,
        "seats": [
            {"seat": f"D{i}", "status": "sold" if i in [2,7] else "available"}
            for i in range(1,16)
        ]
    },

    # Interstellar — Showtime 2
    {
        "_id": ObjectId("612345abcdef678901234574"),
        "movie_id": ObjectId("654321abcdef123456789013"),
        "venue_id": ObjectId("612345abcdef678901234568"),
        "screen_name": "Cinema 1",
        "schedule": datetime(2025, 12, 12, 20, 0, 0),
        "price": 500,
        "seats": [
            {"seat": f"E{i}", "status": "sold" if i in [5] else "available"}
            for i in range(1,16)
        ]
    },

    # Dark Knight — Showtime 1
    {
        "_id": ObjectId("612345abcdef678901234575"),
        "movie_id": ObjectId("654321abcdef123456789014"),
        "venue_id": ObjectId("612345abcdef678901234569"),
        "screen_name": "Cinema 5",
        "schedule": datetime(2025, 12, 13, 18, 30, 0),
        "price": 450,
        "seats": [
            {"seat": f"F{i}", "status": "sold" if i in [8] else "available"}
            for i in range(1,16)
        ]
    },

    # Dark Knight — Showtime 2
    {
        "_id": ObjectId("612345abcdef678901234576"),
        "movie_id": ObjectId("654321abcdef123456789014"),
        "venue_id": ObjectId("612345abcdef678901234568"),
        "screen_name": "Cinema 6",
        "schedule": datetime(2025, 12, 13, 21, 0, 0),
        "price": 480,
        "seats": [
            {"seat": f"G{i}", "status": "sold" if i in [1,12] else "available"}
            for i in range(1,16)
        ]
    }

]

showtimes_collection.delete_many({})
showtimes_collection.insert_many(showtimes_data)
print(f"✓ Inserted {len(showtimes_data)} showtimes\n")

# ============================================
# 5. CREATE BOOKINGS COLLECTION (FINAL SCHEMA)
# ============================================
print("Creating Bookings (consolidated schema)...")
bookings_collection = db.bookings

# Sample booking using your FINAL schema
bookings_data = [
    # -------------------------
    # WHITE CHICKS BOOKINGS
    # -------------------------
    {
        "_id": ObjectId("654321abcdef123456789014"),
        "user_id": ObjectId("654321abcdef123456789013"),
        "movie_id": ObjectId("654321abcdef123456789012"),
        "venue_id": ObjectId("612345abcdef678901234567"),  # Cinema 2
        "showtimes": {
            "schedule": datetime(2025, 11, 10, 18, 0),
            "price": 400
        },
        "seats": ["A5", "A6", "A12"],
        "total_price": 1200,
        "booking_confirmed": True,
        "payment": {
            "payment_method": "gcash",
            "paid_at": datetime(2025, 11, 10, 15, 20)
        },
        "ticket": {
            "issued": datetime(2025, 11, 10, 15, 24),
            "status": "active",
            "wallet_sent": True,
            "email_sent": True
        }
    },

    {
        "_id": ObjectId("654321abcdef123456789015"),
        "user_id": ObjectId("654321abcdef123456789020"),
        "movie_id": ObjectId("654321abcdef123456789012"),
        "venue_id": ObjectId("612345abcdef678901234568"),  # Cinema 1
        "showtimes": {
            "schedule": datetime(2025, 11, 10, 21, 0),
            "price": 420
        },
        "seats": ["B3", "B9"],
        "total_price": 840,
        "booking_confirmed": True,
        "payment": {
            "payment_method": "card",
            "paid_at": datetime(2025, 11, 10, 19, 45)
        },
        "ticket": {
            "issued": datetime(2025, 11, 10, 19, 46),
            "status": "active",
            "wallet_sent": False,
            "email_sent": True
        }
    },

    {
        "_id": ObjectId("654321abcdef123456789016"),
        "user_id": ObjectId("654321abcdef123456789021"),
        "movie_id": ObjectId("654321abcdef123456789012"),
        "venue_id": ObjectId("612345abcdef678901234569"),  # Cinema 4
        "showtimes": {
            "schedule": datetime(2025, 11, 11, 17, 30),
            "price": 450
        },
        "seats": ["C4"],
        "total_price": 450,
        "booking_confirmed": True,
        "payment": {
            "payment_method": "gcash",
            "paid_at": datetime(2025, 11, 11, 14, 10)
        },
        "ticket": {
            "issued": datetime(2025, 11, 11, 14, 12),
            "status": "active",
            "wallet_sent": True,
            "email_sent": True
        }
    },

    # -------------------------
    # INTERSTELLAR BOOKINGS
    # -------------------------
    {
        "_id": ObjectId("654321abcdef123456789017"),
        "user_id": ObjectId("654321abcdef123456789030"),
        "movie_id": ObjectId("654321abcdef123456789013"),
        "venue_id": ObjectId("612345abcdef678901234567"),  # Cinema 3
        "showtimes": {
            "schedule": datetime(2025, 11, 12, 16, 0),
            "price": 480
        },
        "seats": ["D2", "D7"],
        "total_price": 960,
        "booking_confirmed": True,
        "payment": {
            "payment_method": "card",
            "paid_at": datetime(2025, 11, 12, 14, 50)
        },
        "ticket": {
            "issued": datetime(2025, 11, 12, 14, 52),
            "status": "active",
            "wallet_sent": True,
            "email_sent": True
        }
    },

    {
        "_id": ObjectId("654321abcdef123456789018"),
        "user_id": ObjectId("654321abcdef123456789031"),
        "movie_id": ObjectId("654321abcdef123456789013"),
        "venue_id": ObjectId("612345abcdef678901234568"),  # Cinema 1
        "showtimes": {
            "schedule": datetime(2025, 11, 12, 20, 0),
            "price": 500
        },
        "seats": ["E5"],
        "total_price": 500,
        "booking_confirmed": True,
        "payment": {
            "payment_method": "gcash",
            "paid_at": datetime(2025, 11, 12, 18, 40)
        },
        "ticket": {
            "issued": datetime(2025, 11, 12, 18, 42),
            "status": "active",
            "wallet_sent": True,
            "email_sent": True
        }
    },

    # -------------------------
    # THE DARK KNIGHT BOOKINGS
    # -------------------------
    {
        "_id": ObjectId("654321abcdef123456789019"),
        "user_id": ObjectId("654321abcdef123456789032"),
        "movie_id": ObjectId("654321abcdef123456789014"),
        "venue_id": ObjectId("612345abcdef678901234569"),  # Cinema 5
        "showtimes": {
            "schedule": datetime(2025, 11, 13, 18, 30),
            "price": 450
        },
        "seats": ["F8"],
        "total_price": 450,
        "booking_confirmed": True,
        "payment": {
            "payment_method": "card",
            "paid_at": datetime(2025, 11, 13, 16, 55)
        },
        "ticket": {
            "issued": datetime(2025, 11, 13, 16, 58),
            "status": "active",
            "wallet_sent": True,
            "email_sent": True
        }
    },

    {
        "_id": ObjectId("654321abcdef123456789020"),
        "user_id": ObjectId("654321abcdef123456789033"),
        "movie_id": ObjectId("654321abcdef123456789014"),
        "venue_id": ObjectId("612345abcdef678901234568"),  # Cinema 6
        "showtimes": {
            "schedule": datetime(2025, 11, 13, 21, 0),
            "price": 480
        },
        "seats": ["G1", "G12"],
        "total_price": 960,
        "booking_confirmed": True,
        "payment": {
            "payment_method": "gcash",
            "paid_at": datetime(2025, 11, 13, 19, 40)
        },
        "ticket": {
            "issued": datetime(2025, 11, 13, 19, 42),
            "status": "active",
            "wallet_sent": False,
            "email_sent": True
        }
    }
]

bookings_collection.delete_many({})
bookings_collection.insert_many(bookings_data)
print(f"✓ Inserted {len(bookings_data)} bookings\n")

# ============================================
# SUMMARY
# ============================================
print("=" * 50)
print("✅ Database setup complete!")
print("=" * 50)
print(f"\nDatabase: absolutcinema")
print(f"\nCollections created:")
print(f"  • venues      - {db.venues.count_documents({})} documents")
print(f"  • movies      - {db.movies.count_documents({})} documents")
print(f"  • users       - {db.users.count_documents({})} documents")
print(f"  • showtimes   - {db.showtimes.count_documents({})} documents")
print(f"  • bookings    - {db.bookings.count_documents({})} documents")

print(f"\n📋 Key IDs for reference:")
print(f"  Movie (White Chicks): 654321abcdef123456789012")
print(f"  User (Juan): 654321abcdef123456789013")
print(f"  Booking: 654321abcdef123456789014")
print(f"  Venue (Katipunan): 612345abcdef678901234567")

client.close()
print("\n🎉 Ready to start booking tickets!")