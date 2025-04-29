# Transport Booking System

This project is a ticket booking system for transportation, allowing users to browse routes, book tickets, and manage their orders. It is built with Django using Django REST Framework (DRF) and PostgreSQL as the database.

The project is deployed and available at: https://py-transport-api.onrender.com/api/doc/swagger/#/

## Local Setup

1. Clone the repository:
   ```bash
   git clone <your-repo-url>

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate (Linux/Mac)
   venv\Scripts\activate ( Windows )

3. Install dependencies:
    ```bash
   pip install -r requirements.txt

4. Create a .env file based on the .env.example file:
   ```bash
   cp .env.example .env
   Fill in the environment variables .env, example:
   SECRET_KEY=<your_unique_secret_key> # Generate with: python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
   POSTGRES_HOST=db
   POSTGRES_DB=your_db_name
   POSTGRES_USER=your_user
   POSTGRES_PASSWORD=your_secure_password
   POSTGRES_PORT=5432

5. Apply migrations:
   ```bash
   python manage.py migrate

6. Run the development server:
   ```bash
   python manage.py runserver

7. Visit the API documentation at: http://localhost:8000/api/doc/swagger/#/

## The project is containerized using Docker and Docker Compose. It consists of Django and PostgreSQL services.

1. Install Docker and Docker Compose.
2. Create a .env file based on the .env.example file (see instructions above).
3. Start the project:
   ```bash
   docker-compose up --build
4. Swagger documentation is available at: http://localhost:8001/swagger/#/
5. To stop the containers:
    ```bash
   docker-compose down
6. To run tests:
   ```bash
   docker exec -it <container_name_or_id> python manage.py test"# py-transport-api" 
