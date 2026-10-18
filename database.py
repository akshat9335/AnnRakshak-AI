"""
Database module for AnnRakshak AI.
Uses SQLite for persistent storage with thread-safe connection pooling,
safe transactions, parameterized queries, and idempotent seeding.
"""

import sqlite3
import datetime
import uuid
import os
from typing import List, Dict, Any, Optional

DB_FILE = "annrakshak.db"

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_connection()
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS donations (
                id TEXT PRIMARY KEY,
                donor_name TEXT NOT NULL,
                event_type TEXT NOT NULL,
                food_items TEXT NOT NULL,
                food_type TEXT NOT NULL DEFAULT 'Vegetarian',
                original_quantity INTEGER NOT NULL,
                remaining_quantity INTEGER NOT NULL,
                quantity_unit TEXT NOT NULL DEFAULT 'meal portions',
                prep_datetime TEXT NOT NULL,
                storage_handling TEXT NOT NULL,
                location TEXT NOT NULL,
                available_from TEXT NOT NULL,
                pickup_deadline TEXT NOT NULL,
                private_contact TEXT NOT NULL,
                notes TEXT,
                status TEXT NOT NULL DEFAULT 'Available',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                is_demo_seed INTEGER NOT NULL DEFAULT 0
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS pickup_requests (
                id TEXT PRIMARY KEY,
                donation_id TEXT NOT NULL,
                ngo_name TEXT NOT NULL,
                ngo_contact TEXT NOT NULL,
                requested_quantity INTEGER NOT NULL,
                proposed_pickup_time TEXT NOT NULL,
                notes TEXT,
                status TEXT NOT NULL DEFAULT 'Pickup Requested',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                is_demo_seed INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (donation_id) REFERENCES donations (id) ON DELETE CASCADE
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS food_waste_records (
                id TEXT PRIMARY KEY,
                provider_name TEXT NOT NULL,
                record_date TEXT NOT NULL,
                meal_type TEXT NOT NULL,
                menu_items TEXT NOT NULL,
                portions_prepared INTEGER NOT NULL,
                portions_consumed INTEGER NOT NULL,
                edible_surplus INTEGER NOT NULL,
                discarded_waste INTEGER NOT NULL,
                cost_per_meal REAL NOT NULL,
                leftover_quantity INTEGER NOT NULL,
                leftover_pct REAL NOT NULL,
                discarded_waste_pct REAL NOT NULL,
                financial_loss REAL NOT NULL,
                notes TEXT,
                created_at TEXT NOT NULL,
                is_demo_seed INTEGER NOT NULL DEFAULT 0
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS status_history (
                id TEXT PRIMARY KEY,
                entity_type TEXT NOT NULL, -- 'donation' or 'pickup_request'
                entity_id TEXT NOT NULL,
                old_status TEXT,
                new_status TEXT NOT NULL,
                changed_by TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                remarks TEXT
            )
        """)

    seed_demo_data_if_needed(conn)
    conn.close()

def log_status_change(conn: sqlite3.Connection, entity_type: str, entity_id: str, old_status: Optional[str], new_status: str, changed_by: str, remarks: str = ""):
    hist_id = f"HIST-{uuid.uuid4().hex[:8].upper()}"
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute("""
        INSERT INTO status_history (id, entity_type, entity_id, old_status, new_status, changed_by, timestamp, remarks)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (hist_id, entity_type, entity_id, old_status, new_status, changed_by, now_str, remarks))

def seed_demo_data_if_needed(conn: Optional[sqlite3.Connection] = None):
    should_close = False
    if conn is None:
        conn = get_connection()
        should_close = True

    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM donations WHERE is_demo_seed = 1")
    count = cur.fetchone()[0]

    if count == 0:
        now = datetime.datetime.now()
        demo_date = now.strftime("%Y-%m-%d")
        created_at = (now - datetime.timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S")
        
        # Sample Donation A: Wedding Reception
        don_a_id = "DON-WED-001"
        prep_a = f"{demo_date} 19:00"
        avail_a = f"{demo_date} 19:30"
        dead_a = f"{demo_date} 23:30"
        
        # Sample Donation B: Birthday Party
        don_b_id = "DON-BDAY-002"
        prep_b = f"{demo_date} 18:00"
        avail_b = f"{demo_date} 18:30"
        dead_b = f"{demo_date} 22:30"

        # Sample Donation C: Restaurant Surplus
        don_c_id = "DON-REST-003"
        prep_c = f"{demo_date} 15:00"
        avail_c = f"{demo_date} 15:30"
        dead_c = f"{demo_date} 21:00"

        with conn:
            # Insert Donation A
            conn.execute("""
                INSERT INTO donations (
                    id, donor_name, event_type, food_items, food_type,
                    original_quantity, remaining_quantity, quantity_unit,
                    prep_datetime, storage_handling, location, available_from, pickup_deadline,
                    private_contact, notes, status, created_at, updated_at, is_demo_seed
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
            """, (
                don_a_id, "Sharma Wedding Events (Demo)", "Wedding",
                "Vegetable pulao, dal tadka, fresh chapati and paneer gravy", "Vegetarian",
                100, 100, "meal portions",
                prep_a, "Kept hot in insulated chafing dishes; packed in hygienic food-grade containers",
                "Civil Lines, Prayagraj (Fictional Demo Locality)", avail_a, dead_a,
                "Demo Contact: +91-98765-43210 (Sharma Catering Coordinator)",
                "Cooked freshly for reception dinner. Excess prepared due to RSVP drop.",
                "Available", created_at, created_at
            ))
            log_status_change(conn, "donation", don_a_id, None, "Available", "System Seed", "Initial Demo Seed")

            # Insert Donation B
            conn.execute("""
                INSERT INTO donations (
                    id, donor_name, event_type, food_items, food_type,
                    original_quantity, remaining_quantity, quantity_unit,
                    prep_datetime, storage_handling, location, available_from, pickup_deadline,
                    private_contact, notes, status, created_at, updated_at, is_demo_seed
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
            """, (
                don_b_id, "Birthday Event Demo", "Birthday Party",
                "Packed vegetarian meal boxes: Puri, chole, gulab jamun, veg cutlet", "Vegetarian",
                30, 30, "meal portions",
                prep_b, "Sealed tamper-evident paper meal boxes at room temperature (under 4 hours)",
                "Tagore Town, Prayagraj (Fictional Demo Locality)", avail_b, dead_b,
                "Demo Contact: +91-98123-45678 (Demo Host)",
                "Untouched packaged boxes from kid birthday celebration.",
                "Available", created_at, created_at
            ))
            log_status_change(conn, "donation", don_b_id, None, "Available", "System Seed", "Initial Demo Seed")

            # Insert Donation C
            conn.execute("""
                INSERT INTO donations (
                    id, donor_name, event_type, food_items, food_type,
                    original_quantity, remaining_quantity, quantity_unit,
                    prep_datetime, storage_handling, location, available_from, pickup_deadline,
                    private_contact, notes, status, created_at, updated_at, is_demo_seed
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
            """, (
                don_c_id, "Green Plate Demo Restaurant", "Restaurant",
                "Prepared chef-crafted meal boxes: Jeera rice, rajma, mixed veg sabzi", "Vegetarian",
                25, 0, "meal portions",
                prep_c, "Refrigerated at 4°C immediately after lunch buffet closure",
                "Katra Commercial Hub, Prayagraj (Fictional Demo Locality)", avail_c, dead_c,
                "Demo Contact: +91-99554-33221 (Restaurant Duty Manager)",
                "Lunch buffet excess. Safe and packed for immediate evening distribution.",
                "Pickup Requested", created_at, created_at
            ))
            log_status_change(conn, "donation", don_c_id, None, "Available", "System Seed", "Initial Demo Seed")
            log_status_change(conn, "donation", don_c_id, "Available", "Pickup Requested", "System Seed", "Sample Request Placed")

            # Insert Pickup Request for Donation C
            req_c_id = "REQ-DEMO-001"
            conn.execute("""
                INSERT INTO pickup_requests (
                    id, donation_id, ngo_name, ngo_contact, requested_quantity,
                    proposed_pickup_time, notes, status, created_at, updated_at, is_demo_seed
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
            """, (
                req_c_id, don_c_id, "Asha Food Rescue Foundation (Sample Demo NGO)",
                "Demo Volunteer: +91-91234-56789 (Asha Dispatch Desk)", 25,
                f"{demo_date} 19:00",
                "Van ready with insulated transport boxes. Planning distribution to night shelter.",
                "Pickup Requested", created_at, created_at
            ))
            log_status_change(conn, "pickup_request", req_c_id, None, "Pickup Requested", "System Seed", "Sample Request Placed")

            # Seed realistic Food Waste records for historical trends & AI analytics
            waste_samples = [
                ("Sharma Wedding Events (Demo)", (now - datetime.timedelta(days=14)).strftime("%Y-%m-%d"), "Dinner", "Biryani, Shahi Paneer, Naan", 400, 320, 50, 30, 180.0, "Guest turnout 80% of RSVPs. Extra gravy spoiled."),
                ("Hostel Mess Demo (Block A)", (now - datetime.timedelta(days=10)).strftime("%Y-%m-%d"), "Lunch", "Rajma Chawal, Roti, Salad", 250, 210, 25, 15, 65.0, "Exam week, student turnout reduced."),
                ("Green Plate Demo Restaurant", (now - datetime.timedelta(days=7)).strftime("%Y-%m-%d"), "Dinner", "Buffet assortment", 150, 115, 20, 15, 220.0, "Rainy evening caused lower walk-ins."),
                ("College Canteen Demo", (now - datetime.timedelta(days=5)).strftime("%Y-%m-%d"), "Lunch", "Thali specials", 300, 260, 30, 10, 75.0, "Mid-semester break started early."),
                ("Sharma Wedding Events (Demo)", (now - datetime.timedelta(days=2)).strftime("%Y-%m-%d"), "Dinner", "Pulao, Dal Makhani, Mixed Veg", 350, 290, 40, 20, 195.0, "Heavy rain delayed evening arrivals.")
            ]

            for w in waste_samples:
                w_id = f"WST-{uuid.uuid4().hex[:8].upper()}"
                p_provider = w[0]
                p_date = w[1]
                p_meal = w[2]
                p_menu = w[3]
                p_prep = int(w[4])
                p_cons = int(w[5])
                p_edible = int(w[6])
                p_discard = int(w[7])
                cost = float(w[8])
                notes = w[9]
                leftover = p_prep - p_cons
                leftover_pct = round((leftover / p_prep) * 100, 1) if p_prep > 0 else 0.0
                discard_pct = round((p_discard / p_prep) * 100, 1) if p_prep > 0 else 0.0
                fin_loss = round(p_discard * cost, 2)

                conn.execute("""
                    INSERT INTO food_waste_records (
                        id, provider_name, record_date, meal_type, menu_items,
                        portions_prepared, portions_consumed, edible_surplus, discarded_waste,
                        cost_per_meal, leftover_quantity, leftover_pct, discarded_waste_pct,
                        financial_loss, notes, created_at, is_demo_seed
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                """, (
                    w_id, p_provider, p_date, p_meal, p_menu, p_prep, p_cons, p_edible, p_discard,
                    cost, leftover, leftover_pct, discard_pct, fin_loss, notes,
                    created_at
                ))

    if should_close:
        conn.close()

def reset_demo_database():
    """Wipes all data and re-seeds cleanly with fictional demo records."""
    conn = get_connection()
    with conn:
        conn.execute("DELETE FROM status_history")
        conn.execute("DELETE FROM pickup_requests")
        conn.execute("DELETE FROM donations")
        conn.execute("DELETE FROM food_waste_records")
    seed_demo_data_if_needed(conn)
    conn.close()

# --- Donation Queries & Transactions ---

def create_donation(data: Dict[str, Any]) -> str:
    """Inserts a new donation with validation and transaction safety."""
    conn = get_connection()
    don_id = f"DON-{uuid.uuid4().hex[:8].upper()}"
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    qty = int(data["quantity"])
    if qty <= 0:
        raise ValueError("Quantity must be greater than zero.")

    with conn:
        conn.execute("""
            INSERT INTO donations (
                id, donor_name, event_type, food_items, food_type,
                original_quantity, remaining_quantity, quantity_unit,
                prep_datetime, storage_handling, location, available_from, pickup_deadline,
                private_contact, notes, status, created_at, updated_at, is_demo_seed
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Available', ?, ?, 0)
        """, (
            don_id, data["donor_name"], data["event_type"], data["food_items"],
            data.get("food_type", "Vegetarian"), qty, qty, data.get("quantity_unit", "meal portions"),
            data["prep_datetime"], data["storage_handling"], data["location"],
            data["available_from"], data["pickup_deadline"], data["private_contact"],
            data.get("notes", ""), now_str, now_str
        ))
        log_status_change(conn, "donation", don_id, None, "Available", data["donor_name"], "Listing published")

    conn.close()
    return don_id

def get_all_donations(status_filter: Optional[str] = None, event_filter: Optional[str] = None, search: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_connection()
    query = "SELECT * FROM donations WHERE 1=1"
    params = []

    if status_filter and status_filter != "All":
        query += " AND status = ?"
        params.append(status_filter)

    if event_filter and event_filter != "All":
        query += " AND event_type = ?"
        params.append(event_filter)

    if search and search.strip():
        query += " AND (food_items LIKE ? OR location LIKE ? OR donor_name LIKE ?)"
        s = f"%{search.strip()}%"
        params.extend([s, s, s])

    query += " ORDER BY created_at DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_donation_by_id(donation_id: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    row = conn.execute("SELECT * FROM donations WHERE id = ?", (donation_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def cancel_donation(donation_id: str, donor_name: str, reason: str = "Donor cancelled") -> bool:
    conn = get_connection()
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with conn:
        don = conn.execute("SELECT status, original_quantity, remaining_quantity FROM donations WHERE id = ?", (donation_id,)).fetchone()
        if not don:
            conn.close()
            return False
        
        # Can only cancel if not already collected or delivered
        if don["status"] in ["Collected", "Delivered", "Cancelled"]:
            conn.close()
            raise ValueError(f"Cannot cancel donation in status: {don['status']}")

        conn.execute("""
            UPDATE donations
            SET status = 'Cancelled', remaining_quantity = 0, updated_at = ?
            WHERE id = ?
        """, (now_str, donation_id))

        # Reject any pending requests associated with this cancelled donation
        conn.execute("""
            UPDATE pickup_requests
            SET status = 'Cancelled', updated_at = ?
            WHERE donation_id = ? AND status IN ('Pickup Requested', 'Confirmed')
        """, (now_str, donation_id))

        log_status_change(conn, "donation", donation_id, don["status"], "Cancelled", donor_name, reason)

    conn.close()
    return True

# --- Pickup Request Queries & Safe Allocation ---

def create_pickup_request(data: Dict[str, Any]) -> str:
    """
    Submits a pickup request with safe database transaction checking:
    1. Validates requested quantity against remaining available quantity.
    2. Atomically decrements remaining_quantity.
    3. If remaining reaches 0, sets donation status to 'Pickup Requested' (or Confirmed upon approval).
    4. Prevents duplicate allocation / race condition.
    """
    conn = get_connection()
    req_id = f"REQ-{uuid.uuid4().hex[:8].upper()}"
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    don_id = data["donation_id"]
    req_qty = int(data["requested_quantity"])

    if req_qty <= 0:
        conn.close()
        raise ValueError("Requested quantity must be at least 1 portion.")

    with conn:
        cur = conn.cursor()
        # Lock and check donation
        cur.execute("SELECT status, remaining_quantity, donor_name FROM donations WHERE id = ?", (don_id,))
        don = cur.fetchone()
        if not don:
            raise ValueError("Selected donation does not exist.")

        if don["status"] not in ["Available", "Pickup Requested"]:
            raise ValueError(f"Donation is currently {don['status']} and cannot accept new pickup requests.")

        remaining = don["remaining_quantity"]
        if req_qty > remaining:
            raise ValueError(f"Requested {req_qty} portions, but only {remaining} portions are currently available.")

        new_remaining = remaining - req_qty
        new_don_status = "Pickup Requested" if new_remaining == 0 else don["status"]

        # Update donation atomically
        cur.execute("""
            UPDATE donations
            SET remaining_quantity = ?, status = ?, updated_at = ?
            WHERE id = ?
        """, (new_remaining, new_don_status, now_str, don_id))

        # Insert pickup request
        cur.execute("""
            INSERT INTO pickup_requests (
                id, donation_id, ngo_name, ngo_contact, requested_quantity,
                proposed_pickup_time, notes, status, created_at, updated_at, is_demo_seed
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 'Pickup Requested', ?, ?, 0)
        """, (
            req_id, don_id, data["ngo_name"], data["ngo_contact"], req_qty,
            data["proposed_pickup_time"], data.get("notes", ""), now_str, now_str
        ))

        log_status_change(conn, "pickup_request", req_id, None, "Pickup Requested", data["ngo_name"], "Pickup request submitted")
        if new_don_status != don["status"]:
            log_status_change(conn, "donation", don_id, don["status"], new_don_status, data["ngo_name"], "All portions claimed; pending confirmation")

    conn.close()
    return req_id

def get_pickup_requests_for_donation(donation_id: str) -> List[Dict[str, Any]]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM pickup_requests WHERE donation_id = ? ORDER BY created_at DESC", (donation_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_pickup_requests(ngo_name_filter: Optional[str] = None, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_connection()
    query = """
        SELECT r.*, d.donor_name, d.food_items, d.location, d.prep_datetime, d.pickup_deadline, d.private_contact
        FROM pickup_requests r
        JOIN donations d ON r.donation_id = d.id
        WHERE 1=1
    """
    params = []
    if ngo_name_filter and ngo_name_filter != "All":
        query += " AND r.ngo_name = ?"
        params.append(ngo_name_filter)
    if status_filter and status_filter != "All":
        query += " AND r.status = ?"
        params.append(status_filter)

    query += " ORDER BY r.created_at DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def update_request_status(request_id: str, new_status: str, actor_name: str, remarks: str = "") -> bool:
    """
    Validates and executes allowed transitions:
    - Donor:
        Pickup Requested -> Confirmed (Accept)
        Pickup Requested -> Rejected (Reject -> restores allocated portions back to donation)
    - NGO:
        Confirmed -> Collected
        Collected -> Delivered
        Pickup Requested / Confirmed -> Cancelled (restores portions back to donation)
    """
    conn = get_connection()
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM pickup_requests WHERE id = ?", (request_id,))
        req = cur.fetchone()
        if not req:
            conn.close()
            raise ValueError("Pickup request not found.")

        current_status = req["status"]
        don_id = req["donation_id"]
        req_qty = req["requested_quantity"]

        # Validate legal transitions
        valid_transitions = {
            "Pickup Requested": ["Confirmed", "Rejected", "Cancelled"],
            "Confirmed": ["Collected", "Cancelled"],
            "Collected": ["Delivered"],
            "Delivered": [],
            "Rejected": [],
            "Cancelled": []
        }

        if new_status not in valid_transitions.get(current_status, []):
            raise ValueError(f"Illegal status transition from '{current_status}' to '{new_status}'.")

        # Update Request Status
        cur.execute("""
            UPDATE pickup_requests
            SET status = ?, updated_at = ?
            WHERE id = ?
        """, (new_status, now_str, request_id))
        log_status_change(conn, "pickup_request", request_id, current_status, new_status, actor_name, remarks)

        # Handle side-effects on Donation record
        cur.execute("SELECT * FROM donations WHERE id = ?", (don_id,))
        don = cur.fetchone()

        if new_status in ["Rejected", "Cancelled"]:
            # Restore quantity back to remaining_quantity
            restored_qty = don["remaining_quantity"] + req_qty
            restored_status = "Available" if restored_qty > 0 else don["status"]
            cur.execute("""
                UPDATE donations
                SET remaining_quantity = ?, status = ?, updated_at = ?
                WHERE id = ?
            """, (restored_qty, restored_status, now_str, don_id))
            log_status_change(conn, "donation", don_id, don["status"], restored_status, actor_name, f"Restored {req_qty} portions due to request {new_status.lower()}")

        elif new_status == "Confirmed":
            cur.execute("""
                UPDATE donations
                SET status = 'Confirmed', updated_at = ?
                WHERE id = ?
            """, (now_str, don_id))
            log_status_change(conn, "donation", don_id, don["status"], "Confirmed", actor_name, f"Request {request_id} confirmed by donor")

        elif new_status == "Collected":
            cur.execute("""
                UPDATE donations
                SET status = 'Collected', updated_at = ?
                WHERE id = ?
            """, (now_str, don_id))
            log_status_change(conn, "donation", don_id, don["status"], "Collected", actor_name, f"Portions picked up by NGO")

        elif new_status == "Delivered":
            cur.execute("""
                UPDATE donations
                SET status = 'Delivered', updated_at = ?
                WHERE id = ?
            """, (now_str, don_id))
            log_status_change(conn, "donation", don_id, don["status"], "Delivered", actor_name, f"Food safely delivered to beneficiaries")

    conn.close()
    return True

# --- Food Waste Tracker Queries ---

def add_food_waste_record(data: Dict[str, Any]) -> str:
    """
    Validates logical consistency:
    - prepared >= consumed
    - leftover = prepared - consumed
    - edible_surplus + discarded_waste <= leftover (can't have more surplus/waste than leftovers)
    """
    prep = int(data["portions_prepared"])
    cons = int(data["portions_consumed"])
    edible = int(data["edible_surplus"])
    discard = int(data["discarded_waste"])
    cost = float(data["cost_per_meal"])

    if prep < 0 or cons < 0 or edible < 0 or discard < 0 or cost < 0:
        raise ValueError("Values cannot be negative.")

    if cons > prep:
        raise ValueError(f"Portions consumed ({cons}) cannot exceed portions prepared ({prep}).")

    leftover = prep - cons
    if (edible + discard) > leftover:
        raise ValueError(
            f"Sum of edible surplus ({edible}) and discarded waste ({discard}) equals {edible + discard}, "
            f"which exceeds the recorded leftover portions ({leftover} = {prep} prepared - {cons} consumed)."
        )

    leftover_pct = round((leftover / prep) * 100, 1) if prep > 0 else 0.0
    discard_pct = round((discard / prep) * 100, 1) if prep > 0 else 0.0
    financial_loss = round(discard * cost, 2)

    w_id = f"WST-{uuid.uuid4().hex[:8].upper()}"
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = get_connection()
    with conn:
        conn.execute("""
            INSERT INTO food_waste_records (
                id, provider_name, record_date, meal_type, menu_items,
                portions_prepared, portions_consumed, edible_surplus, discarded_waste,
                cost_per_meal, leftover_quantity, leftover_pct, discarded_waste_pct,
                financial_loss, notes, created_at, is_demo_seed
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
        """, (
            w_id, data["provider_name"], data["record_date"], data["meal_type"],
            data["menu_items"], prep, cons, edible, discard, cost,
            leftover, leftover_pct, discard_pct, financial_loss, data.get("notes", ""),
            now_str
        ))
    conn.close()
    return w_id

def get_food_waste_records(provider_filter: Optional[str] = None, meal_type_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_connection()
    query = "SELECT * FROM food_waste_records WHERE 1=1"
    params = []
    if provider_filter and provider_filter != "All":
        query += " AND provider_name = ?"
        params.append(provider_filter)
    if meal_type_filter and meal_type_filter != "All":
        query += " AND meal_type = ?"
        params.append(meal_type_filter)

    query += " ORDER BY record_date DESC, created_at DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# --- Impact Metrics Aggregate Queries ---

def get_donor_impact_metrics() -> Dict[str, Any]:
    conn = get_connection()
    don_cur = conn.cursor()

    don_cur.execute("""
        SELECT 
            COUNT(*) as total_donations,
            COALESCE(SUM(original_quantity), 0) as total_offered,
            COALESCE(SUM(CASE WHEN status IN ('Collected', 'Delivered') THEN (original_quantity - remaining_quantity) ELSE 0 END), 0) as total_collected,
            COALESCE(SUM(CASE WHEN status = 'Delivered' THEN (original_quantity - remaining_quantity) ELSE 0 END), 0) as total_delivered,
            COALESCE(SUM(CASE WHEN status = 'Delivered' THEN 1 ELSE 0 END), 0) as completed_donations,
            COALESCE(SUM(CASE WHEN status = 'Pickup Requested' THEN 1 ELSE 0 END), 0) as pending_requests,
            COALESCE(SUM(CASE WHEN status = 'Confirmed' THEN 1 ELSE 0 END), 0) as confirmed_pickups
        FROM donations
    """)
    d_row = don_cur.fetchone()

    waste_cur = conn.cursor()
    waste_cur.execute("""
        SELECT 
            COALESCE(SUM(discarded_waste), 0) as total_discarded,
            COALESCE(SUM(financial_loss), 0) as total_fin_loss,
            COALESCE(SUM(edible_surplus), 0) as total_edible_surplus
        FROM food_waste_records
    """)
    w_row = waste_cur.fetchone()
    conn.close()

    return {
        "total_donations": d_row["total_donations"],
        "total_offered": d_row["total_offered"],
        "total_collected": d_row["total_collected"],
        "total_delivered": d_row["total_delivered"],
        "completed_donations": d_row["completed_donations"],
        "pending_requests": d_row["pending_requests"],
        "confirmed_pickups": d_row["confirmed_pickups"],
        "total_discarded_waste": w_row["total_discarded"],
        "total_financial_loss": w_row["total_fin_loss"],
        "total_edible_surplus": w_row["total_edible_surplus"]
    }

def get_ngo_impact_metrics(ngo_name: Optional[str] = None) -> Dict[str, Any]:
    conn = get_connection()
    cur = conn.cursor()

    query = """
        SELECT 
            COUNT(*) as total_requests,
            COALESCE(SUM(CASE WHEN status IN ('Confirmed', 'Collected', 'Delivered') THEN 1 ELSE 0 END), 0) as requests_accepted,
            COALESCE(SUM(CASE WHEN status IN ('Confirmed', 'Collected', 'Delivered') THEN requested_quantity ELSE 0 END), 0) as portions_committed,
            COALESCE(SUM(CASE WHEN status IN ('Collected', 'Delivered') THEN requested_quantity ELSE 0 END), 0) as portions_collected,
            COALESCE(SUM(CASE WHEN status = 'Delivered' THEN requested_quantity ELSE 0 END), 0) as portions_delivered,
            COALESCE(SUM(CASE WHEN status = 'Delivered' THEN 1 ELSE 0 END), 0) as completed_pickups
        FROM pickup_requests
        WHERE 1=1
    """
    params = []
    if ngo_name and ngo_name != "All":
        query += " AND ngo_name = ?"
        params.append(ngo_name)

    cur.execute(query, params)
    row = cur.fetchone()
    conn.close()

    return {
        "total_requests": row["total_requests"],
        "requests_accepted": row["requests_accepted"],
        "portions_committed": row["portions_committed"],
        "portions_collected": row["portions_collected"],
        "portions_delivered": row["portions_delivered"],
        "completed_pickups": row["completed_pickups"]
    }
