import os
import uuid

from flask import Flask, render_template, request, redirect, jsonify, url_for, flash, current_app
import requests
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from sqlalchemy import DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta

from werkzeug.security import generate_password_hash, check_password_hash

from flask_sqlalchemy import SQLAlchemy

from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

from datetime import datetime, date, timedelta
from sqlalchemy import and_
from flask_babel import Babel
from werkzeug.utils import secure_filename
import datetime
from datetime import datetime

app=Flask(__name__)

END_POINT="https://api.openweathermap.org/data/2.5/weather"


API_KEY="6ab73d57dd3ea5445996fd55de54ad44"
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    # Check if user is in paid_user table
    user = User.query.get(int(user_id))
    if user:
        return user
    # If not, check if user is in free_user table

    # If user is not in either table, return None
    return None

app.config['SECRET_KEY'] = 'any-secret-key-you-choose'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

babel = Babel(app)

with app.app_context():
    purchases = db.Table(
        'purchases',
        db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
        db.Column('course_id', db.Integer, db.ForeignKey('course.id'), primary_key=True)
    )


    class User(UserMixin, db.Model):
        id = db.Column(db.Integer, primary_key=True)
        phone = db.Column(db.String(100), unique=True)
        password = db.Column(db.String(100))
        name = db.Column(db.String(1000))
        email = db.Column(db.String(100))
        country = db.Column(db.String(100))
        subscription = db.Column(db.String(100))
        credit = db.Column(db.Integer)
        role = db.Column(db.String(100), default="user")
        pay = db.Column(db.Boolean(), default=False)
        message = db.Column(db.String(1000))
        starting_day = db.Column(db.DateTime)
        due_date = db.Column(db.DateTime)
        delegate = db.Column(db.DateTime)
        photo_filename = db.Column(db.String(1000))



    class PurchaseHistory(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
        course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
        purchase_date = db.Column(db.DateTime, default=datetime.utcnow)
        price = db.Column(db.Float)


    class TB(UserMixin, db.Model):
        id = db.Column(db.Integer, primary_key=True)
        phone = db.Column(db.String(100), unique=True)
        name = db.Column(db.String(1000))
        email = db.Column(db.String(100))
        description = db.Column(db.String(1000))
        sample = db.Column(db.String(100))
        approved = db.Column(db.Boolean(), default=False)
        teacher_photo = db.Column(db.String(255))

        def save_profile_photo(self, photo_file):
            filename = secure_filename(photo_file.filename)
            uploads_folder = os.path.join(current_app.root_path, 'static', 'uploads')
            if not os.path.exists(uploads_folder):
                os.makedirs(uploads_folder)
            unique_filename = str(uuid.uuid4()) + '_' + filename
            photo_path = os.path.join(uploads_folder, unique_filename)
            photo_file.save(photo_path)
            self.teacher_photo = unique_filename
            db.session.commit()


    class Teacher(UserMixin, db.Model):
        id = db.Column(db.Integer, primary_key=True)
        phone = db.Column(db.String(100), unique=True)
        password = db.Column(db.String(100))
        name = db.Column(db.String(1000))
        email = db.Column(db.String(100))
        rating = db.Column(db.Integer)
        teacher_photo = db.Column(db.String(255))
        courses = db.relationship('Course', back_populates='teacher', lazy=True)
        videos = db.relationship('Video', backref='teacher', lazy=True)
        credit = db.Column(db.Integer, default=0)
        credit_taken = db.Column(db.Integer, default=0)

        def save_profile_photo(self, photo_file):
            filename = secure_filename(photo_file.filename)
            uploads_folder = os.path.join(current_app.root_path, 'static', 'uploads')
            if not os.path.exists(uploads_folder):
                os.makedirs(uploads_folder)
            unique_filename = str(uuid.uuid4()) + '_' + filename
            photo_path = os.path.join(uploads_folder, unique_filename)
            photo_file.save(photo_path)
            self.teacher_photo = unique_filename
            db.session.commit()


    class Course(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        price = db.Column(db.Float)
        discount = db.Column(db.Integer)
        teacher_name = db.Column(db.String(100))
        description = db.Column(db.String(1000))
        sample = db.Column(db.String(100))
        grade = db.Column(db.String(100))
        section = db.Column(db.String(100))
        type = db.Column(db.String(100))
        country = db.Column(db.String(100))
        name = db.Column(db.String(100), nullable=False)
        course_image = db.Column(db.String(255))
        approved = db.Column(db.Boolean(), default=False)
        online_start_time = db.Column(db.DateTime)
        online_end_time = db.Column(db.DateTime)
        online_date = db.Column(db.Date)
        teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))
        teacher = db.relationship('Teacher', back_populates='courses', lazy=True)
        lessons = relationship('Lesson', backref='course', lazy=True)

        def __init__(self, name, teacher_name, description, grade, discount, sample, section, type, teacher_id,
                     country=None, course_image=None, online_start_time=None, online_end_time=None, online_date=None):
            self.name = name
            self.teacher_name = teacher_name
            self.description = description
            self.grade = grade
            self.discount = discount
            self.sample = sample
            self.section = section
            self.type = type
            self.country = country
            self.course_image = course_image
            self.online_start_time = online_start_time
            self.online_end_time = online_end_time
            self.online_date = online_date
            self.teacher_id = teacher_id

        def save_profile_photo(self, photo_file):
            filename = secure_filename(photo_file.filename)
            uploads_folder = os.path.join(current_app.root_path, 'static', 'uploads')
            if not os.path.exists(uploads_folder):
                os.makedirs(uploads_folder)
            unique_filename = str(uuid.uuid4()) + '_' + filename
            photo_path = os.path.join(uploads_folder, unique_filename)
            photo_file.save(photo_path)
            self.course_image = unique_filename
            db.session.commit()


    class LessonFileAssociation(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=False)
        file_id = db.Column(db.Integer, db.ForeignKey('file.id'), nullable=False)

        lesson = db.relationship('Lesson', backref='file_associations')
        file = db.relationship('File', backref='lesson_associations')

        def __init__(self, lesson_id, file_id):
            self.lesson_id = lesson_id
            self.file_id = file_id


    class Lesson(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(100))
        content = db.Column(db.String(1000))
        course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
        teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))

        # Define the relationship with the video table
        videos = db.relationship('Video', secondary='lesson_video_association', lazy='subquery',
                                 backref=db.backref('lessons', lazy=True))

        # Define the relationship with the file table
        files = db.relationship('File', secondary='lesson_file_association', lazy='subquery',
                                backref=db.backref('lessons', lazy=True))

        def __init__(self, title, content, course_id, teacher_id):
            self.title = title
            self.content = content
            self.course_id = course_id
            self.teacher_id = teacher_id


    class File(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100))
        description = db.Column(db.String(1000))
        path = db.Column(db.String(255))
        is_free = db.Column(db.Boolean, default=True)
        price = db.Column(db.Float)
        teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))
        teacher = db.relationship('Teacher', backref='files')

        def __init__(self, name, description, teacher_id, path, is_free=True, price=None, teacher=None):
            self.name = name
            self.description = description
            self.path = path
            self.teacher_id = teacher_id
            self.is_free = is_free
            self.price = price
            if teacher:
                self.teacher = teacher


    class Video(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(100), nullable=True)
        link = db.Column(db.String(1000))
        teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))
        unit_test = db.Column(db.String(100))

        def __init__(self, title, link, teacher_id, unit_test=None):
            self.title = title
            self.link = link
            self.teacher_id = teacher_id
            self.unit_test = unit_test


    # Define the association table after defining the Lesson and Video classes
    class LessonVideoAssociation(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=False)
        video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)

        lesson = db.relationship('Lesson', backref='video_associations')
        video = db.relationship('Video', backref='lesson_associations')

        def __init__(self, lesson_id, video_id):
            self.lesson_id = lesson_id
            self.video_id = video_id


    db.create_all()


class MyModelView(ModelView):
    def is_accessible(self):
        return True


admin = Admin(app)
admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView(Course, db.session))
admin.add_view(MyModelView(Teacher, db.session))
admin.add_view(MyModelView(Video, db.session))
admin.add_view(MyModelView(TB, db.session))
admin.add_view(MyModelView(Lesson, db.session))
admin.add_view(MyModelView(File, db.session))

@app.route("/")
def start ():
    return "welcom"


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('Passwords do not match!')
            return redirect(url_for('register'))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered!')
            return redirect(url_for('register'))

        hashed_password =  generate_password_hash(
            request.form.get('password'),
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = User(
            name=name,
            email=email,
            phone=phone,
            password=hashed_password,
            starting_day=datetime.now()
        )

        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        flash('Registration successful!')
        return redirect(url_for('dashboard'))

    return render_template('register.html')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            flash('Login failed. Check your email and password.')
            return redirect(url_for('login'))

        login_user(user)
        flash('Login successful!')
        return redirect(url_for('dashboard'))

    return render_template('login.html')
@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role=="user":
        return "this is the userdash borad"
    if current_user.role=="teacher":
        user_courses=Course.query.filter_by(teacher_id=current_user.id).all()

        return render_template("home/index.html",all_courses=user_courses)
    if current_user.role=="admin":
        return "this is the userdash borad"
    else:
        return  redirect("/register")


@app.route('/create_course', methods=['GET', 'POST'])
def create_course():
    if request.method == 'POST':
        name = request.form['name']
        teacher_name = request.form['teacher_name']
        description = request.form['description']
        grade = request.form['grade']
        discount = request.form['discount']
        sample = request.form['sample']
        section = request.form['section']
        course_type = request.form['type']
        country = request.form['country']
        online_start_time = request.form.get('online_start_time')
        online_end_time = request.form.get('online_end_time')
        online_date = request.form.get('online_date')
        teacher_id = request.form['teacher_id']

        # Parse datetime fields if provided
        if online_start_time:
            online_start_time = datetime.strptime(online_start_time, '%Y-%m-%dT%H:%M')
        if online_end_time:
            online_end_time = datetime.strptime(online_end_time, '%Y-%m-%dT%H:%M')
        if online_date:
            online_date = datetime.strptime(online_date, '%Y-%m-%d').date()

        course = Course(
            name=name,
            teacher_name=teacher_name,
            description=description,
            grade=grade,
            discount=discount,
            sample=sample,
            section=section,
            type=course_type,
            country=country,
            online_start_time=online_start_time,
            online_end_time=online_end_time,
            online_date=online_date,
            teacher_id=current_user.id
        )

        # Save course image if provided
        if 'course_image' in request.files:
            course.save_profile_photo(request.files['course_image'])

        db.session.add(course)
        db.session.commit()

        return redirect(url_for('dashboard'))  # Redirect to the course list or another relevant page

    return render_template('create_course.html')
@app.route('/course_description/<int:course_id>')
def course_description(course_id):
    course = Course.query.get_or_404(course_id)
    return render_template('course_description.html', course=course)
@app.route('/create_lesson/<int:course_id>', methods=['GET', 'POST'])
def create_lesson(course_id):
    course = Course.query.get_or_404(course_id)

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        teacher_id = course.teacher_id  # Assuming the lesson is created by the course teacher

        new_lesson = Lesson(
            title=title,
            content=content,
            course_id=course.id,
            teacher_id=teacher_id
        )
        db.session.add(new_lesson)
        db.session.commit()
        flash('Lesson created successfully!', 'success')
        return redirect(url_for('course_description', course_id=course.id))

    return render_template('create_lesson.html', course=course)
@app.route('/lesson/<int:lesson_id>', methods=['GET', 'POST'])
def lesson_description(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)

    if request.method == 'POST':
        title = request.form['title']
        link = request.form['link']
        teacher_id = lesson.teacher_id

        # Transform the YouTube link to the embeddable format
        if 'youtube.com/watch?v=' in link:
            link = link.replace('watch?v=', 'embed/')
        elif 'youtu.be/' in link:
            video_id = link.split('/')[-1]
            link = f'https://www.youtube.com/embed/{video_id}'

        new_video = Video(
            title=title,
            link=link,
            teacher_id=teacher_id
        )
        db.session.add(new_video)
        db.session.commit()

        lesson.videos.append(new_video)
        db.session.commit()

        flash('Video uploaded successfully!', 'success')
        return redirect(url_for('lesson_description', lesson_id=lesson.id))

    return render_template('lesson_description.html', lesson=lesson)


@app.route("/logout")
def logout():
    return "ddd"
if __name__ =="__main__":
    app.run(debug=True)