from flask import Blueprint, render_template, url_for, redirect
from leap.forms import RegisterForm, LoginForm
from leap.ext import db
from leap.models import User


auth = Blueprint("auth", __name__)


# 新用户注册
@auth.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    return render_template("auth/register.html", form=form)


# 用户登录
@auth.route("/login", methods=["GET", "POST"])
def login():
    return "用户登录"


