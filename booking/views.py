from django.http import HttpResponse

# Ayesha - later replace with real HTML template
def login_view(request):
    return HttpResponse("Login page placeholder (Ayesha will design this).")

# Ronnel - later replace with real HTML template
def movies_view(request):
    return HttpResponse("Movies / showtimes page placeholder (Ronnel).")

# Ronnel - seat selection
def reserve_view(request):
    return HttpResponse("Reservation (seat selection) page placeholder (Ronnel).")

# Ayesha - payment form
def payment_view(request):
    return HttpResponse("Payment page placeholder (Ayesha).")

# Ayesha - confirmation/e-ticket
def confirm_view(request):
    return HttpResponse("Confirmation / e-ticket page placeholder (Ayesha).")

# Ronnel - admin analytics, visualizations
def admin_dashboard_view(request):
    return HttpResponse("Admin dashboard placeholder (for analytics/visuals).")
