FROM python:3.11
LABEL maintainer="grendersq2@gmail.com"

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p /files/media
RUN mkdir -p /app/staticfiles

RUN adduser \
        --disabled-password \
        --no-create-home \
        my_user

RUN chown -R my_user /files/media
RUN chmod -R 755 /files/media
RUN chown -R my_user /app/staticfiles
RUN chmod -R 755 /app/staticfiles

USER my_user

CMD ["sh", "-c", "python manage.py wait_for_db && python manage.py collectstatic --noinput && python manage.py migrate && gunicorn transport_settings.wsgi:application --bind 0.0.0.0:$PORT"]