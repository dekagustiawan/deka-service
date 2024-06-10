# app/api/student.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.crud import get_student, get_students, create_student, update_student, delete_student
from app.schemas import Student, StudentCreate, StudentUpdate
from app.utils import get_db

router = APIRouter()

@router.post("/", response_model=Student)
def create_student_endpoint(student: StudentCreate, db: Session = Depends(get_db)):
    return create_student(db=db, student=student)

@router.get("/{student_id}", response_model=Student)
def read_student(student_id: int, db: Session = Depends(get_db)):
    db_student = get_student(db, student_id=student_id)
    if db_student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return db_student

@router.get("/", response_model=List[Student])
def read_students(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    students = get_students(db, skip=skip, limit=limit)
    return students

@router.put("/{student_id}", response_model=Student)
def update_student_endpoint(student_id: int, student: StudentUpdate, db: Session = Depends(get_db)):
    db_student = update_student(db=db, student_id=student_id, student=student)
    if db_student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return db_student

@router.delete("/{student_id}", response_model=Student)
def delete_student_endpoint(student_id: int, db: Session = Depends(get_db)):
    db_student = delete_student(db=db, student_id=student_id)
    if db_student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return db_student
