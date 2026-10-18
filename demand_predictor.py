"""
Demand Prediction module for AnnRakshak AI.
Provides transparent, deterministic baseline demand estimation for event organizers,
caterers, hostels, and mess managers using historical consumption ratios and configurable safety buffers.
"""

from typing import Dict, Any, List, Optional
import pandas as pd

def calculate_demand_prediction(
    expected_attendees: int,
    safety_buffer_pct: float,
    cost_per_meal: float,
    historical_records: Optional[List[Dict[str, Any]]] = None,
    filter_provider: Optional[str] = None,
    filter_meal_type: Optional[str] = None
) -> Dict[str, Any]:
    """
    Transparent baseline demand estimator:
    - If relevant historical records exist:
        Computes observed average consumption ratio = (consumed / prepared) or (consumed / estimated attendees).
        Calculates baseline demand = expected_attendees * observed_avg_ratio.
        Applies safety buffer = baseline_demand * (1 + safety_buffer_pct / 100).
    - If insufficient historical data (< 2 matching records):
        Uses expected attendance directly as baseline demand with safety buffer.
    """
    if expected_attendees <= 0:
        raise ValueError("Expected attendees must be greater than 0.")
    if safety_buffer_pct < 0 or safety_buffer_pct > 50:
        raise ValueError("Safety buffer must be between 0% and 50%.")
    if cost_per_meal < 0:
        raise ValueError("Cost per meal cannot be negative.")

    relevant_records = []
    if historical_records:
        for r in historical_records:
            match = True
            if filter_provider and filter_provider != "All" and r.get("provider_name") != filter_provider:
                match = False
            if filter_meal_type and filter_meal_type != "All" and r.get("meal_type") != filter_meal_type:
                match = False
            if match and r.get("portions_prepared", 0) > 0:
                relevant_records.append(r)

    has_history = len(relevant_records) >= 2
    method_used = ""
    history_summary = {}

    if has_history:
        total_prep = sum(r["portions_prepared"] for r in relevant_records)
        total_cons = sum(r["portions_consumed"] for r in relevant_records)
        total_waste = sum(r["discarded_waste"] for r in relevant_records)
        total_leftover = sum(r["leftover_quantity"] for r in relevant_records)
        
        # Observed consumption efficiency
        avg_consumption_ratio = total_cons / total_prep if total_prep > 0 else 0.85
        avg_waste_pct = (total_waste / total_prep) * 100 if total_prep > 0 else 0.0

        # Baseline demand: In events, typically a fraction of RSVP turns out / eats full meal
        # E.g. if observed ratio is 82%, we anticipate each attendee consumes ~0.85 - 0.95 portion
        portion_factor = min(1.0, max(0.70, avg_consumption_ratio))
        base_demand = round(expected_attendees * portion_factor)
        
        buffer_portions = round(base_demand * (safety_buffer_pct / 100.0))
        recommended_portions = base_demand + buffer_portions
        
        method_used = (
            f"Historical Data Empirical Model ({len(relevant_records)} matched records). "
            f"Observed average meal consumption ratio was {avg_consumption_ratio*100:.1f}%. "
            f"Baseline portion factor set to {portion_factor:.2f} per expected attendee, "
            f"plus a {safety_buffer_pct:.0f}% safety margin."
        )

        history_summary = {
            "records_analyzed": len(relevant_records),
            "historical_prepared": total_prep,
            "historical_consumed": total_cons,
            "historical_leftover": total_leftover,
            "historical_waste": total_waste,
            "avg_consumption_pct": round(avg_consumption_ratio * 100, 1),
            "avg_waste_pct": round(avg_waste_pct, 1)
        }
    else:
        # Transparent rule-based fallback without sufficient historical data
        base_demand = expected_attendees
        buffer_portions = round(base_demand * (safety_buffer_pct / 100.0))
        recommended_portions = base_demand + buffer_portions
        method_used = (
            f"Direct Attendance Planning Model (Insufficient historical data: {len(relevant_records)} matching records). "
            f"Assumes 1 standard meal portion per RSVP ({expected_attendees}) plus a {safety_buffer_pct:.0f}% safety buffer ({buffer_portions} portions)."
        )
        history_summary = {
            "records_analyzed": len(relevant_records),
            "note": "Fewer than 2 historical records available. Direct attendance fallback applied."
        }

    expected_total_cost = round(recommended_portions * cost_per_meal, 2)
    buffer_cost = round(buffer_portions * cost_per_meal, 2)

    return {
        "expected_attendees": expected_attendees,
        "base_demand": base_demand,
        "safety_buffer_pct": safety_buffer_pct,
        "buffer_portions": buffer_portions,
        "recommended_portions": recommended_portions,
        "cost_per_meal": cost_per_meal,
        "expected_total_cost": expected_total_cost,
        "buffer_cost": buffer_cost,
        "method_used": method_used,
        "has_history": has_history,
        "history_summary": history_summary
    }
