import os
import random
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import (
    create_engine, MetaData, Table, Column, Integer, String, ForeignKey, Date, Float, Index
)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, Session
from pydantic import BaseModel
from typing import Union
import requests

# Database Configuration
POSTGRES_DB = "test_db"
POSTGRES_USER = "test_user"
POSTGRES_PASSWORD = "test_password"
POSTGRES_HOST = "localhost"
POSTGRES_PORT = "5432"

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Models
class Project(Base):
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    deadline = Column(Date, nullable=False)
    complexity = Column(Float, nullable=False)

    assignments = relationship("Assignment", back_populates="project")


class Employee(Base):
    __tablename__ = 'employees'

    id = Column(Integer, primary_key=True)
    full_name = Column(String, nullable=False)
    position = Column(String, nullable=False)
    department = Column(String, nullable=True)  # New column added

    __table_args__ = (
        Index("ix_employees_position", "position"),  # Index on position
    )

    assignments = relationship("Assignment", back_populates="employee")


class Assignment(Base):
    __tablename__ = 'assignments'

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    issue_date = Column(Date, nullable=False)
    planned_end_date = Column(Date, nullable=False)
    actual_end_date = Column(Date, nullable=True)
    complexity = Column(Float, nullable=False)

    project = relationship("Project", back_populates="assignments")
    employee = relationship("Employee", back_populates="assignments")

# Schemas
class ProjectCreate(BaseModel):
    name: str
    deadline: str
    complexity: float


class EmployeeCreate(BaseModel):
    full_name: str
    position: str
    department: Union[str, None]


class AssignmentCreate(BaseModel):
    project_id: int
    employee_id: int
    issue_date: str
    planned_end_date: str
    actual_end_date: Union[str, None]
    complexity: float

# Routes for Projects
@app.get("/projects")
def get_projects(db: Session = Depends(get_db)):
    return db.query(Project).all()


@app.post("/projects")
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    new_project = Project(**project.dict())
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project


@app.get("/projects/{project_id}")
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@app.delete("/projects/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project)
    db.commit()
    return {"detail": "Project deleted"}

# Routes for Employees
@app.get("/employees")
def get_employees(db: Session = Depends(get_db)):
    return db.query(Employee).all()


@app.post("/employees")
def create_employee(employee: EmployeeCreate, db: Session = Depends(get_db)):
    new_employee = Employee(**employee.dict())
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)
    return new_employee


@app.get("/employees/{employee_id}")
def get_employee(employee_id: int, db: Session = Depends(get_db)):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


@app.delete("/employees/{employee_id}")
def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    db.delete(employee)
    db.commit()
    return {"detail": "Employee deleted"}

# Routes for Assignments
@app.get("/assignments")
def get_assignments(db: Session = Depends(get_db)):
    return db.query(Assignment).all()


@app.post("/assignments")
def create_assignment(assignment: AssignmentCreate, db: Session = Depends(get_db)):
    new_assignment = Assignment(**assignment.dict())
    db.add(new_assignment)
    db.commit()
    db.refresh(new_assignment)
    return new_assignment


@app.get("/assignments/{assignment_id}")
def get_assignment(assignment_id: int, db: Session = Depends(get_db)):
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return assignment


@app.delete("/assignments/{assignment_id}")
def delete_assignment(assignment_id: int, db: Session = Depends(get_db)):
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    db.delete(assignment)
    db.commit()
    return {"detail": "Assignment deleted"}

# Database Initialization Script
def init_db():
    from sqlalchemy_utils import database_exists, create_database

    if not database_exists(engine.url):
        create_database(engine.url)
        print(f"Database {POSTGRES_DB} created successfully.")
    else:
        print(f"Database {POSTGRES_DB} already exists.")

    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")

# Script to Populate Database
if __name__ == "__main__":
    init_db()

    # Populate projects
    for i in range(1, 6):
        project_data = {
            "name": f"Project {i}",
            "deadline": (datetime.now() + timedelta(days=random.randint(30, 180))).strftime("%Y-%m-%d"),
            "complexity": round(random.uniform(1.0, 10.0), 2)
        }
        response = requests.post("http://127.0.0.1:8000/projects", json=project_data)
        print(response.json())

    # Populate employees
    for i in range(1, 11):
        employee_data = {
            "full_name": f"Employee {i}",
            "position": random.choice(["Developer", "Manager", "Analyst", "Tester"]),
            "department": random.choice(["IT", "HR", "Finance", None])
        }
        response = requests.post("http://127.0.0.1:8000/employees", json=employee_data)
        print(response.json())

    # Populate assignments
    for i in range(1, 21):
        assignment_data = {
            "project_id": random.randint(1, 5),
            "employee_id": random.randint(1, 10),
            "issue_date": datetime.now().strftime("%Y-%m-%d"),
            "planned_end_date": (datetime.now() + timedelta(days=random.randint(10, 100))).strftime("%Y-%m-%d"),
            "actual_end_date": None,
            "complexity": round(random.uniform(1.0, 5.0), 2)
        }
        response = requests.post("http://127.0.0.1:8000/assignments", json=assignment_data)
        print(response.json())
