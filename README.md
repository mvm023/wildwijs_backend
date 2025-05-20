# Wildwijs backend

This is the backend for wildwijs, a Duolingo-style quiz app about Dutch nature, built with Django.

## Getting started

To get started, clone the directory, and run the following commands in the program directory:

#### 1. Create and activate virtual environment

python -m venv venv
source venv/bin/activate

#### 2. Install dependencies

pip install -r requirements.txt

#### 3. Create environment file

cp .env.example .env

- Populate this .env file with proper values to gain access to all functionalities. 

#### 4. Generate HTTPS certificates for localhost

mkcert -install\
mkcert localhost

#### 5. Run first migration

python manage.py migrate

## Building locally

To build the backend locally, activate the virtual environment and run the following command in the program directory:

python manage.py runserver_plus --cert-file=localhost.pem --key-file=localhost-key.pem

- The backend should now be running on https://127.0.0.1:8000.