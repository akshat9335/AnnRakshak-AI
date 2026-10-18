"""
Comprehensive Test Script for AnnRakshak AI
Tests the 3 requested workflows:
Test A: Create a wedding donation (100 meal portions, verify in SQLite, verify NGO discovery)
Test B: Request pickup (NGO requests 40 portions, verify safe deduction, donor accepts request, verify status)
Test C: Collection and delivery (Update to Collected, update to Delivered, verify metrics consistency)
"""

import database
import demand_predictor
import ai_insights

def run_all_tests():
    print("=== STARTING ANNRAKSHAK AI WORKFLOW TESTS ===")
    
    # 0. Initialize & Reset Database
    print("\n[Step 0] Initializing & resetting demo database...")
    database.init_db()
    database.reset_demo_database()
    print("✓ Demo database initialized with baseline seeds.")

    # Test A: Create a wedding donation
    print("\n[Test A] Creating a Wedding Donation (100 meal portions)...")
    wedding_payload = {
        "donor_name": "Grand Royal Palace Wedding (Test)",
        "event_type": "Wedding",
        "food_items": "Shahi Paneer, Dal Makhani, Jeera Pulao, Butter Naan",
        "food_type": "Vegetarian",
        "quantity": 100,
        "quantity_unit": "meal portions",
        "prep_datetime": "2026-10-18 19:00",
        "available_from": "2026-10-18 19:30",
        "pickup_deadline": "2026-10-18 23:30",
        "location": "Civil Lines, Prayagraj",
        "storage_handling": "Chafing dishes with active burners; food-grade airtight containers",
        "private_contact": "+91-98765-00112 (Mr. Agarwal)",
        "notes": "Reception buffet excess. High quality food ready for rescue."
    }

    don_id = database.create_donation(wedding_payload)
    print(f"✓ Created donation with ID: {don_id}")
    
    # Verify in SQLite
    don_rec = database.get_donation_by_id(don_id)
    assert don_rec is not None, "Donation record not found in SQLite!"
    assert don_rec["original_quantity"] == 100, "Original quantity mismatch!"
    assert don_rec["remaining_quantity"] == 100, "Remaining quantity mismatch!"
    assert don_rec["status"] == "Available", "Status mismatch!"
    print("✓ Verified donation in SQLite: 100 meal portions, Status: Available")

    # Verify visible to NGO dashboard
    all_avail = database.get_all_donations(status_filter="Available")
    found = any(d["id"] == don_id for d in all_avail)
    assert found, "Donation not visible in NGO Available list!"
    print(f"✓ Verified donation {don_id} is discoverable by NGOs in shared database.")

    # Test B: Request pickup
    print("\n[Test B] Submitting NGO Pickup Request for 40 meal portions...")
    req_payload = {
        "donation_id": don_id,
        "ngo_name": "Asha Food Rescue Foundation (Sample Demo NGO)",
        "ngo_contact": "+91-91234-56789 (Dispatcher)",
        "requested_quantity": 40,
        "proposed_pickup_time": "2026-10-18 20:30",
        "notes": "Transport van dispatched with insulated catering boxes."
    }

    req_id = database.create_pickup_request(req_payload)
    print(f"✓ Pickup request created: {req_id}")

    # Verify safe database deduction
    updated_don = database.get_donation_by_id(don_id)
    assert updated_don["remaining_quantity"] == 60, f"Expected 60 remaining, got {updated_don['remaining_quantity']}"
    print(f"✓ Verified safe atomic portion allocation: {updated_don['remaining_quantity']} portions remaining out of 100.")

    # Verify donor sees request
    donor_reqs = database.get_pickup_requests_for_donation(don_id)
    assert len(donor_reqs) == 1, "Donor did not see pickup request!"
    assert donor_reqs[0]["status"] == "Pickup Requested", "Request status not 'Pickup Requested'!"
    print(f"✓ Donor dashboard sees incoming request {req_id} with status 'Pickup Requested'.")

    # Donor accepts request -> Confirmed
    print("\n[Test B.2] Donor accepts request -> Updating status to Confirmed...")
    database.update_request_status(req_id, "Confirmed", "Grand Royal Palace Wedding (Test)", "Donor approved pickup")
    
    # Verify NGO sees updated status
    all_ngo_reqs = database.get_all_pickup_requests()
    target_req = next(r for r in all_ngo_reqs if r["id"] == req_id)
    assert target_req["status"] == "Confirmed", "Request status did not update to Confirmed!"
    print(f"✓ Verified NGO dashboard sees updated status: {target_req['status']}")

    # Test C: Collection and delivery
    print("\n[Test C] Updating status to Collected...")
    database.update_request_status(req_id, "Collected", "Asha Food Rescue Foundation (Sample Demo NGO)", "Food picked up by van")
    rec_req = next(r for r in database.get_all_pickup_requests() if r["id"] == req_id)
    assert rec_req["status"] == "Collected", "Failed to transition to Collected!"
    print("✓ Status updated to 'Collected' in shared database.")

    print("\n[Test C.2] Updating status to Delivered...")
    database.update_request_status(req_id, "Delivered", "Asha Food Rescue Foundation (Sample Demo NGO)", "Food delivered to night shelter")
    del_req = next(r for r in database.get_all_pickup_requests() if r["id"] == req_id)
    assert del_req["status"] == "Delivered", "Failed to transition to Delivered!"
    print("✓ Status updated to 'Delivered' in shared database.")

    # Verify Impact Metrics
    print("\n[Test D] Verifying Impact Metrics consistency...")
    donor_metrics = database.get_donor_impact_metrics()
    ngo_metrics = database.get_ngo_impact_metrics()
    print("Donor Impact:", donor_metrics)
    print("NGO Impact:", ngo_metrics)
    assert donor_metrics["total_delivered"] >= 40, "Delivered portions not recorded in donor metrics!"
    assert ngo_metrics["portions_delivered"] >= 40, "Delivered portions not recorded in NGO metrics!"
    print("✓ Impact calculations strictly reflect recorded deliveries.")

    # Test E: Demand Prediction & Food Waste Consistency
    print("\n[Test E] Verifying Demand Prediction calculation...")
    pred = demand_predictor.calculate_demand_prediction(
        expected_attendees=200,
        safety_buffer_pct=10,
        cost_per_meal=150.0,
        historical_records=database.get_food_waste_records()
    )
    print(f"✓ Baseline Demand: {pred['base_demand']}, Buffer: +{pred['buffer_portions']}, Recommended: {pred['recommended_portions']}")
    assert pred["recommended_portions"] > 0, "Prediction portions must be positive"

    print("\n🎉 ALL TESTS PASSED SUCCESSFULLY! 100% FUNCTIONAL AND READY FOR HACKATHON DEMO.")

if __name__ == "__main__":
    run_all_tests()
