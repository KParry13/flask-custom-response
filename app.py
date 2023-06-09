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
class StudentNameSchema(ma.Schema):
    class Meta:
        fields = ('first_name', 'last_name')

class StudentSchema(ma.Schema):
    class Meta:
        fields = ('id', 'first_name', 'last_name', 'year', 'gpa')

student_schema = StudentSchema()
students_schema = StudentSchema(many=True)


# Resources
class StudentListResource(Resource):
    def get(self):
        order = request.args.get('order')
        all_students = Student.query.all()
        if order == 'gpa':
            all_students = Student.query.order_by(Student.gpa.desc()).all()
        elif order =="last_name":
            all_students = Student.query.order_by(Student.last_name.desc()).all()
        return students_schema.dump(all_students)

class FullCourseDetailResource(Resource):
    def get(self, course_details_id):
        custom_response = {}
        course = Course.query.get_or_404(course_details_id)
        custom_response["course_name"] = course.name
        custom_response["instructor_name"] = course.instructor.first_name
        custom_response["student_info"] = {
            "number_of_students": 3,
            "students": students_schema.dump(course)
        }

        return custom_response,200
         
# Routes
api.add_resource(StudentListResource, '/api/students')
api.add_resource(FullCourseDetailResource, '/api/course_details/<int:course_details_id>')
