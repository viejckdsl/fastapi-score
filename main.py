from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator
from typing import List

app = FastAPI()

GRADE_MAP = {
    "A+": 4.5, "A": 4.0, "B+": 3.5, "B": 3.0,
    "C+": 2.5, "C": 2.0, "D+": 1.5, "D": 1.0,
    "F": 0.0
}

class Course(BaseModel):
    course_code: str
    course_name: str
    credits: int
    grade: str

    @field_validator("grade")
    @classmethod
    def check_grade(cls, v):
        if v not in GRADE_MAP:
            raise ValueError("Invalid grade")
        return v

class StudentRequest(BaseModel):
    student_id: str
    name: str
    courses: List[Course]

class StudentSummary(BaseModel):
    student_id: str
    name: str
    gpa: float
    total_credits: int

@app.post("/score")
def calculate_score(data: StudentRequest):
    total_score = 0
    total_credits = 0
    for course in data.courses:
        score = GRADE_MAP[course.grade]
        total_score += score * course.credits
        total_credits += course.credits

    if total_credits == 0:
        raise HTTPException(status_code=400, detail="Total credits cannot be zero")

    gpa = round(total_score / total_credits + 1e-8, 2)
    return {
        "student_summary": StudentSummary(
            student_id=data.student_id,
            name=data.name,
            gpa=gpa,
            total_credits=total_credits
        )
    }
