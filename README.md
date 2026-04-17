# News Application (Django)

## Overview
This is a Django-based news application that allows journalists to publish articles, editors to approve them, and readers to view approved content.

## Features
- Role-based access control (Reader, Journalist, Editor)
- Article creation, update, and deletion via REST API
- Article approval system
- Subscription-based article filtering
- Automated unit tests

## Technologies Used
- Django
- Django REST Framework

## How to Run

```bash

1. Clone the Repository

git clone https://github.com/NickDenji/news_project.git
cd example-repo/news_project

2. Create Virtual Environment
python -m venv .venv

Activate it:

Windows:

.venv\Scripts\activate

Mac/Linux:

source .venv/bin/activate

3. Install Dependencies
pip install -r requirements.txt

4. Setup MariaDB Database

Open your database client (e.g. HeidiSQL) and run:

CREATE DATABASE news_db;

5. Create Database User
CREATE USER 'news_user'@'localhost' IDENTIFIED BY 'password123';
GRANT ALL PRIVILEGES ON news_db.* TO 'news_user'@'localhost';
FLUSH PRIVILEGES;

6. Configure Database in Django

Update settings.py:

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'news_db',
        'USER': 'news_user',
        'PASSWORD': 'password123',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}

7. Apply Migrations
python manage.py migrate

8. Create Superuser
python manage.py createsuperuser

9. Run the Development Server
python manage.py runserver

10. Access the Application
Main site: http://127.0.0.1:8000/
Admin panel: http://127.0.0.1:8000/admin/
API root: http://127.0.0.1:8000/api/articles/

User Roles:

Role	Permissions
Reader	View approved articles, view subscribed content
Journalist	Create and update own articles
Editor	Approve and delete articles

API Endpoints:

Method	Endpoint	Description
GET	/api/articles/	List all approved articles
GET	/api/articles/subscribed/	Articles from subscribed users
GET	/api/articles/<id>/	Retrieve single article
POST	/api/articles/create/	Create article (journalists only)
PUT	/api/articles/<id>/update/	Update article
DELETE	/api/articles/<id>/delete/	Delete article

Testing:

Run automated tests:

python manage.py test

Test Coverage Includes:

Successful requests (e.g. journalist creating articles)
Failed requests (e.g. reader attempting restricted actions)
Permission validation
Subscription filtering

Features:

Role-based access control
Article approval workflow
Subscription-based filtering
RESTful API design
MariaDB database integration
Automated unit testing

Dependencies:

All dependencies are listed in requirements.txt.

Notes:

This project uses MariaDB via Django’s MySQL backend.
A virtual environment is recommended.
Ensure MariaDB is running before starting the server.
