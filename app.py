from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from math import radians, cos, sin, sqrt, atan2

app = Flask(__name__)
DB = "trips.db"

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS trips (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, motorcycle TEXT NOT NULL, description TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS trip_points (id INTEGER PRIMARY KEY AUTOINCREMENT, trip_id INTEGER NOT NULL, latitude REAL NOT NULL, longitude REAL NOT NULL, note TEXT, FOREIGN KEY(trip_id) REFERENCES trips(id))")
    conn.commit()
    conn.close()

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

@app.route("/")
def dashboard():
    conn = sqlite3.connect(DB)
    trips = conn.execute("SELECT * FROM trips").fetchall()
    conn.close()
    return render_template("dashboard.html", trips=trips)

@app.route("/trip/<int:trip_id>")
def trip_detail(trip_id):
    conn = sqlite3.connect(DB)
    trip = conn.execute("SELECT * FROM trips WHERE id = ?", (trip_id,)).fetchone()
    points = conn.execute("SELECT * FROM trip_points WHERE trip_id = ?", (trip_id,)).fetchall()
    conn.close()
    distance = 0.0
    for i in range(1, len(points)):
        distance += haversine(points[i-1][2], points[i-1][3], points[i][2], points[i][3])
    return render_template("trip_detail.html", trip=trip, points=points, distance=round(distance, 2))

@app.route("/trip/new", methods=["POST"])
def new_trip():
    title = request.form["title"]
    motorcycle = request.form["motorcycle"]
    description = request.form["description"]
    conn = sqlite3.connect(DB)
    conn.execute("INSERT INTO trips (title, motorcycle, description) VALUES (?, ?, ?)", (title, motorcycle, description))
    conn.commit()
    conn.close()
    return redirect(url_for("dashboard"))

@app.route("/trip/<int:trip_id>/add_point", methods=["POST"])
def add_point(trip_id):
    coords = request.form["coords"]
    note = request.form["note"]
    lat, lon = map(float, coords.split(","))
    conn = sqlite3.connect(DB)
    conn.execute("INSERT INTO trip_points (trip_id, latitude, longitude, note) VALUES (?, ?, ?, ?)", (trip_id, lat, lon, note))
    conn.commit()
    conn.close()
    return redirect(url_for("trip_detail", trip_id=trip_id))

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=8080)