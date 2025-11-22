from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
from bson import ObjectId
import os

load_dotenv()
uri = os.getenv("MONGODB_URI")

client = MongoClient(uri, server_api=ServerApi('1'))
db = client.absolutcinema

print("\n🔍 VALIDATING DATABASE...\n")

showtimes = list(db.showtimes.find({}))
bookings = list(db.bookings.find({}))
movies = list(db.movies.find({}))
venues = list(db.venues.find({}))
users = list(db.users.find({}))

# Lookup users
user_ids = {str(u["_id"]) for u in users}

# --------------------------------------------
# 1. SOLD SEATS → MUST BE FOUND IN BOOKINGS
# --------------------------------------------
print("1️⃣ Checking SOLD seats have matching bookings...\n")

mismatches = []

for st in showtimes:
    stid = str(st["_id"])
    movie = str(st["movie_id"])
    venue = str(st["venue_id"])

    sold = {seat["seat"] for seat in st["seats"] if seat["status"] == "sold"}

    # Find bookings for this movie + venue
    booked = set()
    for b in bookings:
        if str(b["movie_id"]) == movie and str(b["venue_id"]) == venue:
            booked.update(b["seats"])

    if sold != booked:
        mismatches.append({
            "showtime_id": stid,
            "sold_seats": list(sold),
            "booked_seats": list(booked)
        })

if len(mismatches) == 0:
    print("✔ All sold seats match bookings.\n")
else:
    print("❌ MISMATCH FOUND:")
    for m in mismatches:
        print(m)
    print()


# --------------------------------------------
# 2. BOOKINGS MUST REFERENCE SOLD SEATS ONLY
# --------------------------------------------
print("2️⃣ Checking bookings do not contain seats that are not sold...\n")

invalid_booking_seats = []

for b in bookings:
    movie = str(b["movie_id"])
    venue = str(b["venue_id"])

    st = db.showtimes.find_one({
        "movie_id": ObjectId(movie),
        "venue_id": ObjectId(venue)
    })

    if st is None:
        invalid_booking_seats.append({
            "booking_id": str(b["_id"]),
            "error": "No matching showtime found"
        })
        continue

    sold = {seat["seat"] for seat in st["seats"] if seat["status"] == "sold"}

    for seat in b["seats"]:
        if seat not in sold:
            invalid_booking_seats.append({
                "booking_id": str(b["_id"]),
                "seat": seat,
                "error": "Seat booked but not marked sold in showtime"
            })

if len(invalid_booking_seats) == 0:
    print("✔ All booking seats are correctly marked sold.\n")
else:
    print("❌ Invalid booking seats:")
    for e in invalid_booking_seats:
        print(e)
    print()


# --------------------------------------------
# 3. CHECK USER REFERENCES
# --------------------------------------------
print("3️⃣ Checking user_id references in bookings...\n")

broken_users = []

for b in bookings:
    if str(b["user_id"]) not in user_ids:
        broken_users.append({
            "booking_id": str(b["_id"]),
            "missing_user_id": str(b["user_id"])
        })

if len(broken_users) == 0:
    print("✔ All bookings reference valid users.\n")
else:
    print("❌ Broken references found:")
    for u in broken_users:
        print(u)
    print()


# --------------------------------------------
# SUMMARY
# --------------------------------------------
print("\n===================================")

if len(mismatches) == 0 and len(invalid_booking_seats) == 0 and len(broken_users) == 0:
    print("🎉 DATABASE IS PERFECTLY CONSISTENT ❤️")
else:
    print("⚠ SOME ISSUES FOUND — check above.")

print("===================================\n")

client.close()