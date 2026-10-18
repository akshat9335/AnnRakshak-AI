# 🍲 AnnRakshak AI (अन्नरक्षक AI)

> **Hindi Tagline:** अन्न बचाओ, बर्बादी घटाओ।  
> **English Tagline:** Predict demand. Prevent waste. Rescue surplus.

**AnnRakshak AI** is an AI-powered food waste prevention and surplus food donation platform built for hackathons, community organizers, caterers, banquet halls, hostels, restaurants, and food recovery NGOs.

---

## 📌 Problem Statement
Massive quantities of freshly prepared, high-quality food are discarded daily at Indian weddings, birthday parties, college events, hostel messes, and restaurants due to RSVP dropouts, unpredictable turnout, and overproduction. Meanwhile, local night shelters and food recovery organizations face severe supply volatility and lack a unified, real-time coordination tool to discover and safely rescue surplus food before it spoils.

## 💡 Solution Overview
AnnRakshak AI bridges the gap between surplus generators and local recovery networks through:
1. **Real-Time Surplus Listings:** Families and caterers publish donation lots with precise preparation times, storage protocols, and pickup deadlines.
2. **Safe Multi-Role Coordination:** NGOs discover available food lots, request specific portion quantities, and execute a controlled lifecycle (`Available → Pickup Requested → Confirmed → Collected → Delivered`).
3. **Food Waste Tracking:** Commercial kitchens log prepared vs. consumed quantities to compute discard percentages, leftover costs, and edible surpluses.
4. **Transparent Demand Prediction:** An empirical baseline model that uses historical consumption rates and configurable safety buffers to guide food preparation.
5. **Gemma 4 AI Insights:** Grounded food waste analytics powered by the official Google Gen AI SDK (`google-genai`), backed by a deterministic rule-based demo engine.

---

## 🏛️ Application Architecture & Technology Stack

- **Web Frontend & UI/UX:** Streamlit with custom CSS (Warm off-white `#FDFBF7`, Forest Green `#1E4B35`, Soft Orange `#E67E22`).
- **Data Visualizations:** Plotly Express & Plotly Graph Objects (Interactive donut charts, grouped portion bars, waste trend lines).
- **Backend & Formulas:** Python 3.10+ with pandas for analytical queries.
- **Database:** SQLite (`annrakshak.db`) with foreign key constraints, atomic transactions, parameterized queries, and idempotent seeding.
- **AI Integration:** Official Google Gen AI SDK (`google-genai`) interfacing with Gemma models (`gemma-2-9b-it`, `gemma-2-27b-it`) or Gemini fallback.
- **Demo Mode Engine:** Deterministic rule-based engine when API keys are absent, guaranteeing 100% offline hackathon reliability without hallucinating statistics.

---

## 👥 Exactly Two Main Role-Based Dashboards

AnnRakshak AI consolidates all features within **exactly two role-based dashboards** connected to a **single shared SQLite database**:

### 👨‍🍳 Dashboard A: Donor Dashboard
*Target audience: Families, banquet halls, caterers, hotel chefs, canteen managers.*
1. **Overview:** Real-time KPI summary cards (donations listed, portions offered, pending requests, confirmed pickups, portions delivered, waste logged, financial loss) + 4 interactive Plotly charts.
2. **Donate Food:** Validated listing form with preparation timestamp, pickup deadline, storage details, and a 1-click **"Load Wedding Demo"** button.
3. **My Donations:** Manage created listings, view remaining vs. original portions, accept or reject pending NGO requests, or cancel eligible listings.
4. **NGO Pickup Requests:** Centralized inbox to review and approve/reject volunteer requests.
5. **Food Waste Tracker:** Audit meals prepared vs. consumed; calculates discard percentage and financial loss in ₹.
6. **Demand Prediction:** Transparent attendance-based demand estimator using observed consumption ratios and safety buffer sliders.
7. **Gemma 4 AI Insights:** Click-to-run AI audit interpreting waste patterns and suggesting overproduction prevention protocols.
8. **Impact Summary & CSV Export:** Verified donor metrics with sanitized CSV download options.

### 🤝 Dashboard B: NGO Dashboard
*Target audience: Food rescue charities, food banks, volunteer squads, shelter homes.*
1. **Overview:** Recovery operational cards (requests submitted, accepted, collected, delivered) + live surplus feed.
2. **Available Food Donations:** Live discovery feed of surplus food with quantity badges and preparation times. Private donor contacts remain masked for privacy.
3. **Search & Filters:** Instant search by keyword, meal category, minimum portions required, and locality.
4. **Request Pickup:** Safe portion reservation portal preventing double-allocation and race conditions.
5. **My Pickup Requests:** Track request status (`Pickup Requested → Confirmed → Collected → Delivered`). Authorized donor contact details unlock automatically upon confirmation.
6. **Collection and Delivery Status:** Logistics tracker to mark handovers from event sites to shelter homes.
7. **Impact Summary & CSV Export:** Downloadable operational logs and verified meal delivery counts.

---

## 🚀 Installation & Launch Instructions

### 1. Prerequisites
- Python 3.10 or higher
- Git

### 2. Clone the Repository
```bash
git clone <repo-url>
cd proje
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. (Optional) Configure Google Gen AI API Key
Copy the example environment template and insert your API key:
```bash
copy .env.example .env
```
Add your key inside `.env` or enter it directly inside the app under the Gemma 4 configuration panel:
```env
GEMINI_API_KEY="your_api_key_here"
```
*(If no API key is set, the app will automatically use its transparent rule-based demo engine.)*

### 5. Launch the Web Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 🧪 Automated Testing
To run the automated verification test suite:
```bash
python test_workflows.py
```
This tests:
- **Test A:** Wedding donation creation & SQLite persistence.
- **Test B:** NGO pickup request submission, safe quantity deduction, and donor acceptance.
- **Test C:** Status transition from Confirmed to Collected and Delivered, verifying impact metric synchronization.

---

## 🎬 3-Minute Hackathon Demo Workflow

1. **Launch App:** Open `http://localhost:8501`. Notice the **DEMO MODE ACTIVE** banner and brand tagline.
2. **Step 1 (Donor Role):**
   - In sidebar, ensure `Dashboard A: Donor Dashboard` is selected.
   - Go to `2. Donate Food`. Click **"✨ Load Wedding Demo Form Values"**.
   - Review pre-filled fields (120 portions, wedding pulao/paneer, Prayagraj). Click **"🚀 Publish Donation Listing"**.
   - Notice the green confirmation and balloon celebration.
3. **Step 2 (NGO Role):**
   - Switch sidebar radio to `Dashboard B: NGO Dashboard`.
   - Go to `2. Available Food Donations`. Verify the wedding listing appears instantly.
   - Go to `4. Request Pickup`. Select the listing, choose 40 portions, and click **"📨 Submit Pickup Request"**.
4. **Step 3 (Donor Acceptance):**
   - Switch back to `Dashboard A: Donor Dashboard` ➔ `4. NGO Pickup Requests`.
   - View the incoming request for 40 portions. Click **"✅ Accept Request"**.
5. **Step 4 (NGO Delivery & Handover):**
   - Switch to `Dashboard B: NGO Dashboard` ➔ `5. My Pickup Requests`.
   - Notice status is now **Confirmed** and donor's phone number is unlocked!
   - Click **"🚗 Mark Collected by Volunteer"**, then click **"🏠 Mark Delivered to Beneficiaries"**.
6. **Step 5 (Analytics & Impact):**
   - Go to `7. Gemma 4 AI Insights` in the Donor Dashboard.
   - Click **"🔍 Analyze Food Waste with Gemma 4"** to view real-time pattern analysis and recommendations.
   - View `8. Impact Summary` to inspect updated delivery numbers and click **Export CSV**.

---

## 🛡️ Food Safety & Privacy Safeguards
- **No Autonomous Certification:** AnnRakshak AI makes no claim that AI models can certify microbiological food safety. Handover inspection by humans is mandatory.
- **Privacy by Design:** Private phone numbers and donor contacts are concealed from public donation cards and exposed only to verified NGOs after request confirmation.
- **Zero Hallucination:** Numerical values and metrics are calculated strictly by deterministic Python logic; AI models only provide qualitative interpretations.

---

## 📄 License
This project is licensed under the [MIT License](LICENSE).
