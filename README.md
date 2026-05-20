# VahanChallan — Two-Wheeler Registration & Challan System

> A Django web application for registering two-wheeler vehicles and managing traffic challans with a clean, login-protected interface.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Database Schema](#database-schema)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
- [URL Routes](#url-routes)
- [Key Design Decisions](#key-design-decisions)

---

## Overview

VahanChallan is a full-stack Django web application built to streamline vehicle registration and traffic challan management for two-wheelers. It provides a secure, login-based interface where authorized users can register vehicles, issue challans, track payment status, and view summary dashboards — all without relying on Django's built-in admin panel.

---

## Features

- Authentication — Login/logout using Django's built-in auth system; no admin panel; all views are login-protected
- Vehicle Registration — Create, view, edit, and delete two-wheeler vehicle records
- Challan Management — Issue challans exclusively for registered vehicles; edit, delete, and mark challans as paid
- Dashboard — Summary statistics including total vehicles, total challans, and pending fines collected
- Search & Filter — Filter across both vehicle and challan tables
- Clean Frontend — Pure HTML + CSS, no external UI frameworks

---

## Tech Stack

| Layer      | Technology            |
|------------|-----------------------|
| Backend    | Python 3.10+, Django  |
| Database   | MySQL 8.0+            |
| Frontend   | HTML5, CSS3           |
| Auth       | Django built-in auth  |

---

## Database Schema

### `vehicle_registration` table

| Column               | Type           | Notes                            |
|----------------------|----------------|----------------------------------|
| id                   | BIGINT PK      | Auto-increment                   |
| registration_number  | VARCHAR(20)    | Unique, validated                |
| owner_name           | VARCHAR(100)   |                                  |
| vehicle_type         | VARCHAR(20)    | motorcycle / scooter / moped     |
| brand                | VARCHAR(50)    |                                  |
| model_name           | VARCHAR(50)    |                                  |
| year_of_manufacture  | INT            |                                  |
| fuel_type            | VARCHAR(20)    | petrol / electric / cng          |
| engine_number        | VARCHAR(50)    | Unique                           |
| chassis_number       | VARCHAR(50)    | Unique                           |
| registered_by_id     | FK → auth_user |                                  |
| registered_at        | DATETIME       | Auto                             |
| updated_at           | DATETIME       | Auto                             |

### `vehicle_challan` table

| Column              | Type                       | Notes                            |
|---------------------|----------------------------|----------------------------------|
| id                  | BIGINT PK                  | Auto-increment                   |
| vehicle_id          | FK → vehicle_registration  | CASCADE delete                   |
| challan_number      | VARCHAR(20)                | Unique, auto-generated           |
| violation_type      | VARCHAR(50)                | 11 choices                       |
| violation_date      | DATE                       |                                  |
| violation_location  | VARCHAR(200)               |                                  |
| fine_amount         | DECIMAL(8,2)               |                                  |
| is_paid             | BOOLEAN                    | Default False                    |
| paid_at             | DATETIME                   | Nullable                         |
| remarks             | TEXT                       | Optional                         |
| issued_by_id        | FK → auth_user             |                                  |
| created_at          | DATETIME                   | Auto                             |
| updated_at          | DATETIME                   | Auto                             |

---

## Project Structure

```
vehicle_challan/
├── manage.py
├── requirements.txt
├── README.md
├── static/
│   └── css/
│       └── style.css
├── vehicle_challan/              # Project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── vehicles/                     # Main app
    ├── models.py                 # Vehicle + Challan models
    ├── views.py                  # All view functions
    ├── forms.py                  # Django Form classes
    ├── urls.py                   # URL patterns
    ├── apps.py
    ├── migrations/
    │   └── 0001_initial.py
    └── templates/
        └── vehicles/
            ├── base.html
            ├── login.html
            ├── dashboard.html
            ├── vehicle_list.html
            ├── vehicle_detail.html
            ├── vehicle_form.html
            ├── vehicle_confirm_delete.html
            ├── challan_list.html
            ├── challan_form.html
            └── challan_confirm_delete.html
```

---

## Setup & Installation

### Prerequisites

- Python 3.10 or higher
- MySQL 8.0 or higher
- pip

---

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd vehicle_challan
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create the MySQL database

Run the following in your MySQL shell:

```sql
CREATE DATABASE vehicle_challan_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
```

### 5. Configure database credentials

Open `vehicle_challan/settings.py` and update the `DATABASES` block:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'vehicle_challan_db',
        'USER': 'root',           # your MySQL username
        'PASSWORD': 'your_password',  # your MySQL password
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### 6. Run migrations

```bash
python manage.py migrate
```

### 7. Create a superuser

```bash
python manage.py createsuperuser
```

Enter a username, email, and password when prompted. These will be your login credentials.

### 8. Start the development server

```bash
python manage.py runserver
```

### 9. Open the app

Visit: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

Log in with the superuser credentials you created in step 7.

---

## URL Routes

| URL                          | View Function      | Description                    |
|------------------------------|--------------------|--------------------------------|
| `/` or `/login/`             | login_view         | Login page                     |
| `/logout/`                   | logout_view        | Logout                         |
| `/dashboard/`                | dashboard          | Summary statistics             |
| `/vehicles/`                 | vehicle_list       | All vehicles table             |
| `/vehicles/add/`             | vehicle_create     | Register a new vehicle         |
| `/vehicles/<id>/`            | vehicle_detail     | Vehicle detail + its challans  |
| `/vehicles/<id>/edit/`       | vehicle_edit       | Edit vehicle record            |
| `/vehicles/<id>/delete/`     | vehicle_delete     | Delete vehicle                 |
| `/challans/`                 | challan_list       | All challans table             |
| `/challans/add/`             | challan_create     | Issue a new challan            |
| `/challans/<id>/edit/`       | challan_edit       | Edit challan                   |
| `/challans/<id>/delete/`     | challan_delete     | Delete challan                 |
| `/challans/<id>/mark-paid/`  | mark_challan_paid  | Quick mark-as-paid action      |

---

## Key Design Decisions

1. Challans enforce FK constraint — The `vehicle` ForeignKey on `Challan` with `CASCADE` ensures challans only exist for registered vehicles. The form dropdown also shows only registered vehicles.

2. Auto-generated challan numbers — Challan numbers follow the format `CHL<year><6-digit-random>` and are generated in `model.save()` before the first database write.

3. `select_related()` on list views — Used to avoid N+1 query issues when accessing `vehicle.owner_name` across many challan rows.

4. `paid_at` timestamp — Automatically set when `is_paid` transitions from `False` to `True`, whether on create or on edit.

5. `@login_required` on all views — Unauthenticated users are redirected to `/login/?next=<original-url>`. Login and logout views are the only public endpoints.
