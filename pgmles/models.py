from datetime import datetime

from flask_login import UserMixin

from . import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(6), nullable=False, default="client")
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    weekday = db.Column(db.Integer, nullable=False)
    start = db.Column(db.String(10), nullable=False, default=datetime.utcnow)
    end = db.Column(db.String(10), nullable=False, default=datetime.utcnow)
    location = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f"Course('{self.id}', '{self.name}', '{self.description}')"


class CourseMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
