# PulseFit Pro (Flask + PostgreSQL)

PulseFit Pro is a lightweight fitness tracking web app built with Flask. Users can register, log in, and track workouts (exercise, calories burned, duration, notes). Each workout is stored in a database and displayed with simple statistics and charts.

# Features
User authentication (Register / Login / Logout) using Flask-Login
Password hashing (Werkzeug security)
Workout tracking: add and view workout history
Progress charts with Chart.js (calories & duration trends)
Database-backed storage using SQLAlchemy

# Tech Stack
Backend: Flask
Forms/validation: Flask-WTF / WTForms
Database: PostgreSQL (via Docker Compose)
Frontend: Bootstrap, Chart.js
Containerization: Docker / docker-compose

# Project Structure
app.py — Flask app, models, forms, and routes
templates/ — HTML templates (layout, index, login, register)
static/ — CSS and frontend assets
Dockerfile / docker-compose.yml — container configuration

# Run with Docker Compose
docker-compose up --build

# App
http://localhost:5000
