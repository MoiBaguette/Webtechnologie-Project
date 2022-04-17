from datetime import datetime

from flask_login import UserMixin

from .server import db, login_manager

""" function to load a user from database """
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

""" user-struct for 'user'-database """
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(6), nullable=False, default="client")
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)

""" course-struct for 'course'-database """
class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    weekday = db.Column(db.Integer, nullable=False)
    start = db.Column(db.String(10), nullable=False, default=datetime.utcnow)
    end = db.Column(db.String(10), nullable=False, default=datetime.utcnow)
    location = db.Column(db.String(120), nullable=False)

""" course-member-struct for 'coursemember'-database """
class CourseMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
