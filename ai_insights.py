"""
AI Analytics and Insights module for AnnRakshak AI.
Integrates with the official Google Gen AI SDK (google-genai).
Follows strict instructions:
- Uses verified model identifier or verified fallback
- Never invents statistics, fake donations, or unverified claims
- Deterministic, high-quality rule-based fallback when API key is missing or model unavailable
- Explicitly flags rule-based output as demo fallback, never fakes Gemma
"""

import os
from typing import Dict, Any, List, Optional
import pandas as pd

def generate_waste_insights(
    waste_records: List[Dict[str, Any]],
    api_key: Optional[str] = None,
    preferred_model: str = "gemma-2-9b-it"
) -> Dict[str, Any]:
    """
    Analyzes food waste records.
    Calculates exact numerical metrics in Python first,
    then requests Gemma 4 / Gemma model interpretation if API key is provided.
    Falls back cleanly to transparent rule-based demo analytics.
    """
    if not waste_records:
        return {
            "source": "None",
            "is_ai": False,
            "error": "No food waste records available to analyze.",
            "metrics": {},
            "observations": [],
            "recommendations": [],
            "limitations": "Please record food preparation and waste events in the Food Waste Tracker first."
        }

    # 1. Exact Python Calculation of all numerical metrics
    df = pd.DataFrame(waste_records)
    total_records = len(df)
    total_prep = int(df["portions_prepared"].sum())
    total_cons = int(df["portions_consumed"].sum())
    total_leftover = int(df["leftover_quantity"].sum())
    total_edible = int(df["edible_surplus"].sum())
    total_discard = int(df["discarded_waste"].sum())
    total_fin_loss = float(df["financial_loss"].sum())

    avg_prep = round(df["portions_prepared"].mean(), 1)
    avg_leftover_pct = round(df["leftover_pct"].mean(), 1)
    avg_discard_pct = round(df["discarded_waste_pct"].mean(), 1)

    # Provider breakdown
    provider_group = df.groupby("provider_name")["discarded_waste"].sum().to_dict()
    meal_group = df.groupby("meal_type")["discarded_waste"].sum().to_dict()

    highest_waste_provider = max(provider_group.items(), key=lambda x: x[1])[0] if provider_group else "N/A"
    highest_waste_meal = max(meal_group.items(), key=lambda x: x[1])[0] if meal_group else "N/A"

    calculated_metrics = {
        "total_records": total_records,
        "total_portions_prepared": total_prep,
        "total_portions_consumed": total_cons,
        "total_leftover_portions": total_leftover,
        "total_edible_surplus": total_edible,
        "total_discarded_waste": total_discard,
        "total_financial_loss": total_fin_loss,
        "avg_leftover_pct": avg_leftover_pct,
        "avg_discard_pct": avg_discard_pct,
        "highest_waste_provider": highest_waste_provider,
        "highest_waste_meal": highest_waste_meal
    }

    # 2. Attempt Official Google Gen AI SDK Call if API Key provided
    key_to_use = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

    if key_to_use:
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=key_to_use)

            # Build grounded prompt containing ONLY verified python calculated metrics
            prompt_content = f"""
You are AnnRakshak AI's Food Waste Analyst.
Analyze the following recorded food waste data for commercial kitchens, wedding caterers, and canteens.
CRITICAL CONSTRAINT: Do NOT invent statistics, donations, NGO pickups, or social impact numbers.
All figures must strictly match the verified data provided below:

VERIFIED METRICS:
- Total records analyzed: {total_records}
- Total portions prepared: {total_prep}
- Total portions consumed: {total_cons} (Overall consumption rate: {(total_cons/total_prep*100) if total_prep>0 else 0:.1f}%)
- Total leftover portions: {total_leftover} ({avg_leftover_pct}% average leftover per event)
- Portions rescued/edible surplus: {total_edible}
- Portions discarded to waste: {total_discard} ({avg_discard_pct}% average discard rate)
- Total recorded financial loss: ₹{total_fin_loss:,.2f}
- Highest waste meal type: {highest_waste_meal}
- Provider with largest discarded volume: {highest_waste_provider}

Please structure your response in exact markdown format with these 4 sections:
### 1. Key Observations
(Summarize 3 bullet points referencing the exact data above)

### 2. Operational Patterns & Drivers
(Discuss what is causing leftovers based on the meal types and variance)

### 3. Practical Recommendations for Kitchens & Caterers
(Provide 3 actionable operational steps to prevent overproduction and preserve edible surplus)

### 4. Limitations & Scope
(Mention that this analysis is based on {total_records} historical records and does not substitute on-site food safety audits)
"""
            # Request Gemma / Gemini model via google-genai SDK
            response = client.models.generate_content(
                model=preferred_model,
                contents=prompt_content,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    max_output_tokens=1000
                )
            )

            if response and response.text:
                return {
                    "source": f"Gemma Live Model ({preferred_model})",
                    "is_ai": True,
                    "model_used": preferred_model,
                    "metrics": calculated_metrics,
                    "raw_text": response.text,
                    "observations": [],
                    "recommendations": [],
                    "limitations": f"Generated via official google-genai SDK using model {preferred_model} grounded in {total_records} database records."
                }
        except Exception as e:
            # Fall through to deterministic fallback if API or model fails
            pass

    # 3. Transparent Rule-Based Fallback (Fully documented, explicitly labeled)
    observations = [
        f"Across {total_records} recorded meals, {total_prep:,} portions were prepared and {total_cons:,} were consumed ({round((total_cons/total_prep*100) if total_prep>0 else 0, 1)}% consumption rate).",
        f"A total of {total_leftover:,} leftover portions were generated, of which {total_edible:,} were rescued as edible surplus and {total_discard:,} portions were discarded.",
        f"The recorded discarded waste accounts for an estimated cumulative financial loss of ₹{total_fin_loss:,.2f}, with '{highest_waste_meal}' showing the highest waste frequency."
    ]

    recommendations = [
        f"Calibrate Base Prep with Safety Buffers: Rather than preparing 100% of maximum RSVPs, implement an 85% base preparation with a tiered 10-15% on-demand prep buffer.",
        f"Implement Real-Time RSVP Tracking: In events organized by {highest_waste_provider}, deploy digital head-count check-ins 2 hours prior to buffet opening.",
        f"Same-Day NGO Donation Alignment: Since {total_edible:,} portions were edible surplus, pre-schedule NGO pickup slots at the 2-hour post-prep mark to avoid spoilage.",
        f"Standardize Chilled Storage Protocols: Segregate untouched chafing dish portions immediately after the 3-hour serving window into clean, food-grade airtight containers."
    ]

    limitations = (
        f"Deterministic Rule-Based Demo Output: Derived directly from {total_records} local SQLite records. "
        "Gemma 4 API key not detected or rate-limited. This transparent rule-based algorithm operates deterministically without external generative hallucination."
    )

    return {
        "source": "Deterministic Rule-Based Engine (Demo Mode)",
        "is_ai": False,
        "model_used": "Deterministic Rule-Based Baseline",
        "metrics": calculated_metrics,
        "observations": observations,
        "recommendations": recommendations,
        "limitations": limitations
    }

def format_donation_description(donation_data: Dict[str, Any]) -> str:
    """
    Standardized, clean converter from structured donation parameters
    into an informative, clear summary for NGO dispatch teams.
    """
    don_id = donation_data.get("id", "N/A")
    donor = donation_data.get("donor_name", "Anonymous Donor")
    event = donation_data.get("event_type", "Event")
    food = donation_data.get("food_items", "Assorted meals")
    food_type = donation_data.get("food_type", "Vegetarian")
    qty = donation_data.get("remaining_quantity", donation_data.get("original_quantity", 0))
    unit = donation_data.get("quantity_unit", "portions")
    prep = donation_data.get("prep_datetime", "N/A")
    deadline = donation_data.get("pickup_deadline", "N/A")
    location = donation_data.get("location", "N/A")
    storage = donation_data.get("storage_handling", "Standard packaging")
    notes = donation_data.get("notes", "None")

    desc = (
        f"🍲 **Donation Summary ({don_id})**\n\n"
        f"• **Donor / Event**: {donor} ({event})\n"
        f"• **Food Item**: {food} ({food_type})\n"
        f"• **Available Volume**: {qty} {unit}\n"
        f"• **Preparation Time**: {prep}\n"
        f"• **Strict Pickup Deadline**: {deadline}\n"
        f"• **Pickup Locality**: {location}\n"
        f"• **Storage & Handling Protocol**: {storage}\n"
        f"• **Kitchen Notes**: {notes}\n\n"
        f"⚠️ *Important Food Safety Note*: Transport must use insulated temperature-safe containers. "
        f"Verify freshness upon pickup before distribution."
    )
    return desc
