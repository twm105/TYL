from datetime import datetime
from hashlib import md5
from time import time
from flask import current_app, redirect, url_for
from flask_login import UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import json
from app import db, login, admin
from flask_admin.contrib.sqla import ModelView


# TODO Add image resize method?


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    forename = db.Column(db.String(64), index=True)
    surname = db.Column(db.String(64), index=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    records = db.relationship('Record', backref='user', lazy='dynamic')
    auth_level = db.Column(db.Integer, index=True, default=0)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<User {}, {}>'.format(self.surname, self.forename)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'],
            algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


class Record(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    site_id = db.Column(db.Integer, db.ForeignKey('site.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    count = db.Column(db.Integer)
    comments = db.Column(db.String(280))
    record_time = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<Record {}>'.format(self.count)


class Site(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    records = db.relationship('Record', backref='site', lazy='dynamic')
    cameras = db.relationship('Camera', backref='site', lazy='dynamic')
    latest_count = db.Column(db.Integer, index=True)
    when_registered = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    image = db.Column(db.String(128), index=True, unique=True)

    def __repr__(self):
        return '<Site {}>'.format(self.name)


class Camera(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    site_id = db.Column(db.Integer, db.ForeignKey('site.id'))
    last_call = db.Column(db.DateTime, index=True)
    when_registered = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    image = db.Column(db.String(128), index=True, unique=True)

    def __repr__(self):
        return '<Camera {}>'.format(self.name)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and not current_user.is_anonymous and (current_user.auth_level == 1)

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth.login'))


admin.add_view(AdminModelView(User, db.session))
admin.add_view(AdminModelView(Record, db.session))
admin.add_view(AdminModelView(Site, db.session))
admin.add_view(AdminModelView(Camera, db.session))


# admin.add_view(ModelView(User, db.session))
# admin.add_view(ModelView(Record, db.session))
# admin.add_view(ModelView(Site, db.session))
# admin.add_view(ModelView(Camera, db.session))