# CampusFlow

CampusFlow is a smart digital campus management platform that brings announcements, room availability, events, complaints, lost-and-found items, notifications, and admin analytics into one secure full-stack system.

## Features

- JWT-based authentication and RBAC enforcement
- User registration and login
- Role-based access for Student, Faculty, and Admin
- Announcement, event, room, complaint, and lost-and-found APIs
- Admin analytics dashboard data
- MySQL database integration through MySQL Workbench

## Project Structure

```text
CampusFlow/
├── app.py
├── backend/
│   ├── app.py
│   ├── config.py
│   ├── database.py
│   ├── requirements.txt
│   ├── middleware/
│   ├── models/
│   ├── routes/
│   └── tests/
├── frontend/
│   ├── css/
│   ├── js/
│   ├── index.html
│   ├── login.html
│   ├── student-dashboard.html
│   ├── faculty-dashboard.html
│   ├── admin-dashboard.html
│   ├── rooms.html
│   ├── announcements.html
│   ├── events.html
│   ├── complaints.html
│   ├── lost-found.html
│   └── notifications.html
├── database/
│   └── campusflow.sql
├── .env
├── .gitignore
├── README.md
└── requirements.txt
```

## Local setup

1. Create the `campusflow` database in MySQL Workbench and run `database/campusflow.sql`.
2. Set `DATABASE_URL` in `.env` to your MySQL connection:
   ```env
   DATABASE_URL=mysql+mysqlconnector://root:YOUR_PASSWORD@127.0.0.1:3306/campusflow
   ```
3. Add your Gemini API key and optional model to the same `.env` file:
   ```env
   GEMINI_API_KEY=your_google_ai_api_key
   GEMINI_MODEL=gemini-2.0-flash
   ```
   Never place the Gemini key in frontend JavaScript. The backend reads it only from the environment.
4. Create a virtual environment and install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
5. Run the Flask app:
   ```bash
   python app.py
   ```
6. Open `http://127.0.0.1:5000/` in your browser. The app starts at the login page.

## API notes

- Base URL: `http://localhost:5000`
- Auth endpoints: `/api/auth/register`, `/api/auth/login`, `/api/auth/logout`
- Protected routes require `Authorization: Bearer <JWT>`
- Campus AI uses `POST /api/chat`; the backend calls Google's Gemini API when `GEMINI_API_KEY` is configured

## Default credentials

For local testing, create a user account via the registration API or use a generated admin user in the database.

## Security

- Passwords are stored using Werkzeug hashing.
- JWTs are validated on protected routes.
- Authorization is enforced through the RBAC middleware.
- Environment variables hold the base secrets and database URL.
