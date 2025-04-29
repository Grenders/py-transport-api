# Transport Booking System

Цей проект є системою бронювання квитків на транспорт, що дозволяє користувачам переглядати маршрути, бронювати квитки та керувати замовленнями. Він побудований на Django з використанням Django REST Framework (DRF) та PostgreSQL як бази даних.

## Локальний запуск

1. Клонуйте репозиторій:
   ```bash
   git clone <your-repo-url>

2. Створіть віртуальне середовище і активуйте:
   ```bash
   python -m venv venv
   source venv/bin/activate (Linux/Mac)
   venv\Scripts\activate ( Windows )

3. Встановіть залежності:
    ```bash
   pip install -r requirements.txt

4. Cтворіть файл .env за прикладом .env.example:
   ```bash
   cp .env.example .env
   Заповніть змінні у .env, наприклад:
   SECRET_KEY=<ваш_унікальний_ключ> # Згенеруйте: python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
   POSTGRES_HOST=db
   POSTGRES_DB=your_db_name
   POSTGRES_USER=your_user
   POSTGRES_PASSWORD=your_secure_password
   POSTGRES_PORT=5432

5. Виконайте міграції:
   ```bash
   python manage.py migrate

6. Запустіть сервер:
   ```bash
   python manage.py runserver

7. Перевірте API за адресою http://localhost:8000/api/doc/swagger/#/

## Docker Проєкт контейнеризовано за допомогою Docker і Docker Compose. Використовуються сервіси Django і PostgreSQL.

1. Встановіть Docker і Docker Compose.
2. Створіть файл .env за прикладом .env.example (дивіться інструкцію вище).
3. Запустіть проєкт:
   ```bash
   docker-compose up --build
4. Swagger-документація доступна за http://localhost:8001/swagger/#/
5. Для зупинки контейнерів:
    ```bash
   docker-compose down
6. для запуску тестів
   ```bash
   docker exec -it <container_name_or_id> python manage.py test"# py-transport-api" 
