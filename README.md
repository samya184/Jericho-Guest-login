# Jericho Guest Login

Guest sign-in application for a multi-sport club (tennis, squash, swim, socials). The app is designed for reception teams to quickly find members, record guest visits, and print guest passes.

## Quick start (Windows)

1. Make sure you have Python 3.11+ installed.
2. Open a terminal in this folder.
3. Run the app:

```bash
python app.py
```

The app will create a local `club.db` file and seed a few sample members for testing.

## Core goals

- Fast member lookup at reception (name, membership number, phone, email).
- Quick guest check-in with minimal data entry.
- Printable guest passes with visit details.
- Searchable visit history for audits and reporting.

## Primary users

- **Reception staff**: sign guests in, print passes, and review recent visits.
- **Club members**: optionally pre-register guests (future enhancement).
- **Club admins**: run reports and manage member records.

## Key workflows

### 1) Guest sign-in at reception
1. Search for member by name or membership number.
2. Select the member and confirm membership status.
3. Add guest details (first name, last name, activity, date/time, optional notes).
4. Print guest pass (includes member name, guest name, activity, and timestamp).
5. Save visit record for audit/search.

### 2) Member lookup
- Search by membership number (fastest).
- If the member number is unknown, search by last name.
- If last name is unknown, search by first name.
- Optional: search by phone or email when available.
- Filter by membership type (tennis, squash, swim, socials, multi-sport).
- Quick view of active status and recent visits.

### 3) Visit history
- Filter by date range, member, activity, or staff user.
- Export/print a daily or monthly report.

## Data model (initial draft)

### Member
- `id` (uuid)
- `membership_number`
- `first_name`
- `last_name`
- `email`
- `phone`
- `membership_types` (array: tennis, squash, swim, socials)
- `status` (active, suspended, expired)
- `created_at`
- `updated_at`

### Guest
- `id` (uuid)
- `first_name`
- `last_name`
- `created_at`
- `updated_at`

### Visit
- `id` (uuid)
- `member_id`
- `guest_id`
- `activity` (tennis, squash, swim, socials)
- `visit_at` (timestamp)
- `checked_in_by` (staff user id)
- `notes` (optional)

## Guest visit rules

- Required guest fields: first name, last name, and activity (tennis, squash, swim, or socials).
- Limit by member per guest:
  - **Tennis, squash, swim**: no more than 2 visits per month.
  - **Socials**: no more than 4 visits per month.

### StaffUser
- `id` (uuid)
- `first_name`
- `last_name`
- `email`
- `role` (reception, manager, admin)
- `active`

## Reports & printing

- **Guest pass**: printable ticket with club logo, guest name, host member, activity, date/time, and a QR code (future enhancement).
- **Daily guest log**: counts by activity, with staff member who checked them in.
- **Daily activity receipt**: print today’s guests by activity (tennis, squash, swim, socials) or all combined.

## Next steps

- Confirm whether any additional guest fields are required beyond first/last name and activity.
- Implement staff-only authentication (reception users sign in with staff accounts).
- Choose a Windows-friendly stack (see recommendations below) and plan for an installed desktop app backed by SQL.
- Define the reception UI: the primary sign-in screen optimized for speed (keyboard shortcuts, barcode scans, and quick search).

## Recommended tech stack (for Windows)

Since you already know **Java**, **C++**, and **Python**, the easiest path is:

- **Python + Tkinter (UI) + SQLite (database)** for a first version.
  - Fast to build and beginner-friendly.
  - SQLite stores everything in a local file (easy backups).
  - You can later migrate to SQL Server or PostgreSQL if needed.

If you want a more “enterprise” Windows stack later:

- **Java + JavaFX (UI) + SQLite or SQL Server**.

## Reception UI behavior (draft)

- Primary search field for **member number**; pressing Enter fetches the member.
- If the member number is not found, fallback search in **last name** or **first name** columns.
- When a member is selected, show a side panel with **member number, name, email, status**.
- Provide actions for **generate bill** and **print today’s receipts** by activity or for all guests.
