import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from flaskblog import app, db, bcrypt
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, LanguageForm, PostForm, SubscribeForm, UnsubscribeForm
from flaskblog.models import User, Language, Classes
from flask_login import login_user, current_user, logout_user, login_required


@app.route("/")
@app.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    languages = Language.query.all()
    subs = Classes.query.filter_by(user_id=current_user.id)
    lijst = []
    for sub in subs:
        lijst.append(sub.language_id)
    return render_template('home.html', languages=languages, subs=lijst, subscribed="subscribed")


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

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
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)

@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        #post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Post',
                            form=form, legend='New Post')

@app.route("/admin")
def admin():
    languages = Language.query.all()
    return render_template('admin.html', title = 'Administration Page', languages = languages)

@app.route("/admin/update/<int:lang_id>", methods=['GET', 'POST'])
def update_lang(lang_id):
    form = LanguageForm()
    lang = Language.query.get_or_404(lang_id)
    if form.validate_on_submit():
        lang.name = form.name.data
        lang.info = form.info.data
        db.session.commit()
        flash('The course has been updated!', 'success')
        return redirect(url_for('home', lang_id=lang.id))
    elif request.method == 'GET':
        form.name.data = lang.name
        form.info.data = lang.info
    return render_template('update_lang.html', form=form, legend='Update Language')

@app.route("/course/<int:course_id>", methods=['GET', 'POST']) 
def course(course_id):
    form = SubscribeForm()
    form2 = UnsubscribeForm()
    subscription = Classes.query.filter_by(user_id=current_user.id, language_id=course_id).first()
    show = True
    if subscription:
        show = False
    if form.validate_on_submit() and show == True:
        course = Classes(user_id = current_user.id, language_id = course_id, teacher_id = 1, location = "hier")
        db.session.add(course)
        db.session.commit()
        flash('You have subscribed to this course!', 'success')
        return redirect(url_for('account'))
    if form2.validate_on_submit() and show == False:
        db.session.delete(subscription)
        db.session.commit()
        flash('You been have Unsubscribed to this course!', 'success')
        return redirect(url_for('account'))
    course = Language.query.get_or_404(course_id)
    return render_template('course.html', title=course.name, course=course, form=form, form2=form2, show=show)

@app.route("/course/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post', 
                            form=form, legend='Update Post')

@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    #post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))

@app.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    #posts = Post.query.filter_by(author=user)\
    #    .order_by(Post.date_posted.desc())\
        #.paginate(page=page, per_page=5)
    #return render_template('user_post.html', posts=posts, user=user)
