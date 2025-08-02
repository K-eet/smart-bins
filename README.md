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