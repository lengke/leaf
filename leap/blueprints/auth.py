from flask import Blueprint, render_template, url_for, redirect, flash
from leap.forms import RegisterForm, LoginForm
from leap.ext import db
from flask_login import login_user, current_user
from leap.models import User

auth = Blueprint("auth", __name__)


# 新用户注册
@auth.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        pass
    form = RegisterForm()
    if form.validate_on_submit():
        name = form.name.data
        mobile = form.mobile.data
        email = form.email.data.lower()
        department = form.department.data
        post = form.post.data
        password = form.password.data
        new_user = User(
            name=name,
            mobile=mobile,
            email=email,
            department=department,
            post=post
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for(".login"))

    return render_template("auth/register.html", form=form)


# 用户登录
@auth.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(mobile=form.mobile.data).first()
        if user is not None and user.validate_password(form.password.data):
            if login_user(user, form.remember.data):
                flash('登录成功', 'info')
                return redirect("/")
            else:
                flash('Your account is blocked.', 'warning')
                return redirect(url_for('main.index'))
        flash('密码错误', 'warning')
    return render_template("auth/login.html", form=form)
