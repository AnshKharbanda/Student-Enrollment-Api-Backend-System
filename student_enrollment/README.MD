# Student Enrollment System API

A backend API built using FastAPI for managing:

* Students
* Courses
* Student enrollments

The project demonstrates relationship handling, enrollment management, validation logic, and backend API design.

## Features

### Student APIs

* Create student
* View all students
* View student by ID
* Update student
* Delete student

### Course APIs

* Create course
* View all courses
* View course by ID
* Update course
* Delete course

### Enrollment APIs

* Enroll student into course
* Delete enrollment
* Transfer student from one course to another
* Replace enrolled student in a course
* View all enrollments
* View student enrollments
* View remaining course capacity

## Concepts Implemented

* FastAPI routing
* Pydantic validation
* REST APIs
* Many-to-many relationship handling
* Enrollment capacity constraints
* Duplicate enrollment prevention
* Relationship integrity checks
* HTTP exception handling

## Tech Stack

* Python
* FastAPI
* Pydantic

## Project Structure

student_enrollment/
├── main.py
├── db.py
├── **init**.py

## Run Locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Run server:

```bash
uvicorn student_enrollment.main:app --reload
```

Open Swagger Docs:

```text
http://127.0.0.1:8000/docs
```
