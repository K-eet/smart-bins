# Setup Instructions
> note: this setup assumes you are using Windows
## 1. Install prerequisites
Ensure nodejs, git bash, Postgresql and corresponding client (e.g. pgadmin4) are installed
## 2. Setup SQL database
1. In pgadmin4 (or your preferred Postgresql client), create a new database named `smart_trash`
2. Note your username and password for later
## 3. Clone this repo
`git clone https://github.com/K-eet/smart-bins.git`
## 4. Setup Environment variables
In the `backend` folder, create a `.env` file and add the follwing variables:
```env
DB_USER=your_username
DB_PASSWORD=your_password
DB_HOST=localhost
DB_NAME=smart-trash
```
## 5. Create Virtual Environment and install requirements
1. open a new terminal window and `cd` to the project root (`smart-bins`)
2. `python -m venv .venv`
3. `.venv\Scripts\activate`
## 6. Run Backend Server
1. In the same terminal window, `cd backend`
2. run `python -m pip install -r requirements.txt`
3. `uvicorn main:app --reload`
## 7. Run Frontend Web UI
1. Open a new terminal window (do not close the exisitng one)
2. `cd` to `smart-bins/frontend`
3. `npm install -r requirements.txt`
4. `npm run dev`

# Description of System Components and Logic
## Frontend (App.vue)
- **Frameworks/Libraries**: Vue 3, Vuetify (UI), fetch API for HTTP.
- **Main Features**:
    - **Dashboard**: Displays statistics (total bins, full bins, maintenance, average fill).
    - **Filters**: Users can filter bins by district, type, status, and minimum fill.
    - **Bins Table**: Lists all bins with location, type, fill level, status, last emptied, and actions (schedule, empty, maintenance).
    - **Dialogs**: For adding bins and scheduling collections.
    - **Actions**: Users can add bins, empty bins, toggle maintenance, and schedule/complete collections.
    - **Auto-refresh**: Data auto-refreshes every 30 seconds.
    - **Data Flow**: Uses fetch to call backend API endpoints for bins, stats, and schedules. User actions trigger API calls and UI updates.
## Backend (main.py)
- **Frameworks/Libraries**: FastAPI, SQLModel (ORM), Pydantic, Uvicorn, dotenv, PostgreSQL.
- **Main Features**:
    - **Models**: Defines TrashBin and CollectionSchedule tables, and related Pydantic schemas.
    - **API Endpoints**:
        - `/api/bins`: CRUD for bins (list, create, update, empty).
        - `/api/schedules`: CRUD for collection schedules.
        - `/api/stats`: Returns bin statistics.
    - **Business Logic**:
        - **Bin Creation**: Accepts bin data, stores with uppercase bin_type for DB, but expects lowercase from frontend.
        - **Emptying Bins**: Sets fill to 0, updates status and last emptied timestamp.
        - **Maintenance**: Toggle maintenance status and update bin accordingly.
        - **Sensor Simulation**: Background task simulates fill level changes.
        - **Demo Data**: Seeds database with sample bins and schedules on startup.
        - **CORS**: Allows frontend to communicate with backend.
## How They Work Together
- The **frontend** provides an interactive dashboard for managing smart bins, sending user actions (add, empty, schedule, etc.) as HTTP requests to the **backend**.
- The **backend** processes these requests, updates the database, and returns updated data.
- The **frontend** fetches and displays this data, keeping the UI in sync with the **backend** state.

**Summary**:
The app is a full-stack smart trash management system: Vue/Vuetify frontend for user interaction, FastAPI/SQLModel backend for data and business logic, with real-time-like updates and demo data for testing.