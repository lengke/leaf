from flask import Blueprint, render_template, url_for, redirect, flash, abort
from leaf.models import User
from flask_login import login_required, current_user
from leaf.decorators import confirm_required

admin = Blueprint("admin", __name__)


@admin.route("/profile/<string:user_name>")
@login_required
def profile(user_name):
    user = User.query.filter_by(name=user_name).first()
    if user:
        return render_template("/admin/profile.html", user=user)
    else:
        abort(404)



