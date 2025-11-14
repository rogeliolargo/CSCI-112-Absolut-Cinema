from django.shortcuts import render   # NEW import

# Login page (Ayesha)
def login_view(request):
    # Render the login HTML template instead of plain text
    return render(request, "booking/login.html")

# Browse movies / showtimes (Ronnel)
def movies_view(request):
    return render(request, "booking/movies.html")

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
