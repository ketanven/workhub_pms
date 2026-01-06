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
workhub/
├── venv/                     # Virtual environment (ignored in Git)
├── requirements.txt
├── .gitignore
├── README.md
│
├── workhub_backend/
│   ├── manage.py
│   ├── workhub_backend/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── asgi.py
│   │   └── wsgi.py
│   │
│   ├── accounts/
│   ├── projects/
│   ├── tasks/
│   ├── notifications/
│   ├── reports/
│   └── common/




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


#To Start the Project
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py runserver

