from flask import Blueprint, render_template, url_for, redirect, flash, abort
from leaf.models import User
from leaf.ext import db
from flask_login import login_required, current_user
from leaf.decorators import confirm_required


admin = Blueprint("admin", __name__)

# 查看用户详情页
@admin.route("/profile/<string:user_name>")
@login_required
def profile(user_name):
    user = User.query.filter_by(name=user_name).first()
    if user:
        return render_template("/admin/profile.html", user=user)
    else:
        abort(404)


# 用户管理
@admin.route("/manage-users")
@login_required
@confirm_required
def manage_users():

    if not current_user.is_admin:
        flash("后台管理功能只对系统管理员开放", "warning")
        return redirect(url_for("main.index"))

    users = User.query.order_by(User.signup_time.desc()).all()
    return render_template("admin/manage_users.html", users=users)


# 封禁/解封用户
@admin.route("/toggle-user/<string:user_name>", methods=["POST", "GET"])
@login_required
@confirm_required
def toggle_block_user(user_name):

    if not current_user.is_admin:
        flash("后台管理功能只对系统管理员开放", "warning")
        return redirect(url_for("main.index"))

    user = User.query.filter_by(name=user_name).first()
    user_status = user.is_blocked
    user.is_blocked = not user_status
    db.session.commit()
    return redirect(url_for("admin.manage_users"))




