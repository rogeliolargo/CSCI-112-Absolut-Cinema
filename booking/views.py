from django.shortcuts import render   # NEW import
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

# added by chels
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
from .models import Movie, Showtime, Seat, Reservation

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from .models import Movie, Showtime, Seat, Reservation


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
    movies = Movie.objects.all()
    showtimes = Showtime.objects.all()
    return render(request, "booking/movies.html", {
        "movies": movies,
        "showtimes": showtimes
    })


# ------------------------
# RESERVE PAGE
# ------------------------

@login_required
def reserve_view(request, showtime_id):
    showtime = Showtime.objects.get(id=showtime_id)
    movie = showtime.movie

    return render(request, "booking/reserve.html", {
        "showtime": showtime,
        "showtime_id": showtime_id,
        "movie": movie,
    })

# ------------------------
# APIs
# ------------------------

def seat_availability_api(request, showtime_id):
    seats = Seat.objects.filter(showtime_id=showtime_id)
    data = [
        {"seat_number": s.seat_number, "is_taken": s.is_taken}
        for s in seats
    ]
    return JsonResponse(data, safe=False)


@csrf_exempt
def reserve_seat_api(request):
    if request.method == "POST":
        body = json.loads(request.body)
        seat_numbers = body.get("seats", [])
        showtime_id = body["showtime_id"]
        user_id = body["user_id"]

        reserved = []

        for seat_num in seat_numbers:
            try:
                seat = Seat.objects.get(showtime_id=showtime_id, seat_number=seat_num)
            except Seat.DoesNotExist:
                return JsonResponse({"error": f"Seat {seat_num} does not exist"}, status=400)

            if seat.is_taken:
                return JsonResponse({"error": f"Seat {seat_num} already taken"}, status=409)

            seat.is_taken = True
            seat.save()

            Reservation.objects.create(
                user_id=user_id,
                seat=seat
            )

            reserved.append(seat_num)

        return JsonResponse({"message": "Seats reserved", "reserved": reserved})

# Payment page (Ayesha)
def payment_view(request):
    return render(request, "booking/payment.html")

# Confirmation / e-ticket (Ayesha)
def confirm_view(request):
    return render(request, "booking/confirm.html")

# Admin dashboard / analytics (Ronnel)
def admin_dashboard_view(request):
    return render(request, "booking/admin_dashboard.html")
