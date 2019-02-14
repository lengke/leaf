from flask import Blueprint, render_template, url_for, redirect
from leap.forms import RegisterForm, LoginForm
from leap.ext import db
from leap.models import User

auth = Blueprint("auth", __name__)


# 新用户注册
@auth.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():

        name = form.name.data
        mobile = form.mobile.data
        email = StringField("公司邮箱", validators=[DataRequired()])
        department = StringField("所属部门", validators=[DataRequired()])
        post = StringField("职位名称", validators=[DataRequired()])
        password

    return render_template("auth/register.html", form=form)


# 用户登录
@auth.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    return render_template("auth/login.html", form=form)
