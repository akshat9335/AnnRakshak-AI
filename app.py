"""
AnnRakshak AI — Main Streamlit Web Application
Hindi Tagline: अन्न बचाओ, बर्बादी घटाओ।
English Tagline: Predict demand. Prevent waste. Rescue surplus.

Architecture:
- Shared persistent SQLite database
- Exactly TWO main dashboards:
    Dashboard A: Donor Dashboard (Overview, Donate Food, My Donations, NGO Pickup Requests, Food Waste Tracker, Demand Prediction, Gemma 4 AI Insights, Impact Summary)
    Dashboard B: NGO Dashboard (Overview, Available Food Donations, Search & Filters, Request Pickup, My Pickup Requests, Collection & Delivery Status, Impact Summary)
- Official Google Gen AI SDK integration for Gemma with transparent deterministic fallback
- Clean styling: Warm off-white background (#FDFBF7), Forest green primary (#1E4B35), Soft orange accents (#E67E22)
- CSV exports for donations, pickup requests, waste records, impact summary
- Full demo mode indicator and reset-demo-data confirmation
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import datetime
import io

import database
import demand_predictor
import ai_insights

# ----------------- PAGE CONFIG & CUSTOM CSS -----------------
st.set_page_state = getattr(st, "set_page_config")
st.set_page_config(
    page_title="AnnRakshak AI | Food Rescue & Waste Prevention",
    page_icon="🍲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Warm off-white, Forest Green, Soft Orange, Card Aesthetics)
CUSTOM_CSS = """
<style>
    /* Main container background */
    .stApp {
        background-color: #FDFBF7;
        color: #2C3E50;
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    }
    
    /* Header & Tagline styling */
    .main-header {
        background: linear-gradient(135deg, #1E4B35 0%, #2A6849 100%);
        padding: 24px 32px;
        border-radius: 12px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 4px 15px rgba(30, 75, 53, 0.15);
    }
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 12px;
        color: #FFFFFF;
    }
    .tagline-hi {
        font-size: 1.15rem;
        color: #F8C471;
        font-weight: 600;
        margin-top: 6px;
    }
    .tagline-en {
        font-size: 0.95rem;
        color: #E8F8F0;
        letter-spacing: 0.5px;
        margin-top: 2px;
    }

    /* Cards */
    .metric-card {
        background: #FFFFFF;
        padding: 18px 20px;
        border-radius: 10px;
        border: 1px solid #EAE5D9;
        box-shadow: 0 2px 6px rgba(0,0,0,0.04);
        margin-bottom: 12px;
    }
    .metric-val {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1E4B35;
        margin-top: 4px;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #7F8C8D;
        text-transform: uppercase;
        font-weight: 600;
        letter-spacing: 0.5px;
    }

    /* Status badges */
    .badge-available { background-color: #D4EDDA; color: #155724; padding: 4px 10px; border-radius: 12px; font-weight: 600; font-size: 0.82rem; }
    .badge-requested { background-color: #FFF3CD; color: #856404; padding: 4px 10px; border-radius: 12px; font-weight: 600; font-size: 0.82rem; }
    .badge-confirmed { background-color: #CCE5FF; color: #004085; padding: 4px 10px; border-radius: 12px; font-weight: 600; font-size: 0.82rem; }
    .badge-collected { background-color: #E2E3E5; color: #383D41; padding: 4px 10px; border-radius: 12px; font-weight: 600; font-size: 0.82rem; }
    .badge-delivered { background-color: #D1E7DD; color: #0F5132; padding: 4px 10px; border-radius: 12px; font-weight: 600; font-size: 0.82rem; }
    .badge-rejected  { background-color: #F8D7DA; color: #721C24; padding: 4px 10px; border-radius: 12px; font-weight: 600; font-size: 0.82rem; }
    .badge-cancelled { background-color: #F8D7DA; color: #842029; padding: 4px 10px; border-radius: 12px; font-weight: 600; font-size: 0.82rem; }

    /* Demo indicator banner */
    .demo-banner {
        background-color: #FEF9E7;
        border-left: 5px solid #F39C12;
        padding: 10px 16px;
        border-radius: 6px;
        color: #7D6608;
        font-size: 0.88rem;
        margin-bottom: 20px;
    }

    /* Section Header */
    .sec-header {
        color: #1E4B35;
        font-weight: 700;
        font-size: 1.35rem;
        border-bottom: 2px solid #EAE5D9;
        padding-bottom: 8px;
        margin-top: 10px;
        margin-bottom: 18px;
    }

    /* Safety banner */
    .safety-notice {
        background-color: #EBF5FB;
        border: 1px solid #AED6F1;
        padding: 12px 16px;
        border-radius: 8px;
        color: #1B4F72;
        font-size: 0.88rem;
        margin-bottom: 16px;
    }

    /* Sidebar accents */
    div[data-testid="stSidebar"] {
        background-color: #F7F5EE;
        border-right: 1px solid #E5E0D4;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ----------------- DATABASE INITIALIZATION -----------------
database.init_db()

# ----------------- TOP BANNER & BRANDING -----------------
st.markdown("""
<div class="main-header">
    <div class="main-title">🍲 AnnRakshak AI <span style="font-size:1.1rem; background:#E67E22; padding:3px 10px; border-radius:20px; font-weight:600;">v1.0 Demo</span></div>
    <div class="tagline-hi">अन्न बचाओ, बर्बादी घटाओ।</div>
    <div class="tagline-en">Predict demand. Prevent waste. Rescue surplus.</div>
</div>
""", unsafe_allow_html=True)

# Demo banner
st.markdown("""
<div class="demo-banner">
    ⚠️ <strong>DEMO MODE ACTIVE:</strong> Using fictional sample organizations, mock locations (Prayagraj), and safe simulated timestamps. 
    All food donations are subject to on-site hygiene verification and local food safety guidelines.
</div>
""", unsafe_allow_html=True)

# ----------------- SIDEBAR NAVIGATION & ROLE SELECTOR -----------------
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1488521787991-ed7bbaae773c?w=400&q=80", use_container_width=True)
    st.markdown("### 👤 Demo Role Selector")
    st.caption("Select your role to test end-to-end multi-role workflows:")
    
    role = st.radio(
        "Active Dashboard Role:",
        ["👨‍🍳 Dashboard A: Donor Dashboard", "🤝 Dashboard B: NGO Dashboard"],
        index=0,
        help="Switch roles to test donation creation, NGO pickup requests, and status changes across the shared SQLite database."
    )

    st.markdown("---")

    # Section selection according to role
    if "Donor" in role:
        st.markdown("#### 📋 Donor Navigation")
        donor_sections = [
            "1. Overview",
            "2. Donate Food",
            "3. My Donations",
            "4. NGO Pickup Requests",
            "5. Food Waste Tracker",
            "6. Demand Prediction",
            "7. Gemma 4 AI Insights",
            "8. Impact Summary"
        ]
        active_section = st.radio("Donor Sections", donor_sections, label_visibility="collapsed")
    else:
        st.markdown("#### 🏢 NGO Navigation")
        ngo_sections = [
            "1. Overview",
            "2. Available Food Donations",
            "3. Search & Filters",
            "4. Request Pickup",
            "5. My Pickup Requests",
            "6. Collection & Delivery Status",
            "7. Impact Summary"
        ]
        active_section = st.radio("NGO Sections", ngo_sections, label_visibility="collapsed")

    st.markdown("---")
    st.markdown("#### ⚙️ Demo Controls")
    
    # Reset Demo Database button with confirmation
    with st.expander("🔄 Reset Demo Database"):
        st.warning("This will restore default fictional donations, requests, and waste records.")
        confirm_reset = st.checkbox("I confirm reset to original demo state", key="chk_confirm_reset")
        if st.button("Execute Demo Reset", disabled=not confirm_reset, type="primary"):
            database.reset_demo_database()
            st.success("Database restored to original demo baseline!")
            st.rerun()

    st.markdown("---")
    st.caption("AnnRakshak AI — Hackathon Prototype 2026\nShared SQLite Backend")

# Helper to format status badges in HTML
def render_status_badge(status: str) -> str:
    s_clean = status.lower().replace(" ", "")
    cls_map = {
        "available": "badge-available",
        "pickuprequested": "badge-requested",
        "confirmed": "badge-confirmed",
        "collected": "badge-collected",
        "delivered": "badge-delivered",
        "rejected": "badge-rejected",
        "cancelled": "badge-cancelled",
        "expired": "badge-cancelled"
    }
    css_cls = cls_map.get(s_clean, "badge-available")
    return f'<span class="{css_cls}">{status}</span>'


# ==============================================================================
#                               DASHBOARD A: DONOR
# ==============================================================================
if "Donor" in role:

    # ---------------- 1. OVERVIEW ----------------
    if active_section.startswith("1."):
        st.markdown('<div class="sec-header">📊 Donor Dashboard — Real-time Operations & Waste Overview</div>', unsafe_allow_html=True)
        
        metrics = database.get_donor_impact_metrics()
        
        # Summary KPI cards
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Donations Listed</div>
                <div class="metric-val">{metrics['total_donations']}</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Meal Portions Offered</div>
                <div class="metric-val">{metrics['total_offered']:,}</div>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Pending NGO Requests</div>
                <div class="metric-val" style="color: #E67E22;">{metrics['pending_requests']}</div>
            </div>
            """, unsafe_allow_html=True)
        with c4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Confirmed Pickups</div>
                <div class="metric-val" style="color: #2980B9;">{metrics['confirmed_pickups']}</div>
            </div>
            """, unsafe_allow_html=True)

        c5, c6, c7, c8 = st.columns(4)
        with c5:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Portions Collected</div>
                <div class="metric-val">{metrics['total_collected']:,}</div>
            </div>
            """, unsafe_allow_html=True)
        with c6:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Portions Delivered</div>
                <div class="metric-val" style="color: #27AE60;">{metrics['total_delivered']:,}</div>
            </div>
            """, unsafe_allow_html=True)
        with c7:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Recorded Food Waste</div>
                <div class="metric-val" style="color: #C0392B;">{metrics['total_discarded_waste']:,} <span style="font-size:0.9rem">portions</span></div>
            </div>
            """, unsafe_allow_html=True)
        with c8:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Est. Financial Loss</div>
                <div class="metric-val" style="color: #C0392B;">₹{metrics['total_financial_loss']:,.0f}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # Interactive Charts
        ch1, ch2 = st.columns(2)
        donations = database.get_all_donations()
        df_don = pd.DataFrame(donations)

        with ch1:
            st.markdown("##### 📌 Donation Status Distribution")
            if not df_don.empty:
                status_counts = df_don["status"].value_counts().reset_index()
                status_counts.columns = ["Status", "Count"]
                fig_status = px.pie(
                    status_counts, names="Status", values="Count",
                    color="Status",
                    color_discrete_map={
                        "Available": "#2ECC71",
                        "Pickup Requested": "#F39C12",
                        "Confirmed": "#3498DB",
                        "Collected": "#95A5A6",
                        "Delivered": "#1ABC9C",
                        "Cancelled": "#E74C3C",
                        "Rejected": "#D35400"
                    },
                    hole=0.4
                )
                fig_status.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=300)
                st.plotly_chart(fig_status, use_container_width=True)
            else:
                st.info("No donation listings available yet.")

        with ch2:
            st.markdown("##### 📈 Portions Offered vs Collected vs Delivered")
            if not df_don.empty:
                fig_bar = go.Figure(data=[
                    go.Bar(name='Offered', x=['Meal Portions'], y=[metrics['total_offered']], marker_color='#F39C12'),
                    go.Bar(name='Collected', x=['Meal Portions'], y=[metrics['total_collected']], marker_color='#3498DB'),
                    go.Bar(name='Delivered', x=['Meal Portions'], y=[metrics['total_delivered']], marker_color='#27AE60')
                ])
                fig_bar.update_layout(barmode='group', height=300, margin=dict(t=10, b=10, l=10, r=10))
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("No portions data recorded.")

        ch3, ch4 = st.columns(2)
        waste_recs = database.get_food_waste_records()
        df_waste = pd.DataFrame(waste_recs)

        with ch3:
            st.markdown("##### 🗑️ Food Waste vs Edible Surplus Over Time")
            if not df_waste.empty:
                df_w_sorted = df_waste.sort_values("record_date")
                fig_line = px.line(
                    df_w_sorted, x="record_date", y=["edible_surplus", "discarded_waste"],
                    labels={"value": "Portions", "record_date": "Date", "variable": "Portion Type"},
                    markers=True,
                    color_discrete_map={"edible_surplus": "#27AE60", "discarded_waste": "#E74C3C"}
                )
                fig_line.update_layout(height=300, margin=dict(t=10, b=10, l=10, r=10))
                st.plotly_chart(fig_line, use_container_width=True)
            else:
                st.info("No food waste records tracked.")

        with ch4:
            st.markdown("##### 🏢 Donation Activity by Event Type")
            if not df_don.empty:
                event_counts = df_don["event_type"].value_counts().reset_index()
                event_counts.columns = ["Event Type", "Donations"]
                fig_ev = px.bar(
                    event_counts, x="Event Type", y="Donations",
                    color="Donations", color_continuous_scale="Greens"
                )
                fig_ev.update_layout(height=300, margin=dict(t=10, b=10, l=10, r=10))
                st.plotly_chart(fig_ev, use_container_width=True)
            else:
                st.info("No event data.")

    # ---------------- 2. DONATE FOOD ----------------
    elif active_section.startswith("2."):
        st.markdown('<div class="sec-header">🍲 Donate Food — List Surplus from Weddings, Events & Canteens</div>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="safety-notice">
            🛡️ <strong>Food Safety & Storage Responsibility Notice:</strong><br>
            Donated food must have been prepared in compliance with hygienic kitchen standards, stored at safe temperatures 
            (&gt;63°C for hot food or &lt;4°C for refrigerated food), and packaged in food-grade clean containers. 
            Antigravity and AnnRakshak AI do NOT certify food safety autonomously; donor and NGO representatives must inspect meals on handover.
        </div>
        """, unsafe_allow_html=True)

        # Pre-fill Demo action
        col_load, _ = st.columns([2, 5])
        with col_load:
            if st.button("✨ Load Wedding Demo Form Values", help="Pre-populates fields with a realistic fictional wedding surplus listing (does not auto-submit)"):
                st.session_state["form_donor_name"] = "Sharma Grand Wedding Reception (Demo)"
                st.session_state["form_event_type"] = "Wedding"
                st.session_state["form_food_items"] = "Vegetable Dum Biryani, Paneer Butter Masala, Tandoori Roti & Gulab Jamun"
                st.session_state["form_food_type"] = "Vegetarian"
                st.session_state["form_qty"] = 120
                st.session_state["form_storage"] = "Maintained in covered chafing dishes with live warmers; will be packaged in 500ml food-grade containers."
                st.session_state["form_loc"] = "Tagore Town Palace Banquet Hall, Prayagraj"
                st.session_state["form_contact"] = "Demo Coordinator: +91-98765-11223 (Rajesh Sharma)"
                st.session_state["form_notes"] = "Excess meal cooked due to weather drop. Freshly taken off banquet counters."
                st.info("Wedding Demo sample values loaded into the form below! You may adjust and click 'Publish Donation Listing'.")

        with st.form("donate_food_form"):
            c1, c2 = st.columns(2)
            with c1:
                donor_name = st.text_input("Donor / Organization Name *", value=st.session_state.get("form_donor_name", "Sharma Wedding Events"))
                event_type = st.selectbox(
                    "Event Type *",
                    ["Wedding", "Birthday Party", "Family Function", "College Event", "Restaurant", "Hotel", "Hostel", "Canteen", "Other"],
                    index=["Wedding", "Birthday Party", "Family Function", "College Event", "Restaurant", "Hotel", "Hostel", "Canteen", "Other"].index(st.session_state.get("form_event_type", "Wedding"))
                )
                food_type = st.selectbox("Dietary Classification *", ["Vegetarian", "Non-Vegetarian", "Vegan", "Jain Food"], index=0)
                food_items = st.text_area("Food Items & Menu Description *", value=st.session_state.get("form_food_items", "Vegetable pulao, dal tadka, fresh chapati"), height=100)
                quantity = st.number_input("Quantity (Meal Portions) *", min_value=1, max_value=5000, value=st.session_state.get("form_qty", 100), step=5)

            with c2:
                today = datetime.date.today()
                prep_time = st.time_input("Preparation Time *", value=datetime.time(19, 0))
                avail_time = st.time_input("Available From *", value=datetime.time(19, 30))
                deadline_time = st.time_input("Strict Pickup Deadline *", value=datetime.time(23, 0))
                location = st.text_input("Pickup Locality / Address *", value=st.session_state.get("form_loc", "Civil Lines, Prayagraj (Fictional Demo Locality)"))
                storage_handling = st.text_input("Storage & Handling Protocol *", value=st.session_state.get("form_storage", "Kept hot in insulated chafing dishes; clean food-grade containers"))
                private_contact = st.text_input("Private Contact Details (Revealed only to Confirmed NGO) *", value=st.session_state.get("form_contact", "Demo Host: +91-98765-43210"))
                notes = st.text_input("Additional Notes for Volunteers", value=st.session_state.get("form_notes", "Freshly cooked; ramp access available for transport van."))

            submitted = st.form_submit_button("🚀 Publish Donation Listing", type="primary", use_container_width=True)

            if submitted:
                # Validation
                if not donor_name.strip() or not food_items.strip() or not location.strip() or not private_contact.strip():
                    st.error("Please fill in all required fields marked with *.")
                elif quantity <= 0:
                    st.error("Quantity must be greater than zero.")
                else:
                    try:
                        prep_dt = f"{today.strftime('%Y-%m-%d')} {prep_time.strftime('%H:%M')}"
                        avail_dt = f"{today.strftime('%Y-%m-%d')} {avail_time.strftime('%H:%M')}"
                        dead_dt = f"{today.strftime('%Y-%m-%d')} {deadline_time.strftime('%H:%M')}"

                        donation_payload = {
                            "donor_name": donor_name.strip(),
                            "event_type": event_type,
                            "food_items": food_items.strip(),
                            "food_type": food_type,
                            "quantity": quantity,
                            "quantity_unit": "meal portions",
                            "prep_datetime": prep_dt,
                            "available_from": avail_dt,
                            "pickup_deadline": dead_dt,
                            "location": location.strip(),
                            "storage_handling": storage_handling.strip(),
                            "private_contact": private_contact.strip(),
                            "notes": notes.strip()
                        }

                        new_id = database.create_donation(donation_payload)
                        st.success(f"🎉 Donation Successfully Created! Unique ID: {new_id}")
                        st.balloons()
                        st.info("Listing is now instantly visible on both 'My Donations' and the 'NGO Dashboard' in the shared database!")
                    except Exception as e:
                        st.error(f"Error publishing donation: {e}")

    # ---------------- 3. MY DONATIONS ----------------
    elif active_section.startswith("3."):
        st.markdown('<div class="sec-header">📋 My Donations — Manage Listed Surplus & Requests</div>', unsafe_allow_html=True)
        
        # Filters
        f1, f2, f3 = st.columns([2, 2, 3])
        with f1:
            stat_filter = st.selectbox("Status Filter", ["All", "Available", "Pickup Requested", "Confirmed", "Collected", "Delivered", "Cancelled"])
        with f2:
            ev_filter = st.selectbox("Event Type Filter", ["All", "Wedding", "Birthday Party", "Family Function", "Restaurant", "Hotel", "Hostel", "Canteen", "Other"])
        with f3:
            search_txt = st.text_input("🔍 Search Food, Donor or Locality", placeholder="e.g., Pulao, Civil Lines...")

        donations = database.get_all_donations(status_filter=stat_filter, event_filter=ev_filter, search=search_txt)

        if not donations:
            st.info("No matching donation records found.")
        else:
            st.caption(f"Showing {len(donations)} donation listings from persistent SQLite database:")
            for d in donations:
                with st.expander(f"🍲 {d['id']} — {d['donor_name']} ({d['event_type']}) | {d['remaining_quantity']}/{d['original_quantity']} portions | Status: {d['status']}", expanded=(d['status'] in ['Pickup Requested', 'Available'])):
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown(f"**Menu Items:** {d['food_items']}")
                        st.markdown(f"**Food Type:** {d['food_type']}")
                        st.markdown(f"**Quantity:** {d['remaining_quantity']} remaining out of {d['original_quantity']} original portions")
                        st.markdown(f"**Prep Time:** {d['prep_datetime']}")
                        st.markdown(f"**Pickup Window:** {d['available_from']} to {d['pickup_deadline']}")
                    with c2:
                        st.markdown(f"**Location:** {d['location']}")
                        st.markdown(f"**Storage & Handling:** {d['storage_handling']}")
                        st.markdown(f"**Private Contact:** `{d['private_contact']}`")
                        st.markdown(f"**Notes:** {d['notes'] or 'None'}")
                        badge_html = render_status_badge(d['status'])
                        st.markdown(f"**Current Status:** {badge_html}", unsafe_allow_html=True)

                    st.markdown("---")
                    
                    # Related NGO requests for this donation
                    requests = database.get_pickup_requests_for_donation(d['id'])
                    if requests:
                        st.markdown(f"##### 🤝 NGO Pickup Requests for this Listing ({len(requests)})")
                        for r in requests:
                            rc1, rc2, rc3 = st.columns([3, 2, 2])
                            with rc1:
                                st.write(f"**NGO:** {r['ngo_name']}")
                                st.write(f"**Contact:** {r['ngo_contact']}")
                                st.write(f"**Requested Quantity:** {r['requested_quantity']} portions")
                                st.write(f"**Proposed Pickup:** {r['proposed_pickup_time']}")
                                if r.get('notes'):
                                    st.caption(f"Note: {r['notes']}")
                            with rc2:
                                r_badge = render_status_badge(r['status'])
                                st.markdown(f"**Request Status:** {r_badge}", unsafe_allow_html=True)
                                st.caption(f"Requested at: {r['created_at']}")
                            with rc3:
                                # Actions: Accept or Reject if Pickup Requested
                                if r['status'] == "Pickup Requested":
                                    if st.button("✅ Accept Request", key=f"acc_{r['id']}", type="primary"):
                                        database.update_request_status(r['id'], "Confirmed", d['donor_name'], "Donor confirmed pickup")
                                        st.success(f"Request {r['id']} Confirmed!")
                                        st.rerun()
                                    if st.button("❌ Reject Request", key=f"rej_{r['id']}"):
                                        database.update_request_status(r['id'], "Rejected", d['donor_name'], "Donor declined request")
                                        st.warning(f"Request {r['id']} Rejected; portions restored to listing.")
                                        st.rerun()
                                else:
                                    st.write(f"No donor actions pending for status '{r['status']}'.")
                    else:
                        st.caption("No NGO pickup requests submitted for this listing yet.")

                    # Donor cancel option
                    if d['status'] in ["Available", "Pickup Requested"]:
                        st.markdown("---")
                        if st.button(f"🚫 Cancel This Listing ({d['id']})", key=f"can_{d['id']}"):
                            database.cancel_donation(d['id'], d['donor_name'], "Cancelled by donor")
                            st.warning(f"Donation {d['id']} has been cancelled.")
                            st.rerun()

    # ---------------- 4. NGO PICKUP REQUESTS (DONOR VIEW) ----------------
    elif active_section.startswith("4."):
        st.markdown('<div class="sec-header">🤝 Incoming NGO Pickup Requests</div>', unsafe_allow_html=True)
        st.write("Review all pending, confirmed, or completed food pickup requests across all your listed events:")

        all_reqs = database.get_all_pickup_requests()
        if not all_reqs:
            st.info("No pickup requests have been received yet.")
        else:
            for req in all_reqs:
                with st.expander(f"📦 Request {req['id']} for Donation {req['donation_id']} | NGO: {req['ngo_name']} | Status: {req['status']}", expanded=(req['status']=="Pickup Requested")):
                    c1, c2, c3 = st.columns([3, 2, 2])
                    with c1:
                        st.markdown(f"**Donation ID:** {req['donation_id']} ({req['food_items']})")
                        st.markdown(f"**NGO Name:** {req['ngo_name']}")
                        st.markdown(f"**NGO Volunteer Phone:** `{req['ngo_contact']}`")
                        st.markdown(f"**Requested Quantity:** **{req['requested_quantity']} portions**")
                        st.markdown(f"**Proposed Pickup Time:** {req['proposed_pickup_time']}")
                    with c2:
                        st.markdown(f"**Location:** {req['location']}")
                        st.markdown(f"**Request Timestamp:** {req['created_at']}")
                        st.markdown(f"**Current Status:** {render_status_badge(req['status'])}", unsafe_allow_html=True)
                        if req.get('notes'):
                            st.info(f"NGO Note: {req['notes']}")
                    with c3:
                        if req['status'] == "Pickup Requested":
                            st.markdown("##### Action Required")
                            if st.button("✅ Accept Request", key=f"ov_acc_{req['id']}", type="primary", use_container_width=True):
                                database.update_request_status(req['id'], "Confirmed", req['donor_name'], "Donor confirmed pickup")
                                st.success("Request accepted!")
                                st.rerun()
                            if st.button("❌ Reject Request", key=f"ov_rej_{req['id']}", use_container_width=True):
                                database.update_request_status(req['id'], "Rejected", req['donor_name'], "Donor rejected")
                                st.warning("Request rejected and portions restored.")
                                st.rerun()
                        else:
                            st.caption(f"Status is '{req['status']}'. Handled by NGO dispatch workflow.")

    # ---------------- 5. FOOD WASTE TRACKER ----------------
    elif active_section.startswith("5."):
        st.markdown('<div class="sec-header">📉 Food Waste Tracker — Mess, Caterer & Kitchen Audit</div>', unsafe_allow_html=True)
        st.caption("Record meals prepared vs consumed to calculate exact discarded waste percentages, leftover costs, and edible surplus:")

        with st.form("waste_entry_form"):
            st.markdown("##### ➕ Log Food Consumption & Waste Record")
            c1, c2 = st.columns(2)
            with c1:
                provider = st.text_input("Kitchen / Provider / Event Name *", value="Sharma Wedding Events (Demo)")
                rec_date = st.date_input("Audit Date *", value=datetime.date.today())
                meal_type = st.selectbox("Meal Type *", ["Breakfast", "Lunch", "Hi-Tea", "Dinner", "Buffet Assortment"])
                menu_desc = st.text_input("Menu Description *", value="Dal Makhani, Rice, Paneer Curry, Chapatis")
                cost_per_meal = st.number_input("Cost Per Meal (₹) *", min_value=1.0, max_value=5000.0, value=150.0, step=10.0)

            with c2:
                p_prep = st.number_input("Portions Prepared *", min_value=1, max_value=10000, value=300, step=10)
                p_cons = st.number_input("Portions Consumed *", min_value=0, max_value=10000, value=250, step=10)
                st.caption(f"💡 Calculated Leftover: **{max(0, p_prep - p_cons)} portions**")
                p_edible = st.number_input("Edible Surplus (Safe for Donation) *", min_value=0, max_value=1000, value=35, step=5)
                p_discard = st.number_input("Discarded Inedible Waste (Plate scraps, spoiled) *", min_value=0, max_value=1000, value=15, step=5)
                notes_waste = st.text_input("Audit Observations", value="Excess cooked due to 15% RSVP no-shows.")

            btn_waste = st.form_submit_button("💾 Save Food Waste Record", type="primary", use_container_width=True)

            if btn_waste:
                try:
                    payload = {
                        "provider_name": provider.strip(),
                        "record_date": rec_date.strftime("%Y-%m-%d"),
                        "meal_type": meal_type,
                        "menu_items": menu_desc.strip(),
                        "portions_prepared": p_prep,
                        "portions_consumed": p_cons,
                        "edible_surplus": p_edible,
                        "discarded_waste": p_discard,
                        "cost_per_meal": cost_per_meal,
                        "notes": notes_waste.strip()
                    }
                    w_id = database.add_food_waste_record(payload)
                    st.success(f"Waste Record Successfully Saved! ID: {w_id}")
                    st.rerun()
                except ValueError as ve:
                    st.error(f"Validation Error: {ve}")

        st.markdown("---")
        st.markdown("##### 📜 Recent Kitchen Waste Records")
        recs = database.get_food_waste_records()
        if recs:
            df_w = pd.DataFrame(recs)
            st.dataframe(
                df_w[["id", "provider_name", "record_date", "meal_type", "portions_prepared", "portions_consumed", "leftover_quantity", "edible_surplus", "discarded_waste", "leftover_pct", "discarded_waste_pct", "financial_loss"]],
                use_container_width=True
            )
            
            # Quick aggregate metrics
            st.markdown(f"**Total Tracked Financial Loss from Discarded Food:** <span style='color:#C0392B; font-weight:700; font-size:1.1rem;'>₹{df_w['financial_loss'].sum():,.2f}</span>", unsafe_allow_html=True)
        else:
            st.info("No food waste records logged yet.")

    # ---------------- 6. DEMAND PREDICTION ----------------
    elif active_section.startswith("6."):
        st.markdown('<div class="sec-header">🎯 Demand Prediction — Baseline Consumption Estimator</div>', unsafe_allow_html=True)
        st.write("Transparent mathematical demand estimator for banquet managers and hostel mess supervisors:")

        st.markdown("""
        <div class="safety-notice">
            ℹ️ <strong>Transparent Baseline Estimator:</strong><br>
            Calculates recommended preparation quantities using historical meals-consumed-per-attendee ratios and a configurable safety buffer. 
            <em>Note: This is an empirical estimation model, not an unverified black-box neural network. No guaranteed zero-waste or accuracy is claimed.</em>
        </div>
        """, unsafe_allow_html=True)

        col_in, col_res = st.columns([3, 4])
        with col_in:
            st.markdown("##### ⚙️ Event Parameters")
            pred_attendees = st.number_input("Expected Attendees (RSVP count)", min_value=10, max_value=10000, value=350, step=25)
            pred_event_type = st.selectbox("Event / Provider Type", ["Sharma Wedding Events (Demo)", "Hostel Mess Demo (Block A)", "Green Plate Demo Restaurant", "College Canteen Demo", "Other"])
            pred_meal_type = st.selectbox("Meal Category", ["All", "Dinner", "Lunch", "Breakfast"])
            pred_buffer = st.slider("Safety Buffer (%)", min_value=0, max_value=30, value=10, step=1, help="Extra portions cooked above baseline demand to handle walk-ins.")
            pred_cost = st.number_input("Estimated Cost Per Meal (₹)", min_value=20.0, max_value=2000.0, value=180.0, step=10.0)

            calc_btn = st.button("📊 Calculate Demand Estimate", type="primary", use_container_width=True)

        with col_res:
            st.markdown("##### 📋 Recommended Preparation Quantities")
            recs = database.get_food_waste_records()
            prediction = demand_predictor.calculate_demand_prediction(
                expected_attendees=pred_attendees,
                safety_buffer_pct=pred_buffer,
                cost_per_meal=pred_cost,
                historical_records=recs,
                filter_provider=pred_event_type if pred_event_type != "Other" else None,
                filter_meal_type=pred_meal_type
            )

            p1, p2 = st.columns(2)
            with p1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Estimated Baseline Demand</div>
                    <div class="metric-val">{prediction['base_demand']} <span style="font-size:0.9rem">portions</span></div>
                </div>
                """, unsafe_allow_html=True)
            with p2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Recommended Prep (with Buffer)</div>
                    <div class="metric-val" style="color:#27AE60;">{prediction['recommended_portions']} <span style="font-size:0.9rem">portions</span></div>
                </div>
                """, unsafe_allow_html=True)

            p3, p4 = st.columns(2)
            with p3:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Buffer Portions (+{pred_buffer}%)</div>
                    <div class="metric-val" style="color:#E67E22;">+{prediction['buffer_portions']} <span style="font-size:0.9rem">portions</span></div>
                </div>
                """, unsafe_allow_html=True)
            with p4:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Estimated Food Cost</div>
                    <div class="metric-val">₹{prediction['expected_total_cost']:,.2f}</div>
                </div>
                """, unsafe_allow_html=True)

            st.info(f"**Formulation Method:**\n{prediction['method_used']}")

            if prediction['has_history']:
                hs = prediction['history_summary']
                st.caption(f"Historical stats used: {hs['records_analyzed']} records | Average waste: {hs['avg_waste_pct']}% | Average consumption: {hs['avg_consumption_pct']}%")

    # ---------------- 7. GEMMA 4 AI INSIGHTS ----------------
    elif active_section.startswith("7."):
        st.markdown('<div class="sec-header">🤖 Gemma 4 AI Insights — Food Waste & Operational Analytics</div>', unsafe_allow_html=True)
        st.caption("Integrates via the official Google Gen AI SDK (`google-genai`). All calculations are strictly derived from SQLite records without hallucinations:")

        # API Key input / check
        with st.expander("🔑 Google Gen AI SDK API Configuration (Optional)"):
            st.write("To run live Gemma 4 / Gemma inference, enter your Gemini API key below. If left empty, AnnRakshak AI will transparently provide a deterministic rule-based demo analysis.")
            user_api_key = st.text_input("Google Gen AI API Key", type="password", placeholder="AIzaSy...", help="Configured via Streamlit or environment variable.")
            preferred_model = st.selectbox("Preferred Verified Model", ["gemma-2-9b-it", "gemma-2-27b-it", "gemini-2.5-flash"], index=0)

        waste_records = database.get_food_waste_records()
        
        col_btn, _ = st.columns([3, 4])
        with col_btn:
            run_ai = st.button("🔍 Analyze Food Waste with Gemma 4", type="primary", use_container_width=True)

        if run_ai or "ai_results" in st.session_state:
            if run_ai:
                with st.spinner("Analyzing food waste records via AnnRakshak AI engine..."):
                    insights = ai_insights.generate_waste_insights(
                        waste_records=waste_records,
                        api_key=user_api_key,
                        preferred_model=preferred_model
                    )
                    st.session_state["ai_results"] = insights
            else:
                insights = st.session_state.get("ai_results", {})

            # Display results
            if insights:
                source_badge = "🟢 Live AI Model" if insights.get("is_ai") else "🟡 Transparent Demo Fallback"
                st.markdown(f"**Analysis Engine:** `{insights.get('source')}` | {source_badge}")

                m = insights.get("metrics", {})
                if m:
                    mc1, mc2, mc3, mc4 = st.columns(4)
                    with mc1:
                        st.metric("Total Records", m.get("total_records", 0))
                    with mc2:
                        st.metric("Total Prepared", f"{m.get('total_portions_prepared', 0):,} portions")
                    with mc3:
                        st.metric("Avg Discard Rate", f"{m.get('avg_discard_pct', 0)}%")
                    with mc4:
                        st.metric("Financial Loss", f"₹{m.get('total_financial_loss', 0):,.2f}")

                st.markdown("---")

                if insights.get("is_ai") and insights.get("raw_text"):
                    st.markdown("### 📝 Gemma AI Intelligence Report")
                    st.markdown(insights["raw_text"])
                else:
                    st.markdown("### 📝 Grounded Operational Observations")
                    for obs in insights.get("observations", []):
                        st.markdown(f"- {obs}")

                    st.markdown("### 💡 Practical Overproduction Prevention Strategies")
                    for rec in insights.get("recommendations", []):
                        st.markdown(f"1. **{rec.split(':')[0]}**: {rec.split(':')[1] if ':' in rec else rec}")

                st.markdown("---")
                st.caption(f"**System Note & Scope Boundaries:** {insights.get('limitations')}")

    # ---------------- 8. IMPACT SUMMARY ----------------
    elif active_section.startswith("8."):
        st.markdown('<div class="sec-header">🌱 Donor Impact Summary & Audit Reports</div>', unsafe_allow_html=True)
        st.write("Measured food surplus recovery and recorded waste prevention metrics:")

        metrics = database.get_donor_impact_metrics()

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Total Donations Listed</div>
                <div class="metric-val">{metrics['total_donations']} listings</div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Meal Portions Offered</div>
                <div class="metric-val">{metrics['total_offered']:,} meals</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Portions Collected by NGOs</div>
                <div class="metric-val" style="color:#2980B9;">{metrics['total_collected']:,} meals</div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Portions Confirmed Delivered</div>
                <div class="metric-val" style="color:#27AE60;">{metrics['total_delivered']:,} meals</div>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Recorded Discarded Food</div>
                <div class="metric-val" style="color:#C0392B;">{metrics['total_discarded_waste']:,} portions</div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Recorded Financial Value Discarded</div>
                <div class="metric-val" style="color:#C0392B;">₹{metrics['total_financial_loss']:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("##### 📥 Export Data for Auditing & Reports (CSV)")
        
        exp_col1, exp_col2, exp_col3 = st.columns(3)
        with exp_col1:
            # Donations export (without exposing sensitive private contacts)
            donations = database.get_all_donations()
            df_don_exp = pd.DataFrame(donations)
            if not df_don_exp.empty:
                # Sanitize private contact
                df_don_exp_safe = df_don_exp.drop(columns=["private_contact"], errors="ignore")
                csv_don = df_don_exp_safe.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "📥 Export Public Donations (CSV)",
                    data=csv_don,
                    file_name="annrakshak_donations_public.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        with exp_col2:
            waste_recs = database.get_food_waste_records()
            df_w_exp = pd.DataFrame(waste_recs)
            if not df_w_exp.empty:
                csv_waste = df_w_exp.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "📥 Export Food Waste Log (CSV)",
                    data=csv_waste,
                    file_name="annrakshak_food_waste_audit.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        with exp_col3:
            impact_df = pd.DataFrame([metrics])
            csv_imp = impact_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Export Donor Impact Summary (CSV)",
                data=csv_imp,
                file_name="annrakshak_donor_impact_summary.csv",
                mime="text/csv",
                use_container_width=True
            )


# ==============================================================================
#                               DASHBOARD B: NGO
# ==============================================================================
else:
    # ---------------- 1. NGO OVERVIEW ----------------
    if active_section.startswith("1."):
        st.markdown('<div class="sec-header">🏢 NGO Dashboard — Surplus Discovery & Food Recovery</div>', unsafe_allow_html=True)
        
        ngo_metrics = database.get_ngo_impact_metrics()
        
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Pickup Requests Submitted</div>
                <div class="metric-val">{ngo_metrics['total_requests']}</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Requests Accepted / Confirmed</div>
                <div class="metric-val" style="color:#2980B9;">{ngo_metrics['requests_accepted']}</div>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Portions Collected</div>
                <div class="metric-val" style="color:#E67E22;">{ngo_metrics['portions_collected']:,}</div>
            </div>
            """, unsafe_allow_html=True)
        with c4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Portions Delivered</div>
                <div class="metric-val" style="color:#27AE60;">{ngo_metrics['portions_delivered']:,}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # Discover quick cards
        st.markdown("##### 🍲 Available Donations Ready for Pickup")
        avail_donations = database.get_all_donations(status_filter="Available")
        if avail_donations:
            st.caption(f"{len(avail_donations)} surplus food lots currently available in your locality:")
            for d in avail_donations:
                col_d1, col_d2 = st.columns([3, 1])
                with col_d1:
                    st.write(f"**{d['donor_name']}** ({d['event_type']}) — **{d['food_items']}**")
                    st.write(f"📍 {d['location']} | ⏳ Pickup deadline: **{d['pickup_deadline']}** | 📦 Remaining: **{d['remaining_quantity']} {d['quantity_unit']}**")
                with col_d2:
                    st.markdown(f"<span style='color:#1E4B35; font-size:1.4rem; font-weight:700;'>{d['remaining_quantity']}</span> portions", unsafe_allow_html=True)
                    st.markdown(render_status_badge(d['status']), unsafe_allow_html=True)
                st.markdown("<hr style='margin:6px 0;'>", unsafe_allow_html=True)
        else:
            st.info("No surplus food lots currently open for request.")

    # ---------------- 2. AVAILABLE FOOD DONATIONS ----------------
    elif active_section.startswith("2."):
        st.markdown('<div class="sec-header">🍲 Available Food Donations — Discover & Inspect</div>', unsafe_allow_html=True)
        st.caption("Live feed from the shared database. Private donor contact details are concealed until a pickup request is confirmed:")

        donations = database.get_all_donations()
        # Filter for donations that have remaining portions
        active_donations = [d for d in donations if d["remaining_quantity"] > 0 and d["status"] in ["Available", "Pickup Requested"]]

        if not active_donations:
            st.info("No active donations with remaining portions available.")
        else:
            for d in active_donations:
                with st.container():
                    st.markdown(f"""
                    <div class="metric-card" style="border-left: 6px solid #27AE60;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <span style="font-weight:700; font-size:1.15rem; color:#1E4B35;">{d['donor_name']} — {d['event_type']}</span>
                            {render_status_badge(d['status'])}
                        </div>
                        <div style="margin-top:6px; color:#34495E;"><strong>Items:</strong> {d['food_items']} ({d['food_type']})</div>
                        <div style="margin-top:4px; font-size:0.9rem; color:#5D6D7E;">
                            📍 <strong>Locality:</strong> {d['location']} | 
                            🍲 <strong>Available:</strong> {d['remaining_quantity']} / {d['original_quantity']} portions | 
                            ⏰ <strong>Deadline:</strong> {d['pickup_deadline']}
                        </div>
                        <div style="margin-top:4px; font-size:0.85rem; color:#7F8C8D;">
                            ❄️ <strong>Storage:</strong> {d['storage_handling']} | 
                            📝 <strong>Kitchen Notes:</strong> {d['notes'] or 'None'}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    # Quick button to open request pickup section for this donation
                    with st.expander(f"🔍 View Full Details & Request Form for {d['id']}"):
                        st.markdown(ai_insights.format_donation_description(d))
                        st.caption("Private donor phone number is protected and visible only on confirmed pickup requests.")
                        if st.button(f"➡️ Proceed to Request Pickup for {d['id']}", key=f"req_btn_{d['id']}"):
                            st.session_state["selected_donation_for_request"] = d['id']
                            st.info(f"Selected {d['id']}! Navigate to '4. Request Pickup' section to complete.")

    # ---------------- 3. SEARCH & FILTERS ----------------
    elif active_section.startswith("3."):
        st.markdown('<div class="sec-header">🔍 Search & Filter Food Donations</div>', unsafe_allow_html=True)
        
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            f_event = st.selectbox("Event Category", ["All", "Wedding", "Birthday Party", "Family Function", "Restaurant", "Hotel", "Hostel", "Canteen", "Other"])
        with c2:
            f_min_qty = st.number_input("Minimum Portions Needed", min_value=0, max_value=2000, value=10, step=10)
        with c3:
            f_status = st.selectbox("Listing Status", ["All", "Available", "Pickup Requested", "Confirmed", "Collected", "Delivered"])
        with c4:
            f_query = st.text_input("Keyword Search (Food or Area)", placeholder="e.g. Biryani, Tagore Town")

        all_don = database.get_all_donations(status_filter=f_status, event_filter=f_event, search=f_query)
        # Filter by min quantity
        filtered = [d for d in all_don if d["remaining_quantity"] >= f_min_qty]

        st.caption(f"Found {len(filtered)} matching food donation listings:")
        if filtered:
            for d in filtered:
                with st.expander(f"🍲 {d['id']}: {d['food_items']} ({d['remaining_quantity']} portions available in {d['location']})"):
                    st.write(f"**Donor:** {d['donor_name']} | **Event:** {d['event_type']}")
                    st.write(f"**Preparation Time:** {d['prep_datetime']} | **Deadline:** {d['pickup_deadline']}")
                    st.write(f"**Storage:** {d['storage_handling']}")
                    st.write(f"**Status:** {d['status']}")
        else:
            st.info("No donations match the specified search and filter criteria.")

    # ---------------- 4. REQUEST PICKUP ----------------
    elif active_section.startswith("4."):
        st.markdown('<div class="sec-header">📦 Request Food Pickup — NGO Dispatch Portal</div>', unsafe_allow_html=True)
        st.write("Submit a verified food recovery pickup request with safe database quantity reservations:")

        donations = database.get_all_donations()
        eligible_donations = [d for d in donations if d["remaining_quantity"] > 0 and d["status"] in ["Available", "Pickup Requested"]]

        if not eligible_donations:
            st.warning("Currently, there are no donations with remaining portions available to request.")
        else:
            don_options = {f"{d['id']} — {d['donor_name']} ({d['food_items'][:30]}...) [{d['remaining_quantity']} avail]": d['id'] for d in eligible_donations}
            
            # Pre-select if forwarded from available list
            default_idx = 0
            selected_prev = st.session_state.get("selected_donation_for_request")
            if selected_prev:
                for idx, (label, d_id) in enumerate(don_options.items()):
                    if d_id == selected_prev:
                        default_idx = idx
                        break

            with st.form("ngo_pickup_request_form"):
                sel_label = st.selectbox("Select Donation Listing *", list(don_options.keys()), index=default_idx)
                selected_don_id = don_options[sel_label]
                selected_don = database.get_donation_by_id(selected_don_id)

                st.info(f"Selected: **{selected_don['food_items']}** | Available to claim: **{selected_don['remaining_quantity']} meal portions** | Location: {selected_don['location']}")

                c1, c2 = st.columns(2)
                with c1:
                    ngo_name = st.selectbox("Requesting NGO / Recovery Org *", [
                        "Asha Food Rescue Foundation (Sample Demo NGO)",
                        "Roti Bank Prayagraj (Sample Demo NGO)",
                        "Annapurna Community Kitchen (Sample Demo NGO)",
                        "Prayag Hunger Relief Squad (Sample Demo NGO)"
                    ])
                    ngo_contact = st.text_input("Volunteer Coordinator Contact *", value="+91-91234-56789 (Asha Dispatch Desk)")
                    req_qty = st.number_input(
                        "Requested Quantity (Portions) *",
                        min_value=1,
                        max_value=max(1, selected_don['remaining_quantity']),
                        value=min(25, selected_don['remaining_quantity']),
                        step=5,
                        help="Safe database transaction ensures portions cannot be claimed twice."
                    )

                with c2:
                    proposed_time = st.text_input("Proposed Pickup Time *", value=f"{datetime.date.today().strftime('%Y-%m-%d')} 20:30")
                    ngo_notes = st.text_area("Transport & Distribution Notes", value="Van equipped with insulated hot/cold transport bags. Distributing to shelter home.")

                submit_req = st.form_submit_button("📨 Submit Pickup Request", type="primary", use_container_width=True)

                if submit_req:
                    if not ngo_name or not ngo_contact or not proposed_time:
                        st.error("Please fill in all required fields.")
                    elif req_qty <= 0 or req_qty > selected_don['remaining_quantity']:
                        st.error(f"Invalid quantity. You can request between 1 and {selected_don['remaining_quantity']} portions.")
                    else:
                        try:
                            req_payload = {
                                "donation_id": selected_don_id,
                                "ngo_name": ngo_name,
                                "ngo_contact": ngo_contact.strip(),
                                "requested_quantity": req_qty,
                                "proposed_pickup_time": proposed_time.strip(),
                                "notes": ngo_notes.strip()
                            }
                            req_id = database.create_pickup_request(req_payload)
                            st.success(f"🎉 Pickup Request Submitted! ID: {req_id}")
                            st.balloons()
                            st.info("The request is now visible in both your NGO dashboard and the Donor's Request section in SQLite!")
                            if "selected_donation_for_request" in st.session_state:
                                del st.session_state["selected_donation_for_request"]
                        except ValueError as ve:
                            st.error(f"Transaction Rejected: {ve}")

    # ---------------- 5. MY PICKUP REQUESTS (NGO VIEW) ----------------
    elif active_section.startswith("5."):
        st.markdown('<div class="sec-header">📋 My Pickup Requests — Tracking & Handover Status</div>', unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            ngo_filter = st.selectbox("Filter by NGO", ["All", "Asha Food Rescue Foundation (Sample Demo NGO)", "Roti Bank Prayagraj (Sample Demo NGO)", "Annapurna Community Kitchen (Sample Demo NGO)", "Prayag Hunger Relief Squad (Sample Demo NGO)"])
        with c2:
            st_filter = st.selectbox("Filter by Status", ["All", "Pickup Requested", "Confirmed", "Collected", "Delivered", "Rejected", "Cancelled"])

        reqs = database.get_all_pickup_requests(ngo_name_filter=ngo_filter, status_filter=st_filter)

        if not reqs:
            st.info("No pickup requests found for the selected filter.")
        else:
            st.caption(f"Showing {len(reqs)} pickup requests:")
            for r in reqs:
                with st.expander(f"📦 {r['id']} — {r['food_items']} ({r['requested_quantity']} portions) | Status: {r['status']}", expanded=(r['status'] in ['Confirmed', 'Pickup Requested'])):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Donation ID:** `{r['donation_id']}`")
                        st.markdown(f"**Donor:** {r['donor_name']}")
                        st.markdown(f"**Menu Description:** {r['food_items']}")
                        st.markdown(f"**Requested Quantity:** {r['requested_quantity']} meal portions")
                        st.markdown(f"**Proposed Pickup:** {r['proposed_pickup_time']}")
                    with col2:
                        st.markdown(f"**Location:** {r['location']}")
                        st.markdown(f"**Requested At:** {r['created_at']}")
                        st.markdown(f"**Current Status:** {render_status_badge(r['status'])}", unsafe_allow_html=True)
                        
                        # Sensitive private contact disclosed ONLY if Confirmed or further along
                        if r['status'] in ["Confirmed", "Collected", "Delivered"]:
                            st.success(f"🔓 **Donor Contact Details (Authorized):**\n`{r['private_contact']}`")
                        else:
                            st.warning("🔒 Donor private contact details will be revealed once request is Confirmed by the donor.")

                    # Status Progression Actions for NGO
                    st.markdown("---")
                    st.markdown("##### 🚚 Operational Status Updates")
                    act_col1, act_col2 = st.columns(2)
                    with act_col1:
                        if r['status'] == "Confirmed":
                            if st.button(f"🚗 Mark Collected by Volunteer ({r['id']})", key=f"col_{r['id']}", type="primary"):
                                database.update_request_status(r['id'], "Collected", r['ngo_name'], "Volunteer confirmed physical pickup from event site")
                                st.success("Status updated to 'Collected'!")
                                st.rerun()
                        elif r['status'] == "Collected":
                            if st.button(f"🏠 Mark Delivered to Beneficiaries ({r['id']})", key=f"del_{r['id']}", type="primary"):
                                database.update_request_status(r['id'], "Delivered", r['ngo_name'], "Food safely distributed at shelter")
                                st.success("Status updated to 'Delivered'!")
                                st.rerun()
                        elif r['status'] == "Delivered":
                            st.success("✅ Delivery completed! Food distribution recorded.")
                        elif r['status'] == "Pickup Requested":
                            st.info("Awaiting Donor approval. Donor must accept request in the Donor Dashboard.")
                        elif r['status'] == "Rejected":
                            st.error("Request was rejected by donor. Allocated portions were restored.")
                    with act_col2:
                        if r['status'] in ["Pickup Requested", "Confirmed"]:
                            if st.button(f"🚫 Cancel Request ({r['id']})", key=f"can_req_{r['id']}"):
                                database.update_request_status(r['id'], "Cancelled", r['ngo_name'], "NGO cancelled pickup")
                                st.warning("Request cancelled; portions returned to listing.")
                                st.rerun()

    # ---------------- 6. COLLECTION AND DELIVERY STATUS ----------------
    elif active_section.startswith("6."):
        st.markdown('<div class="sec-header">🚚 Collection & Delivery Status — Real-Time Food Transport</div>', unsafe_allow_html=True)
        st.write("Live status tracker for all active food recovery operations in transit:")

        all_reqs = database.get_all_pickup_requests()
        in_transit = [r for r in all_reqs if r["status"] in ["Confirmed", "Collected"]]

        if not in_transit:
            st.info("No pickups currently confirmed or in transit. Check 'Available Food Donations' to submit requests.")
        else:
            for r in in_transit:
                st.markdown(f"""
                <div class="metric-card" style="border-left:6px solid #2980B9;">
                    <div style="display:flex; justify-content:space-between;">
                        <span style="font-size:1.15rem; font-weight:700;">{r['ngo_name']} ➔ {r['donor_name']}</span>
                        {render_status_badge(r['status'])}
                    </div>
                    <div style="margin-top:6px;"><strong>Food Items:</strong> {r['food_items']} ({r['requested_quantity']} portions)</div>
                    <div style="margin-top:4px;">📍 <strong>Pickup Site:</strong> {r['location']} | ⏰ <strong>Pickup Time:</strong> {r['proposed_pickup_time']}</div>
                    <div style="margin-top:4px;">📞 <strong>Donor Contact:</strong> <code>{r['private_contact']}</code></div>
                </div>
                """, unsafe_allow_html=True)
                
                c_btn1, c_btn2 = st.columns([2, 5])
                with c_btn1:
                    if r['status'] == "Confirmed":
                        if st.button(f"🚗 Record Pickup Handover ({r['id']})", key=f"trans_col_{r['id']}", type="primary"):
                            database.update_request_status(r['id'], "Collected", r['ngo_name'], "Physical handover complete")
                            st.rerun()
                    elif r['status'] == "Collected":
                        if st.button(f"🏠 Record Final Delivery ({r['id']})", key=f"trans_del_{r['id']}", type="primary"):
                            database.update_request_status(r['id'], "Delivered", r['ngo_name'], "Final delivery confirmed")
                            st.rerun()

    # ---------------- 7. NGO IMPACT SUMMARY ----------------
    elif active_section.startswith("7."):
        st.markdown('<div class="sec-header">🌱 NGO Food Recovery Impact Summary</div>', unsafe_allow_html=True)
        st.write("Verified metrics based exclusively on recorded requests and deliveries:")

        ngo_metrics = database.get_ngo_impact_metrics()

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Pickup Requests Submitted</div>
                <div class="metric-val">{ngo_metrics['total_requests']} requests</div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Requests Accepted by Donors</div>
                <div class="metric-val" style="color:#2980B9;">{ngo_metrics['requests_accepted']} accepted</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Portions Committed / Confirmed</div>
                <div class="metric-val" style="color:#2980B9;">{ngo_metrics['portions_committed']:,} portions</div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Portions Collected by Vans</div>
                <div class="metric-val" style="color:#E67E22;">{ngo_metrics['portions_collected']:,} portions</div>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Portions Marked Delivered</div>
                <div class="metric-val" style="color:#27AE60;">{ngo_metrics['portions_delivered']:,} portions</div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Completed Deliveries</div>
                <div class="metric-val" style="color:#27AE60;">{ngo_metrics['completed_pickups']} deliveries</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("##### 📥 Export NGO Recovery Operations Log (CSV)")
        
        reqs = database.get_all_pickup_requests()
        if reqs:
            df_req_exp = pd.DataFrame(reqs)
            # Remove private contacts for public export safety
            df_req_safe = df_req_exp.drop(columns=["private_contact"], errors="ignore")
            csv_data = df_req_safe.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Export NGO Pickup Requests (CSV)",
                data=csv_data,
                file_name="annrakshak_ngo_pickup_requests.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.info("No request records to export.")
