import sqlite3
from datetime import datetime
from pathlib import Path
import uuid

DB_PATH = Path("club.db")


def _connect():
    return sqlite3.connect(DB_PATH)


def init_db():
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS members (
                id TEXT PRIMARY KEY,
                membership_number TEXT UNIQUE,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                status TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS guests (
                id TEXT PRIMARY KEY,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS visits (
                id TEXT PRIMARY KEY,
                member_id TEXT NOT NULL,
                guest_id TEXT NOT NULL,
                activity TEXT NOT NULL,
                visit_at TEXT NOT NULL,
                checked_in_by TEXT NOT NULL,
                notes TEXT,
                FOREIGN KEY(member_id) REFERENCES members(id),
                FOREIGN KEY(guest_id) REFERENCES guests(id)
            )
            """
        )


def seed_members_if_empty():
    with _connect() as conn:
        cursor = conn.execute("SELECT COUNT(*) FROM members")
        count = cursor.fetchone()[0]
        if count > 0:
            return
        sample = [
            (str(uuid.uuid4()), "1001", "Amina", "Khan", "amina@example.com", "555-0100", "active"),
            (str(uuid.uuid4()), "1002", "Liam", "Nguyen", "liam@example.com", "555-0101", "active"),
            (str(uuid.uuid4()), "1003", "Sofia", "Patel", "sofia@example.com", "555-0102", "suspended"),
        ]
        conn.executemany(
            """
            INSERT INTO members (id, membership_number, first_name, last_name, email, phone, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            sample,
        )


def search_member_by_number(membership_number):
    with _connect() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(
            "SELECT * FROM members WHERE membership_number = ?", (membership_number,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None


def search_members_by_last_name(last_name):
    return _search_members_by_name("last_name", last_name)


def search_members_by_first_name(first_name):
    return _search_members_by_name("first_name", first_name)


def _search_members_by_name(column, value):
    with _connect() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(
            f"SELECT * FROM members WHERE {column} LIKE ? ORDER BY last_name",
            (f"%{value}%",),
        )
        return [dict(row) for row in cursor.fetchall()]


def create_guest(first_name, last_name):
    guest_id = str(uuid.uuid4())
    created_at = datetime.now().isoformat(timespec="seconds")
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO guests (id, first_name, last_name, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (guest_id, first_name, last_name, created_at),
        )
    return guest_id


def create_visit(member_id, guest_id, activity, checked_in_by, notes=None):
    visit_id = str(uuid.uuid4())
    visit_at = datetime.now().isoformat(timespec="seconds")
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO visits (id, member_id, guest_id, activity, visit_at, checked_in_by, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (visit_id, member_id, guest_id, activity, visit_at, checked_in_by, notes),
        )


def count_monthly_visits(member_id, guest_first, guest_last, activity):
    current_month = datetime.now().strftime("%Y-%m")
    with _connect() as conn:
        cursor = conn.execute(
            """
            SELECT COUNT(*)
            FROM visits
            JOIN guests ON guests.id = visits.guest_id
            WHERE visits.member_id = ?
              AND guests.first_name = ?
              AND guests.last_name = ?
              AND visits.activity = ?
              AND visits.visit_at LIKE ?
            """,
            (member_id, guest_first, guest_last, activity, f"{current_month}%"),
        )
        return cursor.fetchone()[0]


def fetch_today_visits_by_activity(activity=None):
    today = datetime.now().strftime("%Y-%m-%d")
    with _connect() as conn:
        conn.row_factory = sqlite3.Row
        if activity:
            cursor = conn.execute(
                """
                SELECT visits.visit_at, visits.activity,
                       members.first_name || ' ' || members.last_name AS member_name,
                       guests.first_name || ' ' || guests.last_name AS guest_name
                FROM visits
                JOIN members ON members.id = visits.member_id
                JOIN guests ON guests.id = visits.guest_id
                WHERE visits.activity = ? AND visits.visit_at LIKE ?
                ORDER BY visits.visit_at DESC
                """,
                (activity, f"{today}%"),
            )
        else:
            cursor = conn.execute(
                """
                SELECT visits.visit_at, visits.activity,
                       members.first_name || ' ' || members.last_name AS member_name,
                       guests.first_name || ' ' || guests.last_name AS guest_name
                FROM visits
                JOIN members ON members.id = visits.member_id
                JOIN guests ON guests.id = visits.guest_id
                WHERE visits.visit_at LIKE ?
                ORDER BY visits.visit_at DESC
                """,
                (f"{today}%",),
            )
        return [dict(row) for row in cursor.fetchall()]
