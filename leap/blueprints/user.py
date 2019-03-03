from flask import Blueprint, render_template, url_for, redirect, flash
from leap.models import User
from flask_login import login_required, current_user
from leap.decorators import confirm_required

user = Blueprint("user", __name__)


@user.route("/profile/<string:user_name>")
@login_required
def profile(user_name):
    user = User.query.filter_by(name=user_name).first()

    user_profile = {
        "name": user.name,
        "department": user.department,
        "post": user.post,
        "mobile": user.mobile,
        "signup_time": user.signup_time,
        "email": user.email,
        "its_creation": user.its_creation,
        "its_upload_files": user.its_upload_files
    }

    return render_template("/user/profile.html", user_profile=user_profile)




