# E-Learn-App

[![Python](https://img.shields.io/badge/Python-3.x-blue)](https://www.python.org/) [![Django](https://img.shields.io/badge/Django-5.1.7-green)](https://www.djangoproject.com/) [![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

E-Learn-App is a Django-based eLearning platform that allows users to browse courses, enroll, and complete quizzes. It supports user authentication, role-based access, and media management for course content and avatars.

Features:
- User registration and login
- Role-based access (student, teacher)
- Enroll in courses and track progress
- Quiz system with results
- Media management (avatars, course images, lesson PDFs, and videos)
- Responsive design using Django templates and Tailwind CSS

Technologies:
- Python 3.x
- Django
- SQLite (development database)
- Pillow (image handling)
- python-dotenv (environment variables)

Setup Instructions:
1. Clone the repository: git clone https://github.com/AleksandarMilkov/e-learn-app && cd e-learn-app
2. Create a virtual environment: python -m venv .venv
3. Activate it: 
   - PowerShell: .venv\Scripts\Activate.ps1
   - CMD: .venv\Scripts\activate.bat
4. Install dependencies: pip install -r requirements.txt
5. Create a .env file in the project root with:
   SECRET_KEY=your_secret_key_here
   DEBUG=True
6. Run migrations: python manage.py migrate
7. Create a superuser (optional): python manage.py createsuperuser
8. Run the development server: python manage.py runserver
9. Open http://127.0.0.1:8000 in your browser

Git Ignore:
- .venv/ -> local virtual environment
- .env -> secrets
- db.sqlite3 -> local database
- media/ -> uploaded user content
- __pycache__/ -> Python cache files
- .idea/ -> PyCharm project settings

Notes:
- Media uploads (avatars, course images, PDFs, videos) are not included in the repository. You can add your own files to the `media/` folder for testing.
- The database is empty on first clone — run migrations and create superuser to start.
- Designed for local development. For production, set DEBUG=False and configure ALLOWED_HOSTS.

License:
This project is open-source and free to use for learning and portfolio purposes.
