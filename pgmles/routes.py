import os
import secrets

from flask import flash, redirect, render_template, request, url_for, abort
from flask_login import current_user, login_required, login_user, logout_user
from PIL import Image
from calendar import Calendar as Month
from datetime import datetime

from .server import app, bcrypt, db
from .forms import LoginForm, NewCourseForm, AdminForm, RegistrationForm, SearchForm, SubscribeForm, UnsubscribeForm, UpdateAccountForm
from .models import Course, CourseMember, User


""" calendar-function to calculate days, etc. for calendar """
def make_calendar():
    weekdays = list(enumerate(['Ma', 'Di', 'Wo', 'Do', 'Vr', 'Za', 'Zo']))

    courses = [ None, None, None, None, None, None, None ]
    if current_user.is_authenticated:
        subscriptions = [ cm.course_id for cm in CourseMember.query.filter_by(user_id=current_user.id) ]
        courses = [ ' +\n'.join([ c.name for c in Course.query.filter_by(weekday=i) if c.id in subscriptions ]) for i in range(7) ]
    
    today = datetime.today()
    m = Month()

    rows = []
    for days in m.monthdayscalendar(today.year, today.month):
        rows.append([ (i, d, courses[i]) for i, d in enumerate(days) ])

    return { 'weekdays': weekdays, 'rows': rows }

""" index.html (home-page) route """
@app.route("/")
def index():
    courses = Course.query.all()
    subscriptions = []
    teachers = User.query.filter_by(type='teacher')
    if current_user.is_authenticated:
        subscriptions = [ cm.course_id for cm in CourseMember.query.filter_by(user_id=current_user.id) ]
    return render_template('index.html', calendar=make_calendar(), courses=courses, subs=subscriptions, teachers=teachers)

""" about.html route """
@app.route("/about")
def about():
    return render_template('about.html', calendar=make_calendar(), title='Over ons')

""" register.html route """
@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash('U bent al ingelogd', 'warning')
        return redirect('/')
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Uw profiel werd toegevoegd! U kan nu inloggen.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', calendar=make_calendar(), title='Registeren', form=form)

""" login.html route """
@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('U bent al ingelogd', 'warning')
        return redirect('/')
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            if bcrypt.check_password_hash(user.password, form.email.data):
                flash('Wij zullen aanbevelen uw wachtwoord weer te veranderen', 'warning')
            next_page = request.args.get('next')
            return redirect(next_page if next_page else '/')
        else:
            flash('Kon niet inloggen, is uw e-mail en wachtwoord juist?', 'danger')
    return render_template('login.html', calendar=make_calendar(), title='Inloggen', form=form)

""" logout route """
@app.route("/logout")
def logout():
    logout_user()
    return redirect('/')

""" save-picture function for account.html """
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

""" account.html route """
@app.route("/user/self", methods=[ 'GET', 'POST' ])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        if form.password.data:
            current_user.password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        db.session.commit()
        flash('Uw profiel is bewerkt!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', calendar=make_calendar(), title='Profiel', image_file=image_file, form=form)

""" course.html (course-info) route """
@app.route("/course/<int:course_id>", methods=[ 'GET', 'POST' ])
def course(course_id):
    sub_form = SubscribeForm()
    unsub_form = UnsubscribeForm()
    teachers = User.query.filter_by(type='teacher')
    subscribed = None
    if current_user.is_authenticated:
        subscribed = CourseMember.query.filter_by(user_id=current_user.id, course_id=course_id).first()

    if sub_form.validate_on_submit() and not subscribed:
        course = CourseMember(user_id=current_user.id, course_id=course_id)
        db.session.add(course)
        db.session.commit()
        flash('U bent nu ingeschreven!', 'success')
        return redirect('/')

    if unsub_form.validate_on_submit() and subscribed:
        db.session.delete(subscribed)
        db.session.commit()
        flash('U bent nu uitgeschreven!', 'success')
        return redirect('/')

    course = Course.query.get_or_404(course_id)
    return render_template('course.html', calendar=make_calendar(), title=course.name, course=course, sub_form=sub_form, unsub_form=unsub_form, subscribed=subscribed is not None, teachers=teachers)

""" course_overview.html route """
@app.route("/courses")
@login_required
def course_overview():
    if current_user.type not in [ "admin", "teacher" ]:
        flash('U mag deze website niet bereiken', 'error')
        return redirect('/')
    courses = [ (c, User.query.filter_by(id=c.id).first() ) for c in Course.query.all() ]
    return render_template('course_overview.html', calendar=make_calendar(), legend='Lesoverzicht', courses=courses)

""" new_course.html route """
@app.route("/course/new", methods=['GET', 'POST'])
@login_required
def new_course():
    if current_user.type not in [ "admin", "teacher" ]:
        flash('U mag deze website niet bereiken', 'error')
        return redirect('/')
    form = NewCourseForm()
    form.teacher_id.choices = [ (g.id, g.username) for g in User.query.filter_by(type='teacher') ]
    if form.validate_on_submit():
        course = Course(name=form.name.data, description=form.description.data, teacher_id=form.teacher_id.data, weekday=form.weekday.data, start=form.start.data, end=form.end.data, location=form.location.data)
        db.session.add(course)
        db.session.commit()
        flash('De les is toegevoegd!', 'success')
        return redirect(url_for('course_overview'))
    return render_template('new_course.html', calendar=make_calendar(), legend='Nieuwe les aanmaken', form=form)

""" new_course.html (update course) route """
@app.route("/course/<int:course_id>/update", methods=['GET', 'POST'])
@login_required
def update_course(course_id):
    if current_user.type not in [ "admin", "teacher" ]:
        flash('U mag deze website niet bereiken', 'error')
        return redirect('/')
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
        flash('De les is bewerkt!', 'success')
        return redirect(url_for('course_overview'))
    elif request.method == 'GET':
        form.name.data = course.name
        form.description.data = course.description
        form.teacher_id.data = course.teacher_id
        form.weekday.data = course.weekday
        form.start.data = course.start
        form.end.data = course.end
        form.location.data = course.location
    return render_template('new_course.html', calendar=make_calendar(), form=form, legend='Les aanpassen')

""" delete-course route """
@app.route("/course/<int:course_id>/delete", methods=['GET','POST'])
@login_required
def delete_course(course_id):
    if current_user.type not in [ "admin", "teacher" ]:
        flash('U mag deze website niet bereiken', 'error')
        return redirect('/')
    course = Course.query.get_or_404(course_id)
    db.session.delete(course)
    db.session.commit()
    return redirect(url_for('course_overview'))

""" admin.html route """
@app.route("/users", methods=['GET','POST'])
@login_required
def admin():
    if current_user.type != "admin":
        flash('U mag deze website niet bereiken', 'error')
        return redirect('/')
    form = SearchForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user == None:
            flash(f'Geen gebrukers gevonden met de gebruikersnaam: {form.username.data}!', 'danger')
        else:
            flash(f'Gebruiker gevonden met gebruikersnaam: {form.username.data}!', 'success')
            return redirect(url_for('admin_user', user_id= user.id))
    return render_template('admin.html', calendar=make_calendar(), form=form)

""" account-admin route """
@app.route("/user/<int:user_id>", methods=['GET','POST'])
@login_required
def admin_user(user_id):
    if current_user.type != "admin":
        flash('U mag deze website niet bereiken', 'error')
        return redirect('/')
    form = AdminForm()
    user = User.query.filter_by(id=user_id).first()
    image_file = url_for('static', filename='profile_pics/' + user.image_file)
    if form.validate_on_submit():
        user.type = form.type.data
        db.session.commit()
        flash(f'De gebruiker {user.username} is nu een {user.type}', 'success')
        return redirect(url_for('admin'))
    elif request.method == 'GET':
        form.type.data = user.type
    return render_template('admin_user.html', calendar=make_calendar(), form=form, user=user, image_file=image_file)

""" delete-user route """
@app.route("/user/<int:user_id>/delete", methods=['GET','POST'])
@login_required
def delete_user(user_id):
    if current_user.type != "admin":
        flash('U mag deze website niet bereiken', 'error')
        return redirect('/')
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash(f'De gebruiker {user.username} werd verwijdert', 'success')
    return redirect(url_for('admin'))

""" reset user's password route """
@app.route("/user/<int:user_id>/reset", methods=['GET','POST'])
@login_required
def reset_user(user_id):
    if current_user.type != "admin":
        flash('U mag deze website niet bereiken', 'error')
        return redirect('/')
    user = User.query.get_or_404(user_id)
    user.password = bcrypt.generate_password_hash(user.email).decode('utf-8')
    db.session.commit()
    flash(f'{user.username}\'s is nu zijn/haar e-mail', 'success')
    return redirect(url_for('admin'))

""" 404 not found handler """
@app.errorhandler(404)
def not_found(error):
    flash(f"Deze pagina werd niet gevonden", 'danger')
    return index() # geen redirect om de '/bla' te houden
