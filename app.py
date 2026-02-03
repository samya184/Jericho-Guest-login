import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from pathlib import Path

from db import (
    init_db,
    seed_members_if_empty,
    search_member_by_number,
    search_members_by_last_name,
    search_members_by_first_name,
    create_guest,
    create_visit,
    count_monthly_visits,
    fetch_today_visits_by_activity,
)

ACTIVITIES = ["tennis", "squash", "swim", "socials"]
MONTHLY_LIMITS = {"tennis": 2, "squash": 2, "swim": 2, "socials": 4}


class GuestLoginApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Jericho Guest Login")
        self.geometry("980x640")
        self.resizable(False, False)

        init_db()
        seed_members_if_empty()

        self.selected_member = None

        self._build_layout()

    def _build_layout(self):
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=2)

        search_frame = ttk.LabelFrame(self, text="Member lookup")
        search_frame.grid(row=0, column=0, padx=12, pady=12, sticky="nsew")
        search_frame.columnconfigure(1, weight=1)

        ttk.Label(search_frame, text="Member number:").grid(row=0, column=0, sticky="w", padx=8, pady=6)
        self.member_number_var = tk.StringVar()
        member_entry = ttk.Entry(search_frame, textvariable=self.member_number_var)
        member_entry.grid(row=0, column=1, sticky="ew", padx=8, pady=6)
        member_entry.bind("<Return>", lambda _event: self.lookup_member())

        ttk.Label(search_frame, text="Last name:").grid(row=1, column=0, sticky="w", padx=8, pady=6)
        self.last_name_var = tk.StringVar()
        last_entry = ttk.Entry(search_frame, textvariable=self.last_name_var)
        last_entry.grid(row=1, column=1, sticky="ew", padx=8, pady=6)

        ttk.Label(search_frame, text="First name:").grid(row=2, column=0, sticky="w", padx=8, pady=6)
        self.first_name_var = tk.StringVar()
        first_entry = ttk.Entry(search_frame, textvariable=self.first_name_var)
        first_entry.grid(row=2, column=1, sticky="ew", padx=8, pady=6)

        ttk.Button(search_frame, text="Search", command=self.lookup_member).grid(
            row=3, column=1, sticky="e", padx=8, pady=8
        )

        self.results_list = tk.Listbox(search_frame, height=10)
        self.results_list.grid(row=4, column=0, columnspan=2, sticky="nsew", padx=8, pady=6)
        self.results_list.bind("<<ListboxSelect>>", self.on_member_select)

        side_frame = ttk.LabelFrame(self, text="Member details")
        side_frame.grid(row=0, column=1, padx=12, pady=12, sticky="nsew")
        side_frame.columnconfigure(1, weight=1)

        self.detail_vars = {
            "number": tk.StringVar(value="-") ,
            "name": tk.StringVar(value="-") ,
            "email": tk.StringVar(value="-") ,
            "status": tk.StringVar(value="-") ,
        }

        ttk.Label(side_frame, text="Member number:").grid(row=0, column=0, sticky="w", padx=8, pady=6)
        ttk.Label(side_frame, textvariable=self.detail_vars["number"]).grid(row=0, column=1, sticky="w", padx=8, pady=6)

        ttk.Label(side_frame, text="Name:").grid(row=1, column=0, sticky="w", padx=8, pady=6)
        ttk.Label(side_frame, textvariable=self.detail_vars["name"]).grid(row=1, column=1, sticky="w", padx=8, pady=6)

        ttk.Label(side_frame, text="Email:").grid(row=2, column=0, sticky="w", padx=8, pady=6)
        ttk.Label(side_frame, textvariable=self.detail_vars["email"]).grid(row=2, column=1, sticky="w", padx=8, pady=6)

        ttk.Label(side_frame, text="Status:").grid(row=3, column=0, sticky="w", padx=8, pady=6)
        ttk.Label(side_frame, textvariable=self.detail_vars["status"]).grid(row=3, column=1, sticky="w", padx=8, pady=6)

        ttk.Button(side_frame, text="Generate bill", command=self.generate_bill).grid(
            row=4, column=1, sticky="e", padx=8, pady=8
        )

        guest_frame = ttk.LabelFrame(self, text="Guest check-in")
        guest_frame.grid(row=1, column=0, padx=12, pady=0, sticky="nsew")
        guest_frame.columnconfigure(1, weight=1)

        ttk.Label(guest_frame, text="Guest first name:").grid(row=0, column=0, sticky="w", padx=8, pady=6)
        self.guest_first_var = tk.StringVar()
        ttk.Entry(guest_frame, textvariable=self.guest_first_var).grid(row=0, column=1, sticky="ew", padx=8, pady=6)

        ttk.Label(guest_frame, text="Guest last name:").grid(row=1, column=0, sticky="w", padx=8, pady=6)
        self.guest_last_var = tk.StringVar()
        ttk.Entry(guest_frame, textvariable=self.guest_last_var).grid(row=1, column=1, sticky="ew", padx=8, pady=6)

        ttk.Label(guest_frame, text="Activity:").grid(row=2, column=0, sticky="w", padx=8, pady=6)
        self.activity_var = tk.StringVar(value=ACTIVITIES[0])
        ttk.Combobox(guest_frame, values=ACTIVITIES, textvariable=self.activity_var, state="readonly").grid(
            row=2, column=1, sticky="w", padx=8, pady=6
        )

        ttk.Button(guest_frame, text="Check in guest", command=self.check_in_guest).grid(
            row=3, column=1, sticky="e", padx=8, pady=8
        )

        report_frame = ttk.LabelFrame(self, text="Daily receipts")
        report_frame.grid(row=1, column=1, padx=12, pady=0, sticky="nsew")
        report_frame.columnconfigure(0, weight=1)

        ttk.Label(report_frame, text="Print today by activity:").grid(row=0, column=0, sticky="w", padx=8, pady=6)
        self.receipt_activity_var = tk.StringVar(value="all")
        receipt_choices = ["all"] + ACTIVITIES
        ttk.Combobox(report_frame, values=receipt_choices, textvariable=self.receipt_activity_var, state="readonly").grid(
            row=1, column=0, sticky="w", padx=8, pady=6
        )
        ttk.Button(report_frame, text="Print receipt", command=self.print_receipt).grid(
            row=2, column=0, sticky="w", padx=8, pady=8
        )

    def lookup_member(self):
        self.results_list.delete(0, tk.END)
        self.selected_member = None
        self._clear_member_details()

        number = self.member_number_var.get().strip()
        last_name = self.last_name_var.get().strip()
        first_name = self.first_name_var.get().strip()

        results = []
        if number:
            member = search_member_by_number(number)
            if member:
                results = [member]
        elif last_name:
            results = search_members_by_last_name(last_name)
        elif first_name:
            results = search_members_by_first_name(first_name)

        for member in results:
            display = f"{member['membership_number']} - {member['first_name']} {member['last_name']}"
            self.results_list.insert(tk.END, display)

        if not results:
            messagebox.showinfo("No results", "No members found. Try another search.")

    def on_member_select(self, _event):
        if not self.results_list.curselection():
            return
        selection = self.results_list.get(self.results_list.curselection()[0])
        member_number = selection.split(" - ")[0]
        member = search_member_by_number(member_number)
        if member:
            self.selected_member = member
            self.detail_vars["number"].set(member["membership_number"])
            self.detail_vars["name"].set(f"{member['first_name']} {member['last_name']}")
            self.detail_vars["email"].set(member["email"] or "-")
            self.detail_vars["status"].set(member["status"])

    def check_in_guest(self):
        if not self.selected_member:
            messagebox.showwarning("Select member", "Please select a member first.")
            return

        guest_first = self.guest_first_var.get().strip()
        guest_last = self.guest_last_var.get().strip()
        activity = self.activity_var.get().strip()

        if not guest_first or not guest_last:
            messagebox.showwarning("Missing guest details", "Guest first and last name are required.")
            return

        monthly_visits = count_monthly_visits(
            member_id=self.selected_member["id"],
            guest_first=guest_first,
            guest_last=guest_last,
            activity=activity,
        )
        limit = MONTHLY_LIMITS.get(activity, 0)

        if limit and monthly_visits >= limit:
            messagebox.showwarning(
                "Limit reached",
                f"This guest has already visited {monthly_visits} time(s) this month for {activity}.",
            )
            return

        guest_id = create_guest(guest_first, guest_last)
        create_visit(
            member_id=self.selected_member["id"],
            guest_id=guest_id,
            activity=activity,
            checked_in_by="reception",
        )

        messagebox.showinfo("Checked in", "Guest check-in recorded.")
        self.guest_first_var.set("")
        self.guest_last_var.set("")

    def generate_bill(self):
        if not self.selected_member:
            messagebox.showwarning("Select member", "Please select a member first.")
            return
        messagebox.showinfo("Generate bill", "Billing flow coming soon.")

    def print_receipt(self):
        activity = self.receipt_activity_var.get()
        visits = fetch_today_visits_by_activity(activity if activity != "all" else None)
        if not visits:
            messagebox.showinfo("No visits", "No guest visits found for today.")
            return

        today = datetime.now().strftime("%Y-%m-%d")
        label = activity if activity != "all" else "all"
        output_dir = Path("receipts")
        output_dir.mkdir(exist_ok=True)
        filename = output_dir / f"{today}_{label}.txt"

        lines = [f"Jericho Guest Receipt ({today}) - {label}\n"]
        for visit in visits:
            lines.append(
                f"{visit['visit_at']} | {visit['activity']} | {visit['member_name']} | {visit['guest_name']}"
            )

        filename.write_text("\n".join(lines))
        messagebox.showinfo("Receipt saved", f"Saved to {filename}")

    def _clear_member_details(self):
        for key in self.detail_vars:
            self.detail_vars[key].set("-")


if __name__ == "__main__":
    app = GuestLoginApp()
    app.mainloop()
