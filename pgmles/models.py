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
    image_file = db.Column(db.String(20), nullable=False,
                           default='default.jpg')
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Language(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    info = db.Column(db.Text)

    def __repr__(self):
        return f"Language('{self.name}', '{self.info}')"


class Classes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    language_id = db.Column(db.Integer, db.ForeignKey(
        'language.id'), nullable=False)
    teacher_id = db.Column(
        db.Integer, db.ForeignKey('user.id'), nullable=False)
    start = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f"Language('{self.id}', '{self.language_id}', '{self.start}', '{self.location}')"


# date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
# content = db.Column(db.Text, nullable=False)
# user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
