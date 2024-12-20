# Pharmacy Management System

A Django-based Pharmacy Management System with multi-shop support and custom image handling capabilities.

## Features

- Multi-shop support with separate dashboards for admin and attendants
- Custom image upload for shops and medicines
- Inventory management with low stock alerts
- Sales recording and reporting
- User authentication and role-based access control

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Local Setup Instructions

1. Clone the repository:
```bash
git clone <repository-url>
cd pharmacy-management
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Unix or MacOS:
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create database and apply migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

5. Create a superuser (admin):
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

7. Access the application:
- Admin Dashboard: http://127.0.0.1:8000/admin/
- Main Application: http://127.0.0.1:8000/

## Setting Up Shops and Users

1. Login to the admin panel using your superuser credentials
2. Create a new Shop:
   - Go to Shops section
   - Click "Add Shop"
   - Fill in the details and upload a logo (optional)
   - Save

3. Create Shop Attendants:
   - First, create a user account
   - Then, go to Shop Attendants section
   - Click "Add Shop Attendant"
   - Select the user and assign them to a shop
   - Save

## Usage

### As Admin
- View all shops, medicines, and sales
- Add new shops
- Manage shop attendants
- Access comprehensive sales reports

### As Shop Attendant
- View shop-specific dashboard
- Manage medicine inventory
- Record sales
- View shop-specific reports

## File Structure

```
pharmacy_management/
├── pharmacy_app/
│   ├── models.py         # Database models
│   ├── views.py         # View logic
│   ├── forms.py         # Form definitions
│   ├── admin.py         # Admin interface
│   └── templates/       # HTML templates
├── static/              # Static files
├── media/              # Uploaded images
└── manage.py          # Django management script
```

## Testing

To test the application locally:

1. Make sure you have created a superuser
2. Create a test shop and assign test attendants
3. Test the following functionality:
   - User login/logout
   - Adding medicines with images
   - Recording sales
   - Viewing reports
   - Stock management
   - Multi-shop isolation (attendants can only see their shop's data)

## Notes

- Uploaded images are stored in the `media/` directory
- The system uses SQLite by default for local testing
- Make sure to update `SECRET_KEY` in settings.py for production use
- Static files and media files are served by Django in development mode