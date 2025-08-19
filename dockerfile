FROM python:3.10

WORKDIR /app

# Install system packages for MySQL
RUN apt-get update && apt-get install -y default-libmysqlclient-dev build-essential pkg-config

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn stockmgtr.wsgi:application --bind 0.0.0.0:8000"]