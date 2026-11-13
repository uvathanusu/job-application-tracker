# Job Application Tracker

A simple web application to track job applications in one place. Users can sign up, log in, add the jobs they have applied for, and follow each application through its stages (Applied, Interview, Offer, Rejected, etc.).

## Features

- User signup and login with secure **JWT authentication**
- Add and store job applications (company, role, status, date)
- Role dropdown with an **Other** option for custom roles
- **Stage filter** to view applications by status
- **Search** to find an application quickly
- Clean and simple user interface
- Data stored in a **SQLite** database

## Tech Stack

| Part | Technology |
|------|------------|
| Backend | Python, Flask |
| Database | SQLite |
| Authentication | JWT (JSON Web Token) |
| Frontend | HTML, CSS, JavaScript |

## Screenshots

![Login](screenshots/login.png)
![Dashboard](screenshots/dashboard.png)

## How to Run (Windows)

1. Clone the repository
   ```
   git clone https://github.com/UVATHANUSU/job-application-tracker.git
   cd job-application-tracker
   ```
2. Create and activate a virtual environment
   ```
   py -m venv venv
   venv\Scripts\activate
   ```
3. Install the requirements
   ```
   pip install -r requirements.txt
   ```
4. Start the server
   ```
   python app.py
   ```
5. Open the link shown in the terminal (usually `http://127.0.0.1:5000`) in your browser.

## How It Works

1. The user signs up and logs in. The server returns a **JWT token**.
2. The frontend sends the token with every request to the Flask API.
3. The API reads and writes the user's applications in the **SQLite** database.
4. The dashboard shows the applications, which can be filtered by stage or searched.

## Future Improvements

- Edit and delete applications
- Email reminders for follow-ups and interviews
- Deployment to a live website

## Author

**Uvathanusu T**
B.E. Computer Science and Engineering, Panimalar Engineering College
GitHub: https://github.com/UVATHANUSU
