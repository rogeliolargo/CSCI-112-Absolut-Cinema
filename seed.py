from datetime import date, time
from django.contrib.auth.models import User
from booking.models import Movie, Showtime, Seat

# Clear old data (optional)
Movie.objects.all().delete()
Showtime.objects.all().delete()
Seat.objects.all().delete()
User.objects.exclude(is_superuser=True).delete()   # keep Django superuser safe

print("Old data cleared.")

# --- CREATE ADMIN USER ---
if not User.objects.filter(username="admin").exists():
    admin = User.objects.create_superuser(
        username="admin",
        password="admin123",
        email="admin@example.com"
    )
    print("Admin user created (admin / admin123)")
else:
    print("Admin user already exists.")

# --- CREATE CUSTOMER USER ---
if not User.objects.filter(username="customer").exists():
    customer = User.objects.create_user(
        username="customer",
        password="customer123",
        first_name="SampleCustomer"
    )
    print("Customer user created (customer / customer123)")
else:
    print("Customer user already exists.")

# --- MOVIES ---

white_chicks = Movie.objects.create(
    title="White Chicks",
    description="Two FBI brothers go undercover and impersonate two white socialites.",
    genre="Comedy",
    rated="PG-13",
    runtime_mins=109,
    release_date=date(2004, 6, 23),
    director="Keenen Ivory Wayans"
)

dark_knight = Movie.objects.create(
    title="The Dark Knight",
    description="Batman battles the Joker in Gotham City.",
    genre="Action",
    rated="PG-13",
    runtime_mins=152,
    release_date=date(2008, 7, 18),
    director="Christopher Nolan"
)

print("Movies created.")

# --- SHOWTIMES TEMPLATE ---
showtime_slots = [
    time(12, 30),
    time(15, 30),
    time(18, 30),
]

show_date = date.today()

# --- CREATE SHOWTIMES FOR EACH MOVIE ---

def create_showtimes(movie):
    created = []
    for t in showtime_slots:
        st = Showtime.objects.create(
            movie=movie,
            venue="Cinema 1",
            date=show_date,
            time=t,
            price=400
        )
        created.append(st)
    return created

white_showtimes = create_showtimes(white_chicks)
dark_showtimes = create_showtimes(dark_knight)

print("Showtimes created.")

# --- SEATS (A1–A10, B1–B10) ---
seat_labels = (
    [f"A{i}" for i in range(1, 11)] +
    [f"B{i}" for i in range(1, 11)]
)

def create_seats(showtime):
    for s in seat_labels:
        Seat.objects.create(
            showtime=showtime,
            seat_number=s,
            is_taken=False
        )

for st in white_showtimes + dark_showtimes:
    create_seats(st)

print("Seats generated for all showtimes.")
print("DATABASE SEEDING COMPLETE ✅")