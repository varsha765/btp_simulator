import secrets
import os
from PIL import Image
from flask import render_template, url_for, flash, redirect, request
from simulator import app, db
from simulator.forms import RegistrationForm, LoginForm, UpdateAccountForm, MachineForm, BufferForm, JobForm, JobTimeForm
from simulator.models import User, Machine, Buffer, Job, JobTime
from flask_login import login_user, current_user, logout_user, login_required



@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        #hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=form.password.data)
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
        if user and user.password==form.password.data:
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
    picture_path = os.path.join(app.root_path, 'static/images', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

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
    image_file = url_for('static', filename='images/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)


@app.route("/machine", methods=['GET', 'POST'])
@login_required
def machine():
    
    form = MachineForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            
            machine =Machine(name=form.name.data, eeta=form.eeta.data,beta=form.beta.data,mean=form.mean.data, sd=form.sd.data, image_file=picture_file, author=current_user)
        else:
            machine =Machine(name=form.name.data, eeta=form.eeta.data,beta=form.beta.data,mean=form.mean.data, sd=form.sd.data, author=current_user)
        db.session.add(machine)
        db.session.commit()
        flash('Your machine has been created!', 'success')
        return redirect(url_for('machine'))
    elif request.method == 'GET':
        tasks = Machine.query.order_by(Machine.date_created).all()
        
        return render_template('machine.html', title='Machine',form=form, tasks=tasks)


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = Machine.query.get_or_404(id)
    form = MachineForm()
    if form.validate_on_submit():
        task.name=form.name.data
        task.eeta=form.eeta.data
        task.beta=form.beta.data
        task.mean=form.mean.data
        task.sd=form.sd.data
        if form.picture.data:
            task.image_file=save_picture(form.picture.data)

        

        try:
            db.session.commit()
            flash('Your machine has been updated!', 'success')
            return redirect('/machine')
        except:
            return 'There was an issue updating your task'
    elif request.method == 'GET':
        form.name.data = task.name
        form.eeta.data = task.eeta
        form.beta.data = task.beta
        form.mean.data = task.mean
        form.sd.data = task.sd
        form.picture.data=task.image_file
        
        
    
    return render_template('update.html', task=task, form=form)

@app.route('/show/<int:id>', methods=['GET', 'POST'])
@login_required
def show(id):
    task=Machine.query.get_or_404(id)
    image_file=url_for('static', filename='images/'+task.image_file)
    try:
        return render_template('show.html', task=task, image_file=image_file)
    except:
        return 'There was a problem showing that machine'

@app.route('/delete/<int:id>')
@login_required
def delete(id):
    task_to_delete = Machine.query.get_or_404(id)
    

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        
        return redirect('/machine')
    except:
        return 'There was a problem deleting that task' 



@app.route('/buffer', methods=['POST', 'GET'])
@login_required
def buffer():
    
    form = BufferForm()
    if form.validate_on_submit():
        
            
            
        
        buffer =Buffer(name=form.name.data, capacity=form.capacity.data, author=current_user)
        db.session.add(buffer)
        db.session.commit()
        flash('Your buffer has been created!', 'success')
        return redirect(url_for('buffer'))
    elif request.method == 'GET':
        tasks = Buffer.query.order_by(Buffer.date_created).all()
        
        return render_template('buffer.html', title='Buffer',form=form, tasks=tasks)


@app.route('/deleteb/<int:id>')
def deleteb(id):
    task_to_delete = Buffer.query.get_or_404(id)
    

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        
        return redirect('/buffer')
    except:
        return 'There was a problem deleting that task'

@app.route('/updateb/<int:id>', methods=['GET', 'POST'])
def updateb(id):
    task = Buffer.query.get_or_404(id)
    form = BufferForm()
    if form.validate_on_submit():
        task.name=form.name.data
        task.capacity=form.capacity.data
        
        
        

        try:
            db.session.commit()
            flash('Your Buffer has been updated!', 'success')
            return redirect('/buffer')
        except:
            return 'There was an issue updating your buffer'
    elif request.method == 'GET':
        form.name.data = task.name
        form.capacity.data = task.capacity
        
        
        
    
    return render_template('updateb.html', task=task, form=form)

@app.route('/showb/<int:id>', methods=['GET', 'POST'])
def showb(id):
    task=Buffer.query.get_or_404(id)
    try:
        return render_template('showb.html', task=task)
    except:
        return 'There was a problem showing that buffer'


@app.route("/job", methods=['GET', 'POST'])
@login_required
def job():
    
    form = JobForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            
            job =Job(name=form.name.data,  image_file=picture_file, author=current_user)
        else:
            job =Job(name=form.name.data,  author=current_user)
        db.session.add(job)
        db.session.commit()
        flash('Your job has been created!', 'success')
        return redirect(url_for('job'))
    elif request.method == 'GET':
        tasks = Job.query.order_by(Job.date_created).all()
        
        return render_template('job.html', title='Job',form=form, tasks=tasks)
@app.route('/updatej/<int:id>', methods=['GET', 'POST'])
def updatej(id):
    task = Job.query.get_or_404(id)
    form = JobForm()
    if form.validate_on_submit():
        task.name=form.name.data
        
        if form.picture.data:
            task.image_file=save_picture(form.picture.data)

        

        try:
            db.session.commit()
            flash('Your job has been updated!', 'success')
            return redirect('/job')
        except:
            return 'There was an issue updating your job'
    elif request.method == 'GET':
        form.name.data = task.name
        
        form.picture.data=task.image_file
        
        
    
    return render_template('updatej.html', task=task, form=form)

@app.route('/showj/<int:id>', methods=['GET', 'POST'])
@login_required
def showj(id):
    task=Job.query.get_or_404(id)
    task_time=task.jobtimes
    image_file=url_for('static', filename='images/'+task.image_file)
    try:
        return render_template('showj.html', task=task,task_time=task_time, image_file=image_file)
    except:
        return 'There was a problem showing that job'

@app.route('/deletej/<int:id>')
@login_required
def deletej(id):
    task_to_delete = Job.query.get_or_404(id)
    

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        
        return redirect('/job')
    except:
        return 'There was a problem deleting that task' 


@app.route('/jobtime/<int:id>', methods=['GET','POST'])
@login_required
def jobtime(id):
    form = JobTimeForm()
    if form.validate_on_submit():
        
        jobtime=JobTime(machine_name=form.machine_name.data,setup=form.setup.data, processing=form.processing.data, postprocessing=form.postprocessing.data,  job_id=id)
        db.session.add(jobtime)
        db.session.commit()
        flash('Your job has been created!', 'success')
        return redirect(url_for('jobtime', id=id))
    elif request.method == 'GET':
        tasks = JobTime.query.filter_by(job_id=id).order_by(JobTime.date_created).all()
        
        return render_template('jobtime.html', title='Job Time',form=form, tasks=tasks, id=id)

@app.route('/deletejt/<int:job_id>/<int:id>', methods=["GET","POST"])
@login_required
def deletejt(job_id,id):
    task_to_delete=JobTime.query.get_or_404(id)
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        
        return redirect(url_for('jobtime', id=job_id))
    except:
        return 'There was a problem deleting that task' 

@app.route('/updatejt/<int:job_id>/<int:id>', methods=['GET', 'POST'])
def updatejt(job_id,id):
    task = JobTime.query.get_or_404(id)
    form = JobTimeForm()
    if form.validate_on_submit():
        task.machine_name=form.machine_name.data
        task.setup=form.setup.data
        task.processing=form.processing.data
        task.postprocessing=form.postprocessing.data

        

        try:
            db.session.commit()
            flash('Your job time has been updated!', 'success')
            return redirect(url_for('jobtime', id=job_id))
        except:
            return 'There was an issue updating your job'
    elif request.method == 'GET':
        form.machine_name.data = task.machine_name
        form.setup.data=task.setup
        form.processing.data=task.processing
        
        form.postprocessing.data=task.postprocessing

        
    
    return render_template('updatejt.html', task=task, form=form, job_id=job_id)

@app.route("/line")
def line():
    return render_template('line.html')





        
    

    