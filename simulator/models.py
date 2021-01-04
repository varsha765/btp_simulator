from datetime import datetime
from simulator import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='def_mach.jpg')
    password = db.Column(db.String(60), nullable=False)
    machines = db.relationship('Machine', backref='author', lazy=True)
    buffers = db.relationship('Buffer', backref='author', lazy=True)
    jobs = db.relationship('Job', backref='author', lazy=True)


    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Machine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    eeta = db.Column(db.Integer,nullable=False,  default = 0)
    beta = db.Column(db.Integer,nullable=False, default= 0)
    mean = db.Column(db.Integer,nullable=False, default=0)
    sd = db.Column(db.Integer,nullable=False, default = 0)
    image_file=db.Column(db.String(100), nullable=False, default='def_mach.jpg')

    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Machine('{self.id}','{self.name}','{self.eeta}', '{self.beta}','{self.mean}', '{self.sd}', '{self.image_file}')"


class Buffer(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(200), nullable=False, unique=True)
    capacity=db.Column(db.Integer, nullable=False, default=100)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    def  __repr__(self):
        return f"Buffer('{self.id}', '{self.name}', '{self.capacity}')"

class Job(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(200), nullable=False)
    image_file=db.Column(db.String(100), nullable=False, default='def_mach.jpg')
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    jobtimes = db.relationship('JobTime', backref='jobname', lazy=True)
    def  __repr__(self):
        return f"Job('{self.id}', '{self.name}')"

class JobTime(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    machine_name=db.Column(db.String(200), nullable=False)
    setup=db.Column(db.Integer, nullable=False, default=0)
    processing=db.Column(db.Integer, nullable=False, default=0)
    postprocessing=db.Column(db.Integer, nullable=False, default=0)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    job_id=db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    def  __repr__(self):
        return f"JobTime('{self.id}', '{self.machine_name}', '{self.setup}', '{self.job_id}', '{self.jobname}')"

