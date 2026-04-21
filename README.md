# Django News Application

## Overview

This is a Django-based news application that allows **journalists to create articles**, **editors to approve them**, and **readers to view approved content**.

The system demonstrates:

* Role-based access control
* REST API design
* Containerisation with Docker
* Flexible database configuration for different environments

---

## Features

* Role-based access control (Reader, Journalist, Editor)
* Article creation, update, and deletion via REST API
* Article approval workflow (Editor-controlled)
* Subscription-based article filtering
* Docker container support
* Automated unit testing

---

## Technologies Used

* Python
* Django
* Django REST Framework
* SQLite (Docker environment)
* MariaDB (local development)
* HTML (Django Templates)
* Docker

---

## Setup Instructions (Local Development)

### 1. Clone the repository

```bash
git clone https://github.com/NickDenji/news_project.git
cd news_project
```

---

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it:

**Windows**

```bash
.venv\Scripts\activate
```

**Mac/Linux**

```bash
source .venv/bin/activate
```

---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Configure Database (MariaDB - Optional)

If you want to run the project with MariaDB locally:

```sql
CREATE DATABASE news_db;

CREATE USER 'news_user'@'localhost' IDENTIFIED BY 'password123';
GRANT ALL PRIVILEGES ON news_db.* TO 'news_user'@'localhost';
FLUSH PRIVILEGES;
```

Then update `settings.py`:

```python
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
```

---

### 5. Apply migrations

```bash
python manage.py migrate
```

---

### 6. Create superuser

```bash
python manage.py createsuperuser
```

---

### 7. Run the development server

```bash
python manage.py runserver
```

---

### 8. Access the application

* Main site: http://127.0.0.1:8000/
* Admin panel: http://127.0.0.1:8000/admin/
* API: http://127.0.0.1:8000/api/articles/

---

## Run with Docker (Recommended for Submission)

This project can be run entirely using Docker without setting up a database manually.

### Build the container

```bash
docker build -t news-app .
```

---

### Run the container

```bash
docker run -p 8000:8000 news-app
```

---

### Access the application

```text
http://localhost:8000
```

---

## Database Notes

* **SQLite is used automatically inside Docker** for simplicity and portability.
* **MariaDB is optional** and intended for local development only.
* No additional database setup is required when using Docker.

---

## User Roles

| Role       | Permissions                                     |
| ---------- | ----------------------------------------------- |
| Reader     | View approved articles, view subscribed content |
| Journalist | Create and update own articles                  |
| Editor     | Approve and delete articles                     |

---

## API Endpoints

| Method | Endpoint                     | Description                          |
| ------ | ---------------------------- | ------------------------------------ |
| GET    | `/api/articles/`             | List all approved articles           |
| GET    | `/api/articles/subscribed/`  | Articles from subscribed journalists |
| GET    | `/api/articles/<id>/`        | Retrieve single article              |
| POST   | `/api/articles/create/`      | Create article (journalists only)    |
| PUT    | `/api/articles/<id>/update/` | Update article                       |
| DELETE | `/api/articles/<id>/delete/` | Delete article                       |

---

## How to Use the Application

### 1. Register & Login

* Visit: http://127.0.0.1:8000/
* Register as:

  * Reader
  * Journalist
  * Editor
* Login with your credentials

---

### 2. Create an Article (Journalist)

* Login as a journalist
* Create an article via UI or API
* Articles are created as **not approved**

---

### 3. Approve an Article (Editor)

* Login as an editor
* Approve articles from the homepage

---

### 4. View Articles (Reader)

* Login as a reader
* Only approved articles are visible

---

### 5. Subscribe to a Journalist

Subscriptions can be managed via Django shell:

```bash
python manage.py shell
```

```python
from news_app.models import User

reader = User.objects.get(username='your_reader')
journalist = User.objects.get(username='your_journalist')

reader.subscribed_journalists.add(journalist)
```

Then access:

```
/api/articles/subscribed/
```

---

## Testing

Run tests with:

```bash
python manage.py test
```

### Coverage includes:

* Successful requests (e.g. journalist creating articles)
* Permission validation
* Failed requests (e.g. reader restricted actions)
* Subscription filtering

---

## Notes

* Docker setup includes automatic migrations on startup
* SQLite database is used in container for ease of setup
* MariaDB configuration is optional for local development
* Ensure dependencies are installed from `requirements.txt`

---

## Author

Nicholas Dionissiou
