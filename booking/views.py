from django.shortcuts import render   # NEW import
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required

def auth_page(request):
    return render(request, 'booking/auth.html')

def signup_view(request):
    if request.method == "POST":
        name = request.POST["name"]
        contact = request.POST["contact"]
        username = request.POST["username"]
        password = request.POST["password"]

        # create user
        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=name,
        )
        user.save()

        # auto login new user
        user = authenticate(username=username, password=password)
        login(request, user)

        return redirect('browse')  # goes straight to browse movies

    return redirect('auth_page')

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('browse')
        else:
            return render(request, "booking/auth.html", {
                "error": "Invalid Credentials"
            })

    return redirect('auth_page')


# Browse movies / showtimes (Ronnel)
def movies_view(request):
    movies = [ #placeholder
        {"title": "Interstellar", "genre": "Sci-Fi"},
        {"title": "White Chicks", "genre": "Comedy"},
    ]
    return render(request, "booking/browse.html", {"movies": movies})

# Seat selection (Ronnel)
def reserve_view(request):
    return render(request, "booking/reserve.html")

# Payment page (Ayesha)
def payment_view(request):
    return render(request, "booking/payment.html")

# Confirmation / e-ticket (Ayesha)
def confirm_view(request):
    return render(request, "booking/confirm.html")

# Admin dashboard / analytics (Ronnel)
def admin_dashboard_view(request):
    return render(request, "booking/admin_dashboard.html")
