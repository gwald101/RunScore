## **📝 Updated Product Requirements Document (PRD)**

### **1. Goal, Metrics, and Core Logic**

| Field | Detail |
|---|---|
| Product Name | RunScore (Confirmed Placeholder) |
| Goal | Provide runners with a clear, actionable, and science-backed "Critical Score" to guide their weekly mileage and minimize injury risk. |
| Success Metrics (MVP) | 1. Integration Success: 95% of users successfully connect their Strava account. 
2. Weekly Usage: 40% of connected users view their score at least once per week. 
3. Retention: 7-day retention rate of 50%. |
| Weekly Definition | Monday 12:00 AM to Sunday 11:59 PM (User's local timezone). |

#### **Critical Score Calculation (ACWR)**

The core logic remains the ratio of Acute to Chronic Mileage.

- **Acute Mileage (AC):** Total running mileage of the current week (Week X).

- **Chronic Mileage (CR):** The simple average of the total running mileage across the four complete weeks immediately preceding Week X (Weeks X−1,X−2,X−3,X−4).

Critical Score = Acute Mileage (Week X)​ / Chronic Mileage (Avg. Weeks X−1 to X−4)

#### **Recommended Capacity Calculation**

The recommended maximum safe mileage for the upcoming week (Week X+1) is strictly defined by the maximum safe ACWR threshold of **1.25**.

Recommended Max Mileage (Week X+1)=1.25×Chronic Mileage (Avg. Weeks X−1 to X−4)

### **2. Features & Technical Specifications (Web MVP)**

The MVP will be **extremely focused** to facilitate rapid launch and validation.

#### **A. User Authentication & Profile (New Scope)**

| Feature | Specification | Technical Note |
|---|---|---|
| Authentication (P0) | Users register and log in using Phone Number (SMS verification/OTP) or Email/Password (TBD based on complexity). | Requires a secure authentication service (e.g., Firebase Auth, Auth0, or custom backend). |
| Strava Connection (P0) | After sign-up, users must link their account via "Connect with Strava" (OAuth 2.0). | We must store the Strava Access Token securely to pull data. |
| Data Ingestion (P0) | Pull running activities from Strava for the last 5 complete weeks plus the activities from the current week. | Activity type filtering is critical: only count "Run" or "Virtual Run." |

#### **B. User Interface (UI) and Display**

The UI will be a single, focused dashboard page.

| Component | Specification | Description / UI Note |
|---|---|---|
| Current Score Display | Large, prominent display of the calculated Critical Score. | Must be the first thing the user sees. |
| Status Indicator | Color-coded feedback on the risk level. | Gray (Score <1.10), Green (1.10≤Score≤1.25), Yellow (1.25<Score≤1.3),  Red (Score>1.3). |
| Mileage Breakdown | Clear display of the input values. | Show: 1. Acute Mileage (This Week's Total), 2. Chronic Mileage (Avg. of Last 4 Weeks). |
| Capacity Statement | The single, most actionable metric. | "Recommended Max Mileage for Next Week: XX.X miles." |

#### **C. Backend & Data Handling**

- **Technology Stack:** Python/Django or Node.js/Express (for rapid development) for the backend API, coupled with a robust SQL database (PostgreSQL).

- **Data Structure:** The backend must store user data (ID, Auth info) and a secure, time-stamped log of weekly mileage totals to facilitate fast score calculation without constantly querying Strava's API.

- **API Management:** Implement proper rate-limiting and error handling for the Strava API, ensuring refresh tokens are managed securely.


## 
## 🗺️ Revised Development Roadmap

The roadmap is structured across the three requested platforms, prioritizing the core features for each phase.

### **Phase 1: Web MVP (6-8 Weeks) 🚀**

| Epic | Features | Status |
|---|---|---|
| Auth & Data | Phone Number/Email Authentication. Secure Strava OAuth Integration. Secure storage of Strava tokens. | P0 (Must Have) |
| Core Logic | Backend API for calculating Acute/Chronic Mileage and Critical Score. Logic for filtering non-running activities. | P0 |
| Single Page UI | Single-page display: Score, Status Color, Mileage Breakdown, and Next Week Capacity. | P0 |
| Non-MVP Features | Implement basic database models to support future features (e.g., historical records). | P1 (Nice to Have) |

Export to Sheets

### **Phase 2: iOS App (12-16 Weeks) 📱**

- **Focus:** Native mobile experience, advanced visualization, and user engagement via notifications.

- **Features:**

- **Native App Development:** Full feature parity with the Web MVP.

- **Historical View (P1):** **12-week chart** of Critical Score vs. Actual Mileage.

- **Profile Page (P1):** User settings, ability to unlink Strava, and view calculation settings.

- **Mid-Week Alerts (P1):** Push notifications to alert the user if they are projected to exceed a score of 1.25 by the end of the current week.

### **Phase 3: Android App & Expansion (Ongoing) 🤖**

- **Focus:** Market coverage and expanding core value.

- **Features:**

- **Android App Development:** Full feature parity with the iOS app.

- **Integration Expansion (P2):** Implement integration with **Garmin Connect** API.

- **User Customization (P2):** Allow users to **adjust the 1.25 threshold** (e.g., to 1.35 for experienced runners).

- **Monetization Hooks (P3):** Design system for future subscription tier (e.g., showing a locked **"Advanced Insights"** section).

## 
## **⚙️ Technical Specifications: Web MVP API Integration**

This section details the high-level technical requirements for the two critical integrations in the Web MVP: **User Authentication** (Phone/Email) and **External Data Integration** (Strava).


### **1. User Authentication (Auth)**

Since we are moving away from simple "Log in with Strava" and implementing a custom user base, we need a robust, scalable system.

#### **A. Chosen Method: Phone Number/Email & OTP/Password**

| Component | Technical Specification | Rationale/Requirement |
|---|---|---|
| User Identity | Store User_ID, Phone_Number (unique), Email (optional, for recovery), and Hashed Password (if using password auth). | Phone number provides a unique, non-P.I.I. primary identifier for runners. |
| Authentication Flow | Phone Number + OTP (One-Time Password) via SMS or Email + Password. | OTP is often preferred for mobile-centric apps as it avoids password management complexity. Requirement: Must integrate with a reliable SMS provider (e.g., Twilio, AWS SNS). |
| Session Management | Use JWT (JSON Web Tokens) for authenticated sessions. | JWTs are stateless and highly efficient for securing backend API calls between the web client and our server. |

Export to Sheets

#### **B. Backend API Endpoints (Auth)**

- `POST /api/v1/auth/register`: Create a new user profile.

- `POST /api/v1/auth/login`: Authenticate user and return a JWT.

- `POST /api/v1/auth/verify_otp`: Validate the received OTP.

- `POST /api/v1/auth/logout`: Invalidate the current session's JWT.


### **2. Strava Integration (Data Ingestion)**

The Strava integration is the engine of the app, providing the mileage data for the **Critical Score** calculation. For the MVP, data retrieval will be **on-demand** (triggered by user login/dashboard refresh) to prioritize the freshest data and simplify the initial backend architecture, deferring complex polling mechanisms.

#### **A. Authorization Flow: OAuth 2.0**

1. **Client Configuration:** Register our app with Strava to obtain a **Client ID** and **Client Secret**.

2. **Redirection:** User clicks "Connect with Strava" and is redirected to Strava's authorization page.

3. **Permissions Scope:** We must request the `activity:read_all` scope to access the user's historical and new running activities.

4. **Token Exchange:** Strava redirects the user back to our server with an authorization code, which our backend immediately exchanges for the user's **Access Token** (short-lived) and **Refresh Token** (long-lived).

5. **Secure Storage:** The **Refresh Token** is stored securely in our database, linked to the user's `User_ID`. **Crucial:** We will use the Refresh Token to fetch a new Access Token *only* when needed.

#### **B. Data Retrieval Logic and Timing (Real-Time Update)**

| Action | Specification | Technical Note |
|---|---|---|
| Initial Fetch (P0) | Upon first connection, pull all running activities from the user for the last 6 weeks to seed the initial Chronic and Acute Mileage cache. | Filter API results by type=Run or sport_type=Running. Convert the Strava distance field (in meters) to miles for storage. |
| Real-Time Update (P0) | The current week's Acute Mileage cache will be refreshed every time the user loads the dashboard. | The backend must determine the timestamp of the last successful sync for that user. It then calls the Strava API, filtering activities that occurred since that timestamp. This minimizes the data fetched on each call and reduces the likelihood of immediate rate-limiting issues. |
| Cache Management | Update the user's weekly mileage cache with the newly retrieved data, and update the last successful sync timestamp in the user's database record. | The cache ensures that the Critical Score calculation is fast, using local data rather than waiting for an external API response. |
| Rate Limit Management | Mitigation Strategy: Implement robust error handling to detect Strava API rate limit errors (HTTP 429). If detected, serve the score using the existing cached data and display a message: "Data is temporarily delayed due to high activity." | This prioritizes UX stability over strictly real-time data when limits are reached. |

#### **C. Backend API Endpoints (Strava)**

- `GET /api/v1/data/strava/connect`: Initiate the OAuth flow.

- `GET /api/v1/data/strava/callback`: Handle the redirect from Strava and exchange the code for tokens.

- `GET /api/v1/data/score`: **(The Main Endpoint)** Calculates and returns the Critical Score and Recommended Capacity. This endpoint triggers the **Real-Time Update logic (S2.4)** before calculation.


### 3. Backend Calculation Engine

The core logic must be insulated and highly accurate.

- **Mileage Cache:** Store weekly mileage totals in a dedicated table: `user_id`, `week_start_date`, `total_mileage`.

- **Calculation Flow:**

1. User requests their score (`GET /api/v1/data/score`).

2. The engine retrieves the last 5 complete weeks of mileage from the cache.

3. It calculates Chronic Mileage (CR) by summing and dividing the 4 preceding weeks.

4. It calculates Acute Mileage (AC) for the current week.

5. It computes the **Critical Score (AC/CR)** and the **Recommended Max Mileage (CR×1.25)**.

This architecture ensures the calculation is fast (as it uses cached data) and the external API calls (to Strava) are managed asynchronously to maintain a good user experience.

### **Epic 1: Authentication & Onboarding**

| ID | User Story | Acceptance Criteria (ACs) | Priority |
|---|---|---|---|
| A1.1 | As a new user, I want to register an account using my phone number and a One-Time Password (OTP) so that I can securely log in and establish my unique identity. | 1. The user can successfully enter a phone number. 2. A valid OTP is sent via SMS. 3. The user can enter the OTP to verify the account. | P0 |
| A1.2 | As a new user, I want the option to provide my email and a password during registration so that I have an alternative login and account recovery method. | 1. The email and password fields are clearly marked as optional during registration. 2. The provided password is securely hashed and stored if entered. | P0 |
| A1.3 | As a returning user, I want to log in using my registered credentials (phone/OTP or email/password) so that I can quickly access my RunScore dashboard. | 1. Successful login takes the user directly to the main dashboard. 2. Session management (JWT) is used to maintain a persistent logged-in state. | P0 |
| A1.4 | As a registered user, I want a simple 'Settings' screen so that I can verify my account status and manage my linked services. | 1. Screen displays user's name/email/phone number. 2. Screen shows the status of the Strava connection (Connected/Disconnected). | P1 |

Export to Sheets


### **Epic 2: Strava Data Integration**

| ID | User Story | Acceptance Criteria (ACs) | Priority |
|---|---|---|---|
| S2.1 | As a newly registered user, I must be prompted to connect my Strava account, but I should be allowed to proceed without connecting. | 1. After registration, the user is presented with the Strava connection prompt. 2. The prompt includes a warning: "RunScore requires Strava data to function." 3. An option to "Connect Now" and an option to "Skip for Now" are provided. | P0 |
| S2.2 | As a user who opts to skip Strava connection, I should be brought to a holding screen that offers a button to connect so that I can easily integrate later. | 1. The holding screen clearly explains the lack of functionality without data. 2. A prominent "Connect with Strava" button is displayed on this screen. | P0 |
| S2.3 | As a user connecting to Strava, I want the system to clearly state the required permissions so that I am comfortable with the data sharing. | 1. A clear message explains that we only use running activity data and why. | P0 |
| S2.4 | As a connected user, I want my current week's mileage to update every time I open the app so that my Critical Score is based on the most recent data possible. | 1. Upon dashboard load, the app checks if the Strava Access Token needs refreshing. 2. The app queries the Strava API for recent activities (since the last update) and updates the Acute Mileage cache. 3. This approach is implemented for the MVP, reserving daily polling/webhooks as optimization features for later phases. | P0 |
| S2.5 | As a connected user, I want the app to automatically fetch and cache my initial historical running data (last 6 weeks) so that the Critical Score calculation is ready on the first dashboard load. | 1. Backend successfully exchanges the auth code for a Refresh Token. 2. API fetches running activities only (type=Run or sport_type=Running). | P0 |

Export to Sheets


### **Epic 3: Critical Score Display (Core Value)**

| ID | User Story | Acceptance Criteria (ACs) | Priority |
|---|---|---|---|
| C3.1 | As a runner, I want to see my Critical Score prominently displayed on the main dashboard so that I immediately know my current injury risk level. | 1. The score is displayed as a large, readable number (e.g., 1.15). | P0 |
| C3.2 | As a runner, I want the score to be color-coded to reflect the risk level based on the following thresholds so that I can interpret the number instantly: | 1. Score <1.10 = Gray (Low/Conservative). 2. 1.10≤Score≤1.25 = Green (Safe/Optimal Zone). 3. 1.25<Score≤1.30 = Yellow (Increased Risk/Caution). 4. Score >1.30 = Red (High Risk/Danger Zone). | P0 |
| C3.3 | As a runner, I want to see the Recommended Max Mileage for Next Week clearly stated so that I have an actionable training goal. | 1. The calculation uses the formula: Chronic Mileage×1.25. 2. The number is rounded to one decimal place (e.g., "45.8 miles"). | P0 |
| C3.4 | As a runner, I want to see a simple breakdown of the input mileage so that I understand how the score was calculated. | 1. Display shows: Acute Mileage (This Week's Total): X.X miles. 2. Display shows: Chronic Mileage (Avg. Last 4 Weeks): Y.Y miles. | P0 |
| C3.5 | As a user, if I do not have enough historical data (fewer than 4 weeks of runs), I want a clear message explaining why the score cannot be calculated. | 1. The app displays: "Need more data. Please run for a few more weeks to establish your Chronic Mileage baseline." 2. The Critical Score display area is replaced by this message. | P1 |

## 
## Dependencies & Out of Scope Items for MVP

### Dependencies

This section outlines internal or external limitations that impact the development timeline or architecture.

- **D1. Strava Developer Account:** Requires a registered Strava developer account and approved application keys (Client ID/Secret) before integration development can begin.

- **D2. SMS Provider:** Requires integration with a third-party SMS service (e.g., Twilio, Firebase) for OTP/Phone number authentication.

- **D3. Database Setup:** Requires a production-ready SQL database (e.g., PostgreSQL) instance with necessary security policies for token storage.

### Future Scope (Out-of-Scope Items for MVP)

This section clearly lists features that *will not* be built during the MVP phase, managing expectations for stakeholders and the development team.

| Feature / Item | Target Phase | Rationale for Exclusion from MVP |
|---|---|---|
| Historical Data Charts | Phase 2 (iOS) | Requires significant frontend development effort (charting libraries) that is non-essential for core value validation. |
| User-Adjustable ACWR | Phase 3 | Requires UI/logic for user settings and database changes; 1.25 is sufficient for initial validation. |
| Garmin/Coros Integration | Phase 3 | Focused strictly on Strava for MVP to minimize integration complexity. |
| Email Notifications/Marketing | Phase 2+ | Non-core functionality; focus is on in-app value delivery. |
| Real-time Webhooks | Phase 2 | Complex server setup required; starting with on-demand polling simplifies backend for MVP. |

## 
## 🧱 Summary of Tech Stack

| Component | Recommended Technology | Why it's Sustainable |
|---|---|---|
| Backend API | Python (Django/Flask) or Node.js (Express) | Robust, scalable, excellent library support for data processing and external APIs. |
| Database | PostgreSQL | Reliability, data integrity, and complex query support. |
| Task Queue | Celery (Python) or Bull (Node.js) | Ensures the on-demand Strava logic doesn't block the API, and scales up for future polling/webhooks. |
| Web Frontend (MVP) | React | Lays the architectural foundation for the mobile apps. |
| Mobile Apps (Future) | React Native | Maximum code reuse across iOS and Android, minimizing future development cost. |

## 
## 💾 API Design Patterns for Asynchronous Data & Caching

The goal is to provide a near-instantaneous score to the user while ensuring the underlying data is updated in the background.


### 1. Data Flow Architecture

The system uses an **API-to-Cache-to-Client** pattern, where the backend acts as a proxy, minimizing direct calls to Strava during the user session.

| Layer | Function | Technology |
|---|---|---|
| Client | Requests the score. | React Web App |
| API Endpoint | Receives the score request; returns data immediately from the cache. | Django/Express API |
| Task Queue | Handles long-running background jobs (Strava communication, heavy calculation). | Celery/Bull |
| Cache/DB | Stores user tokens, mileage logs, and the timestamp of the last successful sync. | PostgreSQL/Redis |

Export to Sheets


### 2. Strava Integration Endpoints

These endpoints manage the user's connection and data retrieval initiation.

#### **A. Authorization Endpoints (Token Management)**

| Endpoint | Method | Function | Key Logic |
|---|---|---|---|
| /api/v1/auth/strava/connect | GET | Initiates the OAuth flow. | Redirects the client to the Strava authorization URL. |
| /api/v1/auth/strava/callback | GET | Handles the OAuth callback from Strava. | Exchanges the authorization code for the Access Token (short-lived) and Refresh Token (long-lived). Stores the Refresh Token securely and triggers the initial data fetch task. |

Export to Sheets

#### **B. Core Data Retrieval Endpoint**

This endpoint is the key to the MVP's responsiveness. It immediately triggers an asynchronous update but doesn't wait for it to finish.

| Endpoint | Method | Function | Key Logic |
|---|---|---|---|
| /api/v1/data/score | GET | Retrieves the Critical Score. | 1. Fetches mileage from the local PostgreSQL cache. 2. Calculates and returns the Critical Score and Capacity immediately. 3. Asynchronously triggers a background job (update_strava_data_task) to check for new activities since the last sync. |

Export to Sheets


### 3. Asynchronous Task Queue Logic

The task queue is responsible for ensuring the data is updated without making the user wait. This logic lives entirely on the backend worker process.

#### **Task: **`update_strava_data_task(user_id)`

This task is triggered by the `/data/score` endpoint and runs in the background.

1. **Token Refresh:** Use the stored **Refresh Token** to obtain a fresh **Access Token** from Strava.

2. **Determine Time Window:** Retrieve the `last_successful_sync_timestamp` from the user's DB record.

3. **Strava API Call:** Query the Strava API `/activities` endpoint, filtering results to fetch only activities created **after** the `last_successful_sync_timestamp`.

4. **Data Processing:**

- Iterate through new activities.

- Filter for `sport_type=Running`.

- Convert distance (meters) to miles.

- Calculate which "week" (Monday–Sunday) the activity falls into.

- **Cache Update:** Update the mileage total for the affected week(s) in the **PostgreSQL mileage cache** (e.g., add new mileage to the current week's Acute Mileage).

- **Timestamp Update:** Update the user's `last_successful_sync_timestamp` to the current time, marking the task as complete.

#### **Task: **`initial_historical_fetch(user_id)`

This task is triggered *only once* after the user successfully connects Strava.

1. **Time Window:** Fetch all running data for the last 6 weeks (for a full Chronic baseline).

2. **Processing & Caching:** Process all returned activities, populate the mileage cache for the last 6 weeks, and set the initial `last_successful_sync_timestamp`.

This design ensures the frontend receives data instantly, and the slow, network-dependent work of communicating with Strava happens safely and asynchronously in the background.
