from flask import Flask, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_restful import Api, Resource
from dotenv import load_dotenv
from os import environ

load_dotenv()

# Create App instance
app = Flask(__name__)

# Add DB URI from .env
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('SQLALCHEMY_DATABASE_URI')

# Registering App w/ Services
db = SQLAlchemy(app)
ma = Marshmallow(app)
api = Api(app)
CORS(app)
Migrate(app, db)

# Creating student_course junction table
student_course = db.Table('student_course',
                    db.Column('student_id', db.Integer, db.ForeignKey('student.id')),
                    db.Column('course_id', db.Integer, db.ForeignKey('course.id')),
                    db.Column('grade', db.String(5))
                    )

# Models
class Student(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    year = db.Column(db.Integer())
    gpa = db.Column(db.Float())

class Course(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    instructor_id = db.Column(db.Integer(), db.ForeignKey('instructor.id'))
    credits = db.Column(db.Integer())
    instructor=db.relationship("Instructor")
    students = db.relationship("Student", secondary=student_course, backref='courses')

class Instructor(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    hire_date = db.Column(db.Date())



# Schemas
class StudentSchema(ma.Schema):
    class Meta:
        fields = ('id', 'first_name', 'last_name', 'year', 'gpa')

student_schema = StudentSchema()
students_schema = StudentSchema(many=True)

class StudentNameSchema(ma.Schema):
    def get(self):
        custom_response = {}

        students = Student.query.all()
        for item in students:
            students = Student.query.filter(Student.id.has(id=item.id))

            custom_response[item.name] = {
                'first_name': item.first_name,
                'last_name': item.last_name,
                'students': students_schema.dump(students)
            }
        return custom_response, 200

# Resources
class StudentListResource(Resource):
    def get(self):
        order = request.args.get('order')
        query = Student.query
        if order:
            query = query.order_by(order)
        students = query.all()
        return students_schema.dump(students)

class FullCourseDetailResource(Resource):
    def get(self, course_details_id):
        custom_response = {}
        course_details_id = Course.query.all()
        for item in  course_details_id:
            course_details_id = Course.query.filter(Course.id.has(id=item.id))
            custom_response[item.name] = {
                'course_name': item.course_details_id,
                'instructor_name': item.instructor.relationship,
                'student_info': {
                'number_of_students': (len(course_details_id)),
                'students':[
                    {
                    StudentNameSchema()
                    }
                ]
                },
                'course_details_id': students_schema.dump(course_details_id)
            }
        return custom_response, 200

# Routes
api.add_resource(StudentListResource, '/api/students')
api.add_resource(FullCourseDetailResource, '/api/course_details/<int:course_details_id>')
