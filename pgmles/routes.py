import os
import secrets

from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from PIL import Image

from . import app, bcrypt, calendar, db
from .forms import (LoginForm, RegistrationForm, SubscribeForm, UnsubscribeForm, UpdateAccountForm, NewCourseForm, SearchForm, PermissionForm)
from .models import Course, CourseMember, User


@app.route("/")
def index():
    courses = Course.query.all()
    subscriptions = []
    teachers = [[teacher.id, teacher.username] for teacher in User.query.filter_by(type='teacher')]
    if current_user.is_authenticated:
        subscriptions = [cm.course_id for cm in CourseMember.query.filter_by(
            user_id=current_user.id)]
#        for coursemember in members:
#            course[] = Course.id
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
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user = User(username=form.username.data,
                    email=form.email.data, password=hashed_password)
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
            return redirect(next_page) if next_page else redirect('/')
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
    picturepath = os.path.join(
        app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picturepath)

    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
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
    image_file = url_for(
        'static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', calendar=calendar, title='Account', image_file=image_file, form=form)


@app.route("/course_overview")
@login_required
def course_overview():
    if not(current_user.type == "admin" or current_user.type == "teacher"):
        abort(403)
    courses = Course.query.all()
    type = current_user.type
    return render_template('course_overview.html', calendar=calendar, title='Administration Page', courses=courses, type=type)


@app.route("/course_overview/new_course", methods=['GET', 'POST'])
@login_required
def new_course():
    if not(current_user.type == "admin" or current_user.type == "teacher"):
        abort(403)
    form = NewCourseForm()
    form.teacher_id.choices = [(g.id, g.username) for g in User.query.filter_by(type='teacher')]
    if form.validate_on_submit():
        course = Course(name=form.name.data, description=form.description.data,\
                        teacher_id=form.teacher_id.data, weekday=form.weekday.data,\
                        start=form.start.data, end=form.end.data, location=form.location.data)
        db.session.add(course)
        db.session.commit()
        flash('The course has been created!', 'success')
        return redirect(url_for('admin'))
    return render_template('new_course.html', calendar=calendar, title='New Course', form=form)


@app.route("/course_overview/course_update/<int:course_id>", methods=['GET', 'POST'])
@login_required
def update_course(course_id):
    if not(current_user.type == "admin" or current_user.type == "teacher"):
        abort(403)
    form = NewCourseForm()
    form.teacher_id.choices = [(g.id, g.username) for g in User.query.filter_by(type='teacher')]
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
        return redirect(url_for('course_overview'))
    elif request.method == 'GET':
        form.name.data = course.name
        form.description.data = course.description
        form.teacher_id.data = course.teacher_id
        form.weekday.data = course.weekday
        form.start.data = course.start
        form.end.data = course.end
        form.location.data = course.location
    return render_template('update_course.html', calendar=calendar, form=form, legend='Update Language')


@app.route("/course/<int:course_id>", methods=['GET', 'POST'])
def course(course_id):
    form = SubscribeForm()
    form2 = UnsubscribeForm()
    teachers = [[teacher.id, teacher.username] for teacher in User.query.filter_by(type='teacher')]
    subscribed = None
    if current_user.is_authenticated:
        subscribed = CourseMember.query.filter_by(
            user_id=current_user.id, course_id=course_id).first()

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

@app.route("/delete_course/<int:course_id>", methods=['GET','POST'])
@login_required
def delete_course(course_id):
    if not(current_user.type == "admin"):
        abort(403)
    course = Course.query.get_or_404(course_id)
    db.session.delete(course)
    db.session.commit()
    return redirect(url_for('index'))

@app.route("/admin")
@login_required
def admin():
    if not(current_user.type == "admin"):
        abort(403)
    courses = Course.query.all()
    return render_template('admin.html', calendar=calendar, courses=courses)

@app.route("/permissions", methods=['GET','POST'])
@login_required
def permissions():
    if not(current_user.type == "admin"):
        abort(403)
    form = SearchForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user == None:
            flash(f'No user found in the database with username: {form.username.data}', 'danger')
        else:
            flash(f'Username found in the database with username: {form.username.data}', 'success')
            return redirect(url_for('updatePermissions', user_id= user.id))
    return render_template('permissions.html', calendar=calendar, form=form)

@app.route("/permissions/update/<int:user_id>", methods=['GET','POST'])
@login_required
def updatePermissions(user_id):
    if not(current_user.type == "admin"):
        abort(403)
    form = PermissionForm()
    user = User.query.filter_by(id=user_id).first()
    image_file = url_for(
        'static', filename='profile_pics/' + user.image_file)
    if form.validate_on_submit():
        user.type = form.type.data
        db.session.commit()
        flash(f'The permissions for user: {user.username} have been set to {user.type}', 'success')
        return redirect(url_for('permissions'))
    elif request.method == 'GET':
        form.type.data = user.type
    return render_template('updatepermissions.html', calendar=calendar, form=form, user=user, image_file=image_file)
