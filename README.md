# WorkHub – Project Management System (PMS)

WorkHub is a web-based **Project Management System** designed to help teams plan, organize, and track projects and tasks efficiently.  
The system is built using **Django (Backend)**, **React (Frontend – future scope)**, and **MySQL (Database)**, following a clean and modular architecture suitable for academic and real-world use.

---

## 🚀 Features (Current Scope)

- User & Role Management (Admin, Manager, Team Member)
- Project Management
- Task Management
- Modular Django App Structure
- REST API Ready
- MySQL Database Support
- Clean Service-Based Architecture
- Git Version Control

---

## 🛠️ Tech Stack

### Backend
- **Python**: 3.10+
- **Django**: 4.x
- **Django REST Framework**
- **MySQL**: 8.x

### Frontend (Future Scope)
- **React.js**

### Tools
- Git & GitHub
- Virtual Environment (venv)

---

## 📁 Project Folder Structure
```bash
workhub/
├── venv/ # Virtual environment (ignored in Git)
├── requirements.txt # Project dependencies
├── .gitignore
├── .env # Environment variables (ignored in Git)
├── env.example # Sample env file
├── README.md
├── manage.py
│
├── common/
│ └── responses.py # Common API response handler
│
├── core/ # Single main app
│ ├── migrations/
│ │ ├── init.py
│ │ └── 0001_initial.py
│ │
│ ├── models/
│ │ ├── init.py
│ │ ├── user.py
│ │ ├── project.py
│ │ └── task.py
│ │
│ ├── serializers/
│ │ ├── Admin/
│ │ │ └── login_serializer.py
│ │ └── User/
│ │ └── login_serializer.py
│ │
│ ├── controllers/
│ │ ├── Admin/
│ │ │ └── auth_controller.py
│ │ └── User/
│ │ └── auth_controller.py
│ │
│ ├── services/
│ │ ├── Admin/
│ │ │ └── auth_service.py
│ │ └── User/
│ │ └── auth_service.py
│ │
│ ├── urls.py
│ └── apps.py
│
└── workhub/
├── init.py
├── settings.py
├── urls.py
├── asgi.py
└── wsgi.py




---

## ⚙️ Prerequisites

Make sure the following are installed:

- Python 3.10+
- pip
- MySQL Server
- Git

Check versions:
```bash
python3 --version
pip3 --version
mysql --version
git --version



#Create a .env file using env.example:
DEBUG=True
SECRET_KEY=your-secret-key

DB_NAME=workhub_db
DB_USER=root
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=3306

ALLOWED_HOSTS=127.0.0.1,localhost
LANGUAGE_CODE=en-us
TIME_ZONE=Asia/Kolkata


#To Start the Project
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py runserver

#Overview
Request
  → Serializer (validation)
    → Controller (API layer)
      → Service (business logic)
        → Model (database)
      → Common Response


