# Apartment Management System

A robust, API-first backend solution designed to streamline the operations of rental properties. Built with **Django** and **Django REST Framework**, it facilitates seamless interaction between Landlords and Tenants.

## 🚀 Features

### 🔐 Authentication & Roles
*   **Secure Auth**: JWT (JSON Web Tokens) based authentication.
*   **Role-Based Access**: Distinct roles for **Landlords (Admin)** and **Tenants**.
*   **Profiles**: Verified landlord profiles with subscription management.

### 🏠 Landlord Features
*   **Property Management**: Add and manage multiple properties and rooms.
*   **Tenant Onboarding**: Assign registered users to specific rooms.
*   **Financials**:
    *   Review and approve/reject rent payments.
    *   Post monthly electricity bills.
    *   **Income Analytics**: View monthly income aggregation.
*   **Communication**:
    *   Post community-wide announcements.
    *   1-on-1 Chat with tenants.

### 👤 Tenant Features
*   **Dashboard**: View assigned room details and landlord contact info.
*   **Payments**: Upload rent proofs and pay electricity bills.
*   **Communication**: View community messages and chat with the landlord.

## 🛠️ Tech Stack
*   **Backend**: Django 5.1.3
*   **API**: Django REST Framework (DRF)
*   **Database**: MySQL
*   **Auth**: SimpleJWT

## 📦 Installation & Setup

1.  **Clone the repository**
    ```bash
    # Clone into a folder named 'apartment'
    git clone <repository-url> apartment
    cd apartment
    ```

2.  **Create and activate a virtual environment**
    ```bash
    python -m venv env
    # Windows
    .\env\Scripts\activate
    # Linux/Mac
    source env/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Database Configuration**
    *   Ensure MySQL is running.
    *   Create a database named `mkdb`.
    *   Update database credentials in `apartment/settings.py` if necessary.

5.  **Run Migrations**
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

6.  **Seed Roles**
    Initialize the default roles (Admin, Tenant):
    ```bash
    python manage.py seed_roles
    ```

7.  **Create Superuser**
    ```bash
    python manage.py createsuperuser
    ```

8.  **Run Server**
    ```bash
    python manage.py runserver
    ```

## 🧪 Testing
Run the comprehensive test suite to verify all features:
```bash
python manage.py test
```

## 📝 API Documentation
*   **Auth**: `/api/token/`, `/register/`
*   **Landlord**: `/landlord/properties/`, `/landlord/assign-tenant/`, `/landlord/analytics/income/`
*   **Tenant**: `/landlord/tenant/room/`, `/landlord/tenant/payments/`
