# Setup Instructions
> note: this setup assumes you are using Windows
## 1. Install prerequisites
Ensure [nodejs](https://nodejs.org/en), [python](https://www.python.org/downloads/), [git and git bash](https://git-scm.com/downloads), [Postgresql](https://www.postgresql.org/download/) and corresponding client (e.g. pgadmin4) are installed.
## 2. Setup SQL database
1. In pgadmin4 (or your preferred Postgresql client), create a new database named `smart_trash`
2. Note your username and password for later
> note: Don't worry about adding data. The first time you run the backend, 2 tables (`trashbin` and `collectionschedule`, both already populated) will automatically be created in the `smart_trash` database.
## 3. Clone this repo
Using git bash, `git clone https://github.com/K-eet/smart-bins.git`
## 4. Setup Environment variables
In the `backend` folder, create a `.env` file and add the follwing variables:
```env
DB_USER=USERNAME (your username)
DB_PASSWORD=******** (your password)
DB_HOST=localhost
DB_NAME=smart_trash
```
## 5. Create Virtual Environment and install requirements
1. open a new terminal window and `cd ~/smart-bins` (the project root)
2. `python -m venv .venv`
3. `.venv\Scripts\activate`
## 6. Run Backend Server
1. In the same terminal window, `cd ~/smart-bins/backend`
2. `python -m pip install -r requirements.txt`
3. `uvicorn main:app --reload`
4. Go to http://127.0.0.1:8000/docs to view the API endpoints

## 7. Run Frontend Web UI
1. Open a new terminal window (do not close the exisitng one)
2. `cd ~/smart-bins/frontend`
3. `npm i`
4. `npm run dev`
5. Ctrl + click the http://localhost:3000/ link to access the Web UI

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
## PostgreSQL Database (smart_trash)
- **Tables**
    - **trashbins**: Current state and long-term statistics for every physical bin.
    - **collectionschedule**: Planned and completed trash-collection jobs.
- **How the backend uses the database (Main Features)**
    - **Real-time Updates**: A background task periodically increases `fill_level` for each `trashbin`. When a bin is emptied (via the “Empty” action) the API sets `fill_level` to 0 and records `last_emptied_at`.
    - **Scheduling collections**: Creating a schedule row via `/api/schedules`inserts into `collectionschedule`. When a driver marks a job complete, the API timestamps `completed_at` and switches `status` to done.
    - **Data integrity & indexing**:
        - Foreign-key constraints ensure a schedule can’t exist for a non-existent bin.
        - Composite indexes on (`status`, `district`) and (`bin_type`, `fill_level`) speed up the dashboard’s filter queries.
## How They Work Together
- The **frontend** provides an interactive dashboard for managing smart bins, sending user actions (add, empty, schedule, etc.) as HTTP requests to the **backend**.
- The **backend** processes these requests, updates the **database**, and returns updated data.
- The **frontend** fetches and displays this data, keeping the UI in sync with the **backend** state.

**Summary**:
The app is a full-stack smart trash management system: Vue/Vuetify frontend for user interaction, FastAPI/SQLModel backend for data and business logic, with real-time-like updates and demo data for testing.

# Screenshots
![](</screenshots/Screenshot 2025-08-03 025847.png>)
![](</screenshots/Screenshot 2025-08-03 025950.png>)
![](</screenshots/Screenshot 2025-08-03 030008.png>)
![](</screenshots/Screenshot 2025-08-03 030018.png>)
![](</screenshots/Screenshot 2025-08-03 030022.png>)
