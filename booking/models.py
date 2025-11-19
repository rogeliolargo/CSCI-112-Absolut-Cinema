from django.db import models
from django.contrib.auth.models import User

class Movie(models.Model):
    title = models.CharField(max_length=100, null=False, blank=True)
    description = models.TextField(null=True, blank=True)
    genre = models.CharField(max_length=100, null=True, blank=True)
    rated = models.CharField(max_length=20, null=True, blank=True)
    runtime_mins = models.IntegerField(null=True, blank=True)
    release_date = models.DateField(null=True, blank=True)
    director = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.title

class Showtime(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    venue = models.CharField(max_length=255)
    date = models.DateField()
    time = models.TimeField()
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.movie.title} - {self.venue} @ {self.time}"

class Seat(models.Model):
    showtime = models.ForeignKey(Showtime, on_delete=models.CASCADE)
    seat_number = models.CharField(max_length=10)
    is_taken = models.BooleanField(default=False)

class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    reserved_at = models.DateTimeField(auto_now_add=True)

    # Backend 3 stuff: payment and ticket info -
    is_paid = models.BooleanField(default=False)

    payment_method = models.CharField(
        max_length=10,
        choices=[
            ("gcash", "GCash"),
            ("card", "Card"),
        ],
        null=True,
        blank=True,
    )

    ticket_ref = models.CharField(
        max_length=20,
        null=True,
        blank=True,
    )

    # only masked value (e.g. "GCash ••••1234"), no real number stored
    masked_account = models.CharField(
        max_length=32,
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.user.username} - {self.seat.seat_number} - {self.ticket_ref or 'UNPAID'}"