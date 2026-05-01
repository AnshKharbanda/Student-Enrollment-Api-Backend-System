# imports
from fastapi import FastAPI,HTTPException,Path
from pydantic import BaseModel,Field,EmailStr
from typing import Annotated,Optional,Literal
from .db import students,courses,enrollment

app=FastAPI()

student_id_counter=1


# pydantic models

"""student base models"""

class Student(BaseModel):
    name:str=Field(...,description="Enter name of student")
    email:EmailStr
    age:int=Field(...,gt=0,description="Enter age of student")
    
class StudentUpdate(BaseModel):
    name:Optional[str]=None
    email:Optional[EmailStr]=None
    age:Optional[int]=Field(None,gt=0)
    
"""course base models"""
class Course(BaseModel):
    id:int=Field(...,description="Enter id of course")
    title:str=Field(...,min_length=1,description="Enter title of course")
    max_enrollments:int=Field(...,gt=0,description="enter max enrollments")
    
class CourseUpdate(BaseModel):
    title:Optional[str]=None
    max_enrollments:Optional[int]=Field(None,gt=0)
    

# api endpoints

"""student endpoints"""

@app.get('/students')
def load_students():
    return list(students.values())

@app.get('/students/{student_id}')
def get_student(student_id:Annotated[int,Path(gt=0)]):
    
    if student_id not in students:
        raise HTTPException(status_code=404,detail="Id not found")
    
    return students[student_id]

"""create"""
@app.post('/students/create')
def create_student(student_info:Student):
    global student_id_counter
    
    student_id=student_id_counter
    student_id_counter+=1
    
    new_student={
        'id':student_id,
        **student_info.model_dump()
    }
    
    students[student_id]=new_student
    
    return new_student

"""update"""
@app.patch('/students/update/{student_id}')
def update_student(student_id:int,update_info:StudentUpdate):
    
    if student_id not in students:
        raise HTTPException(status_code=404,detail="Student not found")
    
    existing_student_info=students[student_id]
    updated_student_info=update_info.model_dump(exclude_unset=True)
    
    if not updated_student_info:
        raise HTTPException(status_code=400,detail="no data to update")
        
    for key,value in updated_student_info.items():
        existing_student_info[key]=value
        
    return {
        'updated_info':existing_student_info,
        'message':'updated successfully'
    }
    
"""delete endpoint"""
@app.delete('/students/delete/{student_id}')
def delete_student(student_id:int):
    
    if student_id not in students:
        raise HTTPException(status_code=404,detail='Student not found')
    
    student_info=students[student_id]
    del students[student_id]
    
    return {
        **student_info,
        'message':'deleted successfully'
    }
    
"""courses endpoints"""

@app.get('/courses')
def view_courses():
    return list(courses.values())

@app.get('/courses/{course_id}')
def view_course_by_id(course_id:int):
    if course_id not in courses:
        raise HTTPException(status_code=404,detail="Course not found")
    
    return courses[course_id]

"""create"""
@app.post('/courses/create')
def create_course(course_info:Course):
    course_id=course_info.id
    
    if course_id in courses:
        raise HTTPException(status_code=409,detail='Course with similar id exists')
    
    courses[course_id]=course_info.model_dump()
    enrollment[course_id]=[]
    
    return courses[course_id]

"""update course"""
@app.patch('/courses/update/{course_id}')
def update_course(course_id:int,update_info:CourseUpdate):
    if course_id not in courses:
        raise HTTPException(status_code=404,detail="Course not found")
    
    existing_course_info=courses[course_id]
    updated_course_info=update_info.model_dump(exclude_unset=True)
    
    if not updated_course_info:
        raise HTTPException(status_code=400,detail="No update info")
    
    for key,value in updated_course_info.items():
        existing_course_info[key]=value
        
    return {
        **existing_course_info,
        'message':'updated successfully'
    }
    
@app.delete('/courses/delete/{course_id}')
def delete_course(course_id:int):
    if course_id not in courses:
        raise HTTPException(status_code=404,detail='Course ID not found')
    
    course_info=courses[course_id]
    
    del courses[course_id]
    del enrollment[course_id]
    return {
        **course_info,
        'message':'deleted successfully'
    }
    
# enrollments

@app.get('/all-enrollments')
def get_all_enrollments():
    return enrollment

@app.get('/courses/enrollments/{course_id}')
def get_course_enrollment_left(course_id:int):
    if course_id not in courses:
        raise HTTPException(status_code=404,detail="Course not found")
    
    enrollments_left=courses[course_id]['max_enrollments']-len(enrollment[course_id])
    status='open' if enrollments_left else 'closed'
    return {
        'Course id':course_id,
        'Enrollments left':enrollments_left,
        'status':status
    }

@app.get('/student/enrollment/{student_id}')
def get_student_all_enrollment(student_id:int):
    if student_id not in students:
        raise HTTPException(status_code=404,detail='Student Not Found')
    
    enrolled_courses=[]
    
    for course_id in enrollment:
        for student in enrollment[course_id]:
            if student_id==student:
                enrolled_courses.append((course_id,courses[course_id]['title']))
                
    if not enrolled_courses:
        return {
            'Student ID':student_id,
            'Enrolled COurses':'No Enrolled Courses'
        }
        
                
    return {
        'Student ID':student_id,
        'Enrolled Courses':enrolled_courses,
        'Total Enrolled':len(enrolled_courses)
    }
    
@app.post('/create/enrollment/{student_id}/{course_id}')
def create_enrollment(student_id:int,course_id:int):
    if student_id not in students or course_id not in courses:
        raise HTTPException(status_code=404,detail='Student or Course Not found')
    
    if student_id in enrollment[course_id]:
        raise HTTPException(status_code=409,detail='Student already enrolled in course')
    
    if courses[course_id]['max_enrollments']==len(enrollment[course_id]):
        raise HTTPException(status_code=409,detail="Can't Have More Enrollments in this Course")
    
    enrollment[course_id].append(student_id)
    
    return {
        'message':f'{student_id} enrolled in {course_id} successfully'
    }

# delete enrollment
@app.delete('/delete/course/enrollment/{student_id}/{course_id}')
def delete_enrollment(student_id:int,course_id:int):
    if student_id not in students or course_id not in courses or student_id not in enrollment[course_id]:
        raise HTTPException(status_code=404,detail='Student Not Enrolled in this Course')
    
    enrollment[course_id].remove(student_id)
    
    return {
        'message':f'Deleted Successfully {student_id} from {course_id}'
    }
    
    
# update student1 to student2 in a course
@app.patch('/update/enrollment/student/{student1}/{student2}/{course_id}')
def update_students_in_course(student1:int,student2:int,course_id:int):
    if student1 not in students or student2 not in students or course_id not in courses:
        raise HTTPException(status_code=404,detail='Student or course not found')
    
    if student1 not in enrollment[course_id]:
        raise HTTPException(status_code=404,detail=f'{student1} not found in {course_id}')
        
        
    if student2 in enrollment[course_id]:
        raise HTTPException(status_code=409,detail=f'{student2} already enrolled in that course')
    enrollment[course_id].remove(student1)
    enrollment[course_id].append(student2)
    
    return {
        'message':f'{student2} enrolled successfully in {course_id}'
    }

# update student1 course from course1 to course2
@app.patch('/update/enrollment/student/{student_id}/course/{course1}/{course2}')
def update_student_course(student_id:int,course1:int,course2:int):
    if student_id not in students or course1 not in courses or course2 not in courses:
        raise HTTPException(status_code=404,detail='course or Student not found')
    
    if course1==course2:
        raise HTTPException(status_code=409,detail="Same Course ID's")
    
    if student_id not in enrollment[course1]:
        raise HTTPException(status_code=409,detail=f'{student_id} not enrolled in {course1}')
    
    if (courses[course2]['max_enrollments']-len(enrollment[course2]))==0:
        raise HTTPException(status_code=409,detail=f"Can't Enroll {student_id} in {course2}")
    
    if student_id in enrollment[course2]:
        raise HTTPException(status_code=409,detail=f'{student_id} already enrolled in {course2}')
    
    enrollment[course1].remove(student_id)
    enrollment[course2].append(student_id)
    
    return{
        'message':f'{student_id} enrolled in {course2} successfully',
        'status':'done'
    }

