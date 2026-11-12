
from flask import Flask, render_template, request
import sqlite3
from pathlib import Path

app = Flask(__name__)

DB_PATH = Path(__file__).with_name("routes.db")


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/", methods=["GET"])
def index():
    start = request.args.get("start", "")
    end = request.args.get("end", "")

    conn = get_db_connection()

    stations = conn.execute("""
        SELECT station FROM (
            SELECT start_station AS station FROM routes
            UNION
            SELECT end_station AS station FROM routes
        )
        WHERE station != ''
        ORDER BY station
    """).fetchall()

    results = []

    if start:
        destinations = conn.execute("""
            SELECT DISTINCT end_station
            FROM routes
            WHERE start_station = ?
            AND end_station != ''
            ORDER BY end_station
        """, (start,)).fetchall()
    else:
        destinations = conn.execute("""
            SELECT DISTINCT end_station
            FROM routes
            WHERE end_station != ''
            ORDER BY end_station
        """).fetchall()

    if start or end:
        query = "SELECT * FROM routes WHERE 1=1"
        params = []

        if start:
            query += " AND start_station = ?"
            params.append(start)

        if end:
            query += " AND end_station = ?"
            params.append(end)

        results = conn.execute(query, params).fetchall()

    conn.close()

    return render_template(
        "index.html",
        stations=[row["station"] for row in stations],
        destinations=[row["end_station"] for row in destinations],
        results=results,
        start=start,
        end=end
    )


if __name__ == "__main__":
    app.run(debug=True)
