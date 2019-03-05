from flask import Blueprint, render_template, url_for, redirect, flash, abort
from leap.models import User
from flask_login import login_required, current_user
from leap.decorators import confirm_required

user = Blueprint("user", __name__)


@user.route("/profile/<string:user_name>")
@login_required
def profile(user_name):
    user = User.query.filter_by(name=user_name).first()
    if user:
        return render_template("/user/profile.html", user=user)
    else:
        abort(404)



