"""
models.py for Absolut Cinema Booking App

We're using MongoDB with PyMongo directly, so we DON'T need Django ORM models.
All database operations are handled through the mongo_db.py connection.

This file is kept here because Django expects a models.py file to exist in each app,
but it remains empty since we're not using Django's ORM.

MongoDB Collections (accessed via mongo_db.py):
- movies
- venues  
- showtimes
- bookings
- users (custom MongoDB users, separate from Django auth users)
"""

# No Django models needed - we use PyMongo directly!