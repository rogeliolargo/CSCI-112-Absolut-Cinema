from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
from datetime import datetime, timedelta
from bson import ObjectId

import random
import string

# MongoDB connection - this is all we need!
from .mongo_db import db

# -- helper functions for ticket and masking -- gelo

# for the admin dashboard
def analytics_data(request):
    from django.http import JsonResponse
    from .mongo_db import db 

    # MOVIE REVENUE
    pipeline_movie = [
        {"$group": {
            "_id": "$movie_id",
            "total_revenue": {"$sum": "$total_price"},
            "tickets_sold": {"$sum": {"$size": "$seats"}}
        }},
        {"$lookup": {
            "from": "movies",
            "localField": "_id",
            "foreignField": "_id",
            "as": "movie"
        }},
        {"$unwind": "$movie"},
        {"$project": {
            "_id": "$movie.title",
            "total_revenue": 1,
            "tickets_sold": 1
        }}
    ]

    movie_revenue = list(db.bookings.aggregate(pipeline_movie))

    # VENUE REVENUE
    pipeline_venue = [
        {"$group": {
            "_id": "$venue_id",
            "total_revenue": {"$sum": "$total_price"},
            "total_tickets": {"$sum": {"$size": "$seats"}}
        }},
        {"$lookup": {
            "from": "venues",
            "localField": "_id",
            "foreignField": "_id",
            "as": "venue"
        }},
        {"$unwind": "$venue"},
        {"$project": {
            "_id": "$venue.name",
            "total_revenue": 1,
            "total_tickets": 1,
            "city": "$venue.city"
        }}
    ]

    venue_revenue = list(db.bookings.aggregate(pipeline_venue))

    # DAILY SALES
    pipeline_daily = [
        {"$group": {
            "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$payment.paid_at"}},
            "daily_sales": {"$sum": "$total_price"},
            "tickets_sold": {"$sum": {"$size": "$seats"}}
        }},
        {"$sort": {"_id": 1}}
    ]

    daily_sales = list(db.bookings.aggregate(pipeline_daily))

    return JsonResponse({
        "movieRevenue": movie_revenue,
        "venueRevenue": venue_revenue,
        "dailySales": daily_sales
    }, safe=False)

def generate_ticket_ref():
    """
    Creates a short ticket reference like: ACB-3F9K2
    ACB = Absolut Cinema Booking
    """
    prefix = "ACB"
    random_part = "".join(
        random.choices(string.ascii_uppercase + string.digits, k=5)
    )
    return f"{prefix}-{random_part}"


def mask_account_number(method, number):
    """
    Only show last 4 digits. We never save the raw number.
    """
    last4 = number[-4:]
    if method == "gcash":
        return f"GCash ••••{last4}"
    return f"Card ••••{last4}"


# ------------------------
# AUTH
# ------------------------

def auth_page(request):
    return render(request, 'booking/auth.html')

def signup_view(request):
    if request.method == "POST":
        user = User.objects.create_user(
            username=request.POST["username"],
            password=request.POST["password"],
            first_name=request.POST["name"]
        )
        login(request, user)
        return redirect("movies")

    return redirect("auth_page")

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)

            # ADMIN → dashboard
            if user.is_staff or user.is_superuser:
                return redirect('admin_dashboard')

            # CUSTOMER → movies
            return redirect('movies')

        return render(request, "booking/auth.html", {
            "error": "Invalid Credentials"
        })

    return redirect('auth_page')

# ------------------------
# MOVIES PAGE
# ------------------------

@login_required
def movies_view(request):
    # Fetch from MongoDB instead of SQL
    movies = list(db.movies.find())
    showtimes = list(db.showtimes.find())
    
    # Convert movie ObjectIds to strings for consistency
    for movie in movies:
        movie["id"] = str(movie["_id"])  # Add 'id' key for template compatibility
    
    # Enrich showtimes with movie and venue details, convert ObjectId to string for URLs
    enriched_showtimes = []
    for st in showtimes:
        movie = db.movies.find_one({"_id": st["movie_id"]})
        venue = db.venues.find_one({"_id": st["venue_id"]})
        
        # Ensure movie and venue have 'id' fields too
        if movie:
            movie["id"] = str(movie["_id"])
        if venue:
            venue["id"] = str(venue["_id"])
        
        enriched_showtimes.append({
            "_id": str(st["_id"]),  # Convert ObjectId to string for URL
            "id": str(st["_id"]),   # Also add 'id' key for template compatibility
            "movie_id": str(st["movie_id"]),
            "venue_id": str(st["venue_id"]),
            "movie": movie,
            "venue": venue,
            "screen_name": st.get("screen_name"),
            "schedule": st.get("schedule"),
            "price": st.get("price"),
            "seats": st.get("seats", [])
        })
    
    return render(request, "booking/movies.html", {
        "movies": movies,
        "showtimes": enriched_showtimes
    })


# ------------------------
# RESERVE PAGE
# ------------------------

@login_required
def reserve_view(request, showtime_id):
    try:
        # Convert string showtime_id to ObjectId for MongoDB query
        showtime_oid = ObjectId(showtime_id)
        showtime = db.showtimes.find_one({"_id": showtime_oid})
        
        if not showtime:
            return redirect("movies")
        
        # Get the associated movie and venue
        movie = db.movies.find_one({"_id": showtime["movie_id"]})
        venue = db.venues.find_one({"_id": showtime["venue_id"]})
        
        # Format showtime data for template
        showtime_display = {
            "date": showtime["schedule"].strftime("%B %d, %Y") if showtime.get("schedule") else "N/A",
            "time": showtime["schedule"].strftime("%I:%M %p") if showtime.get("schedule") else "N/A",
            "venue": venue["name"] if venue else "N/A",
            "price": showtime.get("price", 0),
            "screen_name": showtime.get("screen_name", "Screen")
        }
        
        return render(request, "booking/reserve.html", {
            "showtime": showtime_display,
            "showtime_id": showtime_id,
            "movie": movie,
            "venue": venue,
        })
    except:
        # Invalid ObjectId format
        return redirect("movies")

# ------------------------
# APIs
# ------------------------

def seat_availability_api(request, showtime_id):
    try:
        # Convert string showtime_id to ObjectId for MongoDB query
        showtime_oid = ObjectId(showtime_id)
        showtime = db.showtimes.find_one({"_id": showtime_oid})
        
        if not showtime:
            return JsonResponse({"error": "Showtime not found"}, status=404)
        
        # Get seats from showtime document
        seats = showtime.get("seats", [])
        data = [
            {"seat": s["seat"], "is_taken": s["status"] == "sold"}
            for s in seats
        ]
        return JsonResponse(data, safe=False)
    except:
        return JsonResponse({"error": "Invalid showtime ID"}, status=400)


@csrf_exempt
def reserve_seat_api(request):
    if request.method == "POST":
        print("\n" + "="*60)
        print("RESERVE_SEAT_API CALLED")
        print("="*60)
        
        try:
            body = json.loads(request.body)
            showtime_id = body.get("showtime_id")
            seat_ids = body.get("seat_ids", [])
            user_id = request.user.id
            
                         
            print(f"DEBUG reserve_seat_api: Received request")
            print(f"  showtime_id={showtime_id} (type: {type(showtime_id)})")
            print(f"  seat_ids={seat_ids}")
            print(f"  user_id={user_id} (type: {type(user_id)})")
            
            if not showtime_id or not seat_ids:
                print("DEBUG: Missing showtime_id or seat_ids")
                return JsonResponse({"error": "Missing data"}, status=400)
            
            # Convert string showtime_id to ObjectId
            showtime_oid = ObjectId(showtime_id)
            showtime = db.showtimes.find_one({"_id": showtime_oid})
            
            if not showtime:
                print("DEBUG: Showtime not found")
                return JsonResponse({"error": "Showtime not found"}, status=404)
            
            print(f"DEBUG: Found showtime with {len(showtime.get('seats', []))} seats")
            
            # Check if seats are available and mark them as sold
            reserved = []
            for seat_num in seat_ids:
                print(f"DEBUG: Checking seat {seat_num}")
                seat_found = False
                for seat in showtime["seats"]:
                    if seat["seat"] == seat_num:
                        seat_found = True
                        print(f"DEBUG: Found seat {seat_num}, status: {seat['status']}")
                        if seat["status"] == "available":
                            seat["status"] = "sold"
                            seat["booking_id"] = ObjectId()  # Temporary booking ID
                            reserved.append(seat_num)
                            print(f"DEBUG: Marked seat {seat_num} as sold")
                        else:
                            print(f"DEBUG: Seat {seat_num} already taken")
                            return JsonResponse({"error": f"Seat {seat_num} already taken"}, status=400)
                        break
                
                if not seat_found:
                    print(f"DEBUG: Seat {seat_num} does not exist")
                    return JsonResponse({"error": f"Seat {seat_num} does not exist"}, status=400)
            
            # Update the showtime document in MongoDB
            db.showtimes.update_one(
                {"_id": showtime_oid},
                {"$set": {"seats": showtime["seats"]}}
            )
            
            # Create a booking record in MongoDB bookings collection
            if not reserved:
                print("DEBUG: No seats were reserved!")
                return JsonResponse({"error": "No seats were reserved"}, status=400)
            
            booking_id = ObjectId()
            booking_data = {
                "_id": booking_id,
                "user_id": user_id,
                "movie_id": showtime["movie_id"],
                "venue_id": showtime["venue_id"],
                "showtime_id": showtime_oid,
                "seats": reserved,
                "total_price": len(reserved) * showtime["price"],
                "booking_confirmed": False,
                "payment": {},
                "ticket": {}
            }
            print(f"DEBUG reserve_seat_api: Creating booking with:")
            print(f"  _id={booking_id}")
            print(f"  user_id={user_id} (type: {type(user_id)})")
            print(f"  showtime_id={showtime_oid} (type: {type(showtime_oid)})")
            print(f"  seats={reserved}")
            print(f"  booking_confirmed=False")
            
            db.bookings.insert_one(booking_data)
            print(f"DEBUG: Booking created successfully with ID {booking_id}")
            
            # Verify it was created
            created_booking = db.bookings.find_one({"_id": booking_id})
            print(f"DEBUG: Verified booking exists in DB: {created_booking is not None}")
            
            print(f"DEBUG: Returning success with reserved seats: {reserved}")
            return JsonResponse({"message": "Seats reserved", "reserved": reserved})
        
        except json.JSONDecodeError as e:
            print(f"DEBUG: JSON decode error: {e}")
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        except Exception as e:
            print(f"DEBUG: Exception in reserve_seat_api: {e}")
            import traceback
            traceback.print_exc()
            return JsonResponse({"error": str(e)}, status=500)

# Payment page (Ayesha) -- gelo edits here for payment stuff backend 3
@login_required
def payment_view(request):
    print("\n" + "="*60)
    print("PAYMENT_VIEW CALLED")
    print("="*60)
    
    # 1. Which showtime is the user paying for?
    showtime_id = request.GET.get("showtime_id")
    print(f"DEBUG payment_view: showtime_id={showtime_id}, user_id={request.user.id}")
    
    try:
        if not showtime_id:
            print("DEBUG: No showtime_id provided")
            return redirect("movies")
            
        showtime_oid = ObjectId(showtime_id)
        showtime = db.showtimes.find_one({"_id": showtime_oid})
        
        if not showtime:
            print("DEBUG: Showtime not found in DB")
            return redirect("movies")
        
        # 2. Get the booking for this user & showtime
        # Try multiple times in case of timing issues
        booking = None
        for attempt in range(3):
            booking = db.bookings.find_one({
                "user_id": request.user.id,
                "showtime_id": showtime_oid,
                "booking_confirmed": False
            })
            if booking:
                break
            if attempt < 2:
                print(f"DEBUG: Booking not found on attempt {attempt + 1}, retrying...")
                import time
                time.sleep(0.5)
        
        print(f"DEBUG payment_view: Looking for booking with:")
        print(f"  user_id={request.user.id} (type: {type(request.user.id)})")
        print(f"  showtime_id={showtime_oid} (type: {type(showtime_oid)})")
        print(f"  booking_confirmed=False")
        print(f"DEBUG: Found booking after {(3 if not booking else 1)} attempt(s): {booking is not None}")
        
        if not booking:
            print("DEBUG: No booking found - checking all bookings for this user")
            all_bookings = list(db.bookings.find({"user_id": request.user.id}))
            print(f"DEBUG: Total bookings for user {request.user.id}: {len(all_bookings)}")
            for b in all_bookings:
                print(f"DEBUG: Booking {b['_id']}: user_id={b.get('user_id')} (type: {type(b.get('user_id'))}), showtime_id={b.get('showtime_id')} (type: {type(b.get('showtime_id'))}), confirmed={b.get('booking_confirmed')}")
            
            print("DEBUG: Checking if any bookings match without confirmed filter:")
            all_bookings_any = list(db.bookings.find({"user_id": request.user.id, "showtime_id": showtime_oid}))
            print(f"DEBUG: Found {len(all_bookings_any)} bookings with matching user and showtime")
            for b in all_bookings_any:
                print(f"DEBUG: Booking: {b}")
            
            return redirect("movies")
        
        # 3. Get movie and venue info
        movie = db.movies.find_one({"_id": showtime["movie_id"]})
        venue = db.venues.find_one({"_id": showtime["venue_id"]})
        
        total_amount = booking["total_price"]
        
        if request.method == "POST":
            # 4. Read form data
            method = request.POST["payment_method"]      # "gcash" or "card"
            account_num = request.POST["account_number"]  # user input

            # 5. "Process" payment: generate ticket + mask account
            ticket_ref = generate_ticket_ref()
            masked = mask_account_number(method, account_num)

            # 6. Update booking with payment info
            db.bookings.update_one(
                {"_id": booking["_id"]},
                {"$set": {
                    "booking_confirmed": True,
                    "payment": {
                        "payment_method": method,
                        "masked_account": masked,
                        "paid_at": datetime.now()
                    },
                    "ticket": {
                        "ticket_ref": ticket_ref,
                        "issued": datetime.now(),
                        "status": "active"
                    }
                }}
            )

            # 7. Store minimal info in session for confirm page
            request.session["last_ticket_ref"] = ticket_ref
            request.session["last_showtime_id"] = showtime_id
            request.session["last_booking_id"] = str(booking["_id"])

            # 8. Redirect to e-ticket page
            return redirect("confirm")

        # GET request → just show the payment form
        return render(request, "booking/payment.html", {
            "showtime": showtime,
            "movie": movie,
            "venue": venue,
            "booking": booking,
            "total_amount": total_amount,
        })
    
    except Exception as e:
        print(f"DEBUG: Exception in payment_view: {e}")
        import traceback
        traceback.print_exc()
        return redirect("movies")

@login_required
def confirm_view(request):
    ticket_ref = request.session.get("last_ticket_ref")
    showtime_id = request.session.get("last_showtime_id")
    booking_id = request.session.get("last_booking_id")

    # If someone manually goes to /confirm with no session data
    if not ticket_ref or not showtime_id or not booking_id:
        return redirect("movies")

    try:
        showtime_oid = ObjectId(showtime_id)
        booking_oid = ObjectId(booking_id)
        
        # Get the booking
        booking = db.bookings.find_one({"_id": booking_oid})
        
        if not booking or booking["user_id"] != request.user.id:
            return redirect("movies")
        
        # Get showtime, movie, and venue
        showtime = db.showtimes.find_one({"_id": showtime_oid})
        movie = db.movies.find_one({"_id": showtime["movie_id"]})
        venue = db.venues.find_one({"_id": showtime["venue_id"]})
        
        if not showtime or not movie or not venue:
            return redirect("movies")
        
        return render(request, "booking/confirm.html", {
            "ticket_ref": ticket_ref,
            "showtime": showtime,
            "booking": booking,
            "movie": movie,
            "venue": venue,
            "payment_method": booking["payment"].get("payment_method", "N/A"),
            "masked_account": booking["payment"].get("masked_account", "N/A"),
        })
    
    except Exception as e:
        return redirect("movies")

# Admin dashboard / analytics (Ronnel)
@login_required
def admin_dashboard_view(request):
    return render(request, "booking/admin_dashboard.html")