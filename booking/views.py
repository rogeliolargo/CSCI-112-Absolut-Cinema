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

import random
import string

from .models import Movie, Showtime, Seat, Reservation

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from .models import Movie, Showtime, Seat, Reservation

# -- helper functions for ticket and masking -- gelo

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

# Payment page (Ayesha) -- gelo edits here for payment stuff backend 3
@login_required
def payment_view(request):
    # 1. Which showtime is the user paying for?
    showtime_id = request.GET.get("showtime_id")
    showtime = get_object_or_404(Showtime, id=showtime_id)

    # 2. Get all UNPAID reservations for this user & showtime
    reservations = Reservation.objects.filter(
        user=request.user,
        seat__showtime=showtime,
        is_paid=False,
    ).select_related("seat")

    # If no unpaid reservation, send them back to movies
    if not reservations.exists():
        return redirect("movies")

    # 3. Compute total amount  
    #    (using showtime.price from your model)
    price_per_seat = showtime.price
    total_amount = reservations.count() * float(price_per_seat)

    if request.method == "POST":
        # 4. Read form data
        method = request.POST["payment_method"]      # "gcash" or "card"
        account_num = request.POST["account_number"]  # user input

        # 5. "Process" payment: generate ticket + mask account
        ticket_ref = generate_ticket_ref()
        masked = mask_account_number(method, account_num)

        # 6. Mark all these reservations as paid
        for r in reservations:
            r.is_paid = True
            r.payment_method = method
            r.ticket_ref = ticket_ref
            r.masked_account = masked
            r.save()

        # 7. Store minimal info in session for confirm page
        request.session["last_ticket_ref"] = ticket_ref
        request.session["last_showtime_id"] = showtime.id

        # 8. Redirect to e-ticket page
        return redirect("confirm")

    # GET request → just show the payment form
    return render(request, "booking/payment.html", {
        "showtime": showtime,
        "reservations": reservations,
        "total_amount": total_amount,
    })

@login_required
def confirm_view(request):
    ticket_ref = request.session.get("last_ticket_ref")
    showtime_id = request.session.get("last_showtime_id")

    # If someone manually goes to /confirm with no session data
    if not ticket_ref or not showtime_id:
        return redirect("movies")

    showtime = get_object_or_404(Showtime, id=showtime_id)

    # All reservations for this user + showtime + ticket
    reservations = Reservation.objects.filter(
        user=request.user,
        seat__showtime=showtime,
        ticket_ref=ticket_ref,
    ).select_related("seat")

    if not reservations.exists():
        return redirect("movies")

    sample = reservations.first()  # same payment info for all seats

    return render(request, "booking/confirm.html", {
        "ticket_ref": ticket_ref,
        "showtime": showtime,
        "reservations": reservations,
        "payment_method": sample.payment_method,
        "masked_account": sample.masked_account,
    })

# Admin dashboard / analytics (Ronnel)
def admin_dashboard_view(request):
    return render(request, "booking/admin_dashboard.html")
