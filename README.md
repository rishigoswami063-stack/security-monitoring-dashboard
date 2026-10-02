\# Security Monitoring Dashboard



A web-based security monitoring dashboard built to demonstrate cybersecurity monitoring concepts through a centralized interface.



\## Features



\- JWT-based user authentication

\- Security metrics and dashboard overview

\- Security incident monitoring and status updates

\- Vulnerability tracking

\- Audit log monitoring

\- Security posture overview

\- SQLite database integration

\- REST API built with Flask



\## Technology Stack



\- \*\*Frontend:\*\* React, Vite, JavaScript, CSS

\- \*\*Backend:\*\* Python, Flask

\- \*\*Database:\*\* SQLite

\- \*\*Authentication:\*\* JSON Web Tokens (JWT)

\- \*\*API:\*\* REST API



\## Project Structure



```text

Security Monitoring Dashboard/

├── backend/

│   ├── app.py

│   ├── database.py

│   ├── requirements.txt

│   └── ...

├── frontend/

│   ├── src/

│   ├── public/

│   ├── package.json

│   └── ...

├── .gitignore

└── README.md

```



\## Run Locally



\### 1. Backend Setup



Open a terminal in the project root and run:



```powershell

cd backend

.\\venv\\Scripts\\Activate.ps1

python -m pip install -r requirements.txt

python app.py

```



Configure a `backend/.env` file with these variables:



```dotenv

JWT\_SECRET\_KEY=your-strong-random-secret

ADMIN\_USERNAME=your-admin-username

ADMIN\_PASSWORD=your-strong-password

```



Use your own values. \*\*Never upload the `.env` file or share your credentials publicly.\*\*



\### 2. Frontend Setup



Open a second terminal in the project root and run:



```powershell

cd frontend

npm install

npm run dev

```



Open the local URL displayed by Vite, usually `http://localhost:5173`.



\## Project Scope and Disclaimer



This is an educational demonstration project. Unless connected to real infrastructure and security data sources, the dashboard metrics and records should be treated as application/demo data rather than live organizational security telemetry. It is not a replacement for an enterprise Security Information and Event Management (SIEM) platform.



\## Author



\*\*Rishi Goswami\*\*  

Computer Science Engineering Student



