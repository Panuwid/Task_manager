from flask import render_template, flash, redirect, url_for, request
from app import db
from app.forms import RegistrationForm, LoginForm, TaskForm
from app.models import User, Task
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app import app

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, password=form.password.data)  # ในที่นี้ เราควรทำการแฮชพาสเวิร์ดด้วย แต่เพื่อความง่ายจะข้ามไป
        db.session.add(user)
        db.session.commit()
        flash('สมัครสมาชิกสำเร็จ! กรุณาเข้าสู่ระบบ.')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or user.password != form.password.data:  # ในที่นี้ เราควรตรวจสอบพาสเวิร์ดที่ถูกแฮช แต่เพื่อความง่ายจะข้ามไป
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('dashboard')
        return redirect(next_page)
    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    tasks = current_user.tasks.order_by(Task.timestamp.desc()).all()
    return render_template('dashboard.html', title='Dashboard', tasks=tasks)

@app.route('/create_task', methods=['GET', 'POST'])
@login_required
def create_task():
    form = TaskForm()
    if form.validate_on_submit():
        task = Task(title=form.title.data, description=form.description.data, due_date=form.due_date.data, status=form.status.data, author=current_user)
        db.session.add(task)
        db.session.commit()
        flash('สร้างงานสำเร็จ!')
        return redirect(url_for('dashboard'))
    return render_template('create_task.html', title='Create Task', form=form)

@app.route('/edit_task/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.author != current_user:
        flash('คุณไม่มีสิทธิ์แก้ไขงานนี้')
        return redirect(url_for('dashboard'))
    form = TaskForm()
    if form.validate_on_submit():
        task.title = form.title.data
        task.description = form.description.data
        task.due_date = form.due_date.data
        task.status = form.status.data
        db.session.commit()
        flash('แก้ไขงานสำเร็จ!')
        return redirect(url_for('dashboard'))
    elif request.method == 'GET':
        form.title.data = task.title
        form.description.data = task.description
        form.due_date.data = task.due_date
        form.status.data = task.status
    return render_template('edit_task.html', title='Edit Task', form=form)

@app.route('/delete_task/<int:task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.author != current_user:
        flash('คุณไม่มีสิทธิ์ลบงานนี้')
        return redirect(url_for('dashboard'))
    db.session.delete(task)
    db.session.commit()
    flash('ลบงานสำเร็จ!')
    return redirect(url_for('dashboard'))
