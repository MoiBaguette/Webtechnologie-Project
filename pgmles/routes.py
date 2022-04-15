import os
import secrets

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from PIL import Image

from . import app, bcrypt, calendar, db
from .forms import LoginForm, NewCourseForm, RegistrationForm, SubscribeForm, UnsubscribeForm, UpdateAccountForm
from .models import Course, CourseMember, User


@app.route("/")
def index():
    courses = Course.query.all()
    subscriptions = []
    teachers = User.query.filter_by(type='teacher')
    if current_user.is_authenticated:
        subscriptions = [ cm.course_id for cm in CourseMember.query.filter_by(user_id=current_user.id) ]
    return render_template('index.html', calendar=calendar, courses=courses, subs=subscriptions, teachers=teachers)

@app.route("/about")
def about():
    return render_template('about.html', calendar=calendar, title='About')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect('/')
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', calendar=calendar, title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/')
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page if next_page else '/')
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', calendar=calendar, title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect('/')

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picturepath = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picturepath)

    return picture_fn

@app.route("/account", methods=[ 'GET', 'POST' ])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', calendar=calendar, title='Account', image_file=image_file, form=form)

@app.route("/admin")
def admin():
    courses = Course.query.all()
    return render_template('admin.html', calendar=calendar, title='Administration Page', courses=courses)


@app.route("/admin/new_course", methods=[ 'GET', 'POST' ])
def new_course():
    form = NewCourseForm()
    form.teacher_id.choices = [ (g.id, g.username) for g in User.query.filter_by(type='teacher') ]
    if form.validate_on_submit():
        course = Course(name=form.name.data, description=form.description.data, teacher_id=form.teacher_id.data, weekday=form.weekday.data, start=form.start.data, end=form.end.data, location=form.location.data)
        db.session.add(course)
        db.session.commit()
        flash('The course has been created!', 'success')
        return redirect(url_for('admin'))
    return render_template('new_course.html', calendar=calendar, title='New Course', form=form)

@app.route("/admin/update/<int:course_id>", methods=[ 'GET', 'POST' ])
def update_lang(course_id):
    form = NewCourseForm()
    form.teacher_id.choices = [ (g.id, g.username) for g in User.query.filter_by(type='teacher') ]
    course = Course.query.get_or_404(course_id)
    if form.validate_on_submit():
        course.name = form.name.data
        course.description = form.description.data
        course.teacher_id = form.teacher_id.data
        course.weekday = form.weekday.data
        course.start = form.start.data
        course.end = form.end.data
        course.location = form.location.data
        db.session.commit()
        flash('The course has been updated!', 'success')
        return redirect(url_for('admin'))
    elif request.method == 'GET':
        form.name.data = course.name
        form.description.data = course.description
        form.teacher_id.data = course.teacher_id
        form.weekday.data = course.weekday
        form.start.data = course.start
        form.end.data = course.end
        form.location.data = course.location
    return render_template('update_course.html', calendar=calendar, form=form, legend='Update Language')

@app.route("/course/<int:course_id>", methods=[ 'GET', 'POST' ])
def course(course_id):
    form = SubscribeForm()
    form2 = UnsubscribeForm()
    teachers = User.query.filter_by(type='teacher')
    subscribed = None
    if current_user.is_authenticated:
        subscribed = CourseMember.query.filter_by(user_id=current_user.id, course_id=course_id).first()

    if form.validate_on_submit() and not subscribed:
        course = CourseMember(user_id=current_user.id, course_id=course_id)
        db.session.add(course)
        db.session.commit()
        flash('You have subscribed to this course!', 'success')
        return redirect(url_for('account'))

    if form2.validate_on_submit() and subscribed:
        db.session.delete(subscribed)
        db.session.commit()
        flash('You been have Unsubscribed to this course!', 'success')
        return redirect(url_for('account'))

    course = Course.query.get_or_404(course_id)
    return render_template('course.html', calendar=calendar, title=course.name, course=course, form=form, form2=form2, show=not subscribed, teachers=teachers)

@app.route("/delete_course/<int:course_id>", methods=['GET', 'POST'])
def delete_course(course_id):
    course = Course.query.get_or_404(course_id)
    db.session.delete(course)
    db.session.commit()
    return redirect(url_for('index'))
