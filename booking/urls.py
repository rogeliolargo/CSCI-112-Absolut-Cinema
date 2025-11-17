from django.urls import path
from . import views

urlpatterns = [
    # Ayesha: login page
    path('', views.auth_page, name='auth_page'),   # login + signup page
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('browse/', views.movies_view, name='browse'),

    # Ronnel: movies/showtimes page
    path('movies/', views.movies_view, name='movies'),

    # Ronnel: seat selection page
    path('reserve/', views.reserve_view, name='reserve'),

    # Ayesha: payment page
    path('payment/', views.payment_view, name='payment'),

    # Ayesha: confirmation / e-ticket page
    path('confirm/', views.confirm_view, name='confirm'),

    # Ronnel (admin visualizations)
    path('admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
]
