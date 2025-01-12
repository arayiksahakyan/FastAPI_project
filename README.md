FastAPI PostgreSQL Project

Overview

This project is a REST API application built with FastAPI and PostgreSQL. It demonstrates basic CRUD operations, database initialization, and data migrations. The API allows for managing projects, employees, and assignments, offering endpoints to create, read, update, and delete records.

Features

Database Initialization:

Automatically creates a PostgreSQL database with the specified name if it doesn't exist.

CRUD Operations:

Manage projects, employees, and assignments through REST API.

Data Population:

Populate the database with random data using the provided scripts.

Migrations:

Add new columns and indexes to tables via Alembic migrations.

Database Interaction:

Uses SQLAlchemy ORM for database interactions.

Prerequisites

Python 3.9+

PostgreSQL

pip for package installation

Installation

Clone the repository:
