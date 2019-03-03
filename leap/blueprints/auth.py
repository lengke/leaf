from flask import Blueprint, render_template, url_for, redirect, flash
from leap.forms import RegisterForm, LoginForm, ForgetPasswordForm, ResetPasswordForm
from leap.ext import db
from flask_login import login_user, current_user, logout_user, login_required
from leap.models import User
from leap.utils import redirect_back, generate_token, validate_token, flash_errors
from leap.emails import send_confirm_email, send_reset_password_email
from leap.settings import Operations


auth = Blueprint("auth", __name__)


# 新用户注册
@auth.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        flash("请先退出登录", "info")
        return redirect(url_for("main.index"))


    form = RegisterForm()
    if form.validate_on_submit():
        # 如果新用户跟已有用户重名则为其加上部门和职位名以区分
        if User.query.filter_by(name=form.name.data).first():
            name = form.name.data + "_" +form.department.data + "_" +form.post.data
        else:
            name = form.name.data
        mobile = form.mobile.data
        # 将Email地址统一小写化处理
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
        # 生成确认新用户的token
        token = generate_token(user=new_user, operation='confirm')
        # 向用户邮箱发送带有token的确认邮件
        send_confirm_email(user=new_user, token=token)
        flash('请到您的公司邮箱点击邮件中的确认链接', 'info')
        return redirect(url_for("auth.login"))
    flash_errors(form=form)
    return render_template("auth/register.html", form=form)


# 用户登录
@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(mobile=form.mobile.data).first()
        if user is not None and user.validate_password(form.password.data):
            if login_user(user, form.remember.data):
                flash('登录成功', 'info')
                return redirect_back()
            else:
                flash('账号被锁，请联系管理员', 'warning')
                return redirect_back()
        flash('手机号或密码错误', 'warning')
    return render_template("auth/login.html", form=form)


# 用户退出登录
@auth.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    flash("你已退出登录", "info")
    return redirect(url_for("main.index"))


# 确认新注册用户
@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.is_confirmed:
        flash("您已进行过邮箱验证，请勿重复操作", "info")
        return redirect(url_for('main.index'))

    if validate_token(user=current_user, token=token, operation=Operations.CONFIRM):
        flash('邮件验证成功，祝使用愉快', 'success')
        return redirect(url_for('main.index'))
    else:
        flash('验证失败', 'danger')
        return redirect(url_for('auth.resend_confirm_email'))


# 重新发送确认邮件
@auth.route('/resend-confirm-email')
@login_required
def resend_confirm_email():
    if current_user.is_confirmed:
        return redirect(url_for('main.index'))

    token = generate_token(user=current_user, operation=Operations.CONFIRM)
    send_confirm_email(user=current_user, token=token)
    flash('新的确认邮件已发送，请检查公司邮箱', 'info')
    return redirect(url_for('main.index'))


# 忘记密码
@auth.route('/forget-password', methods=['GET', 'POST'])
def forget_password():
    if current_user.is_authenticated:
        flash("您已登录，不能重置密码", "info")
        return redirect(url_for("main.index"))

    form = ForgetPasswordForm()

    if form.validate_on_submit():
        mobile = form.mobile.data
        user = User.query.filter_by(mobile=mobile).first()
        if user:
            token = generate_token(user=user, operation=Operations.RESET_PASSWORD)
            send_reset_password_email(user=user, token=token)
            flash("密码重置邮件已发送", "info")
            return redirect(url_for("auth.login"))
        flash("输入的手机号错误", "warning")
        return redirect(url_for("auth.forget_password"))

    return render_template("auth/forget_password.html", form=form)


# 更改新密码
@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        flash("您已登录，不能重置密码", "info")
        return redirect(url_for('main.index'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        mobile = form.mobile.data
        user = User.query.filter_by(mobile=mobile).first()
        if user is None:
            return redirect(url_for('main.index'))
        if validate_token(user=user, token=token, operation=Operations.RESET_PASSWORD,
                          new_password=form.password.data):
            flash('密码更新成功，请重新登录', 'success')
            return redirect(url_for('.login'))
        else:
            flash('验证失败', 'danger')
            return redirect(url_for('.forget_password'))
    return render_template('auth/reset_password.html', form=form)

