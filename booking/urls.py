from django.urls import path
from . import views

from django.shortcuts import render   # NEW import
from django.shortcuts import render, redirect

urlpatterns = [
    path("", views.auth_page, name="auth_page"),
    path('admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path("dashboard/analytics-data/", views.analytics_data),
    path("login/", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),

    path("movies/", views.movies_view, name="movies"),

    # seat reservation page - changed to <str:showtime_id> for MongoDB ObjectIds
    path("reserve/<str:showtime_id>/", views.reserve_view, name="reserve"),

    # APIs - also changed to <str:showtime_id> for MongoDB ObjectIds
    path("api/seats/<str:showtime_id>/", views.seat_availability_api),
    path("api/reserve/", views.reserve_seat_api),

    # other pages
    path("payment/", views.payment_view, name="payment"),
    path("confirm/", views.confirm_view, name="confirm"),
]