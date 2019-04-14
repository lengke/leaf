from flask import Blueprint, render_template, url_for, redirect, flash
from leaf.forms import RegisterForm, LoginForm, ForgetPasswordForm, ResetPasswordForm, ChangePasswordForm, ChangeEmailForm, ChangeInfoForm
from leaf.ext import db
from flask_login import login_user, current_user, logout_user, login_required, fresh_login_required, login_fresh, confirm_login
from leaf.models import User
from leaf.utils import redirect_back, generate_token, validate_token, flash_errors
from leaf.emails import send_confirm_email, send_reset_password_email, send_change_email_email
from leaf.settings import Operations


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
        # 判断是否为被封禁用户
        if user.is_blocked:
            flash('您的账号已被封禁，请联系管理员', 'warning')
            return redirect_back()
        # 没有被封禁则继续判断用户名和密码是否正确
        elif user is not None and user.validate_password(form.password.data):
            if login_user(user, form.remember.data):
                flash('登录成功', 'info')
                return redirect_back()
        elif not user.validate_password(form.password.data):
            flash('密码错误', 'warning')
            return render_template("auth/login.html", form=form)

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


# 忘记密码之后，更改新密码
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



# 用户主动修改密码
@auth.route("/change-password", methods=["GET", "POST"])
@fresh_login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit() and current_user.validate_password(form.old_password.data):
        current_user.set_password(form.new_password.data)
        db.session.commit()
        flash("密码修改成功，请用新密码重新登录", "success")
        logout_user()
        return redirect(url_for("main.index"))
    return render_template("auth/change_password.html", form=form)


# 非fresh_login的用户重新认证
@auth.route("/re-authenticate", methods=["POST", "GET"])
@login_required
def re_authenticate():
    # 先判断用户的登录是否新鲜
    if login_fresh():
        return redirect(url_for("main.index"))
    form = LoginForm()
    if form.validate_on_submit() and current_user.validate_password(form.password.data):
        # 将用户会话重新设置为新鲜的
        confirm_login()
        return redirect_back()
    return render_template("auth/login.html", form=form)


# 用户主动修改邮箱地址
@auth.route("/change-email", methods=["Get", "POST"])
@fresh_login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        token = generate_token(user=current_user, operation=Operations.CHANGE_EMAIL, new_email=form.new_email.data.lower())
        # 向用户邮箱发送带有token的确认邮件
        send_change_email_email(to=form.new_email.data, user=current_user, token=token)
        flash('请进入新邮箱点击确认邮件中的链接', 'info')
        return redirect(url_for("auth.login"))
    return render_template("auth/change-email.html", form=form)


# 验证用户修改后的邮箱
@auth.route('/change-email/<token>')
@login_required
def change_email(token):
    if validate_token(user=current_user, token=token, operation=Operations.CHANGE_EMAIL):
        flash('邮箱修改成功！', 'success')
        return redirect(url_for('main.index'))
    else:
        flash('邮箱验证失败，请重试', 'warning')
        return redirect(url_for('auth.change_email_request'))


# 修改用户其他个人信息
@auth.route("/change-info", methods=["GET", "POST"])
@fresh_login_required
def change_info():
    form = ChangeInfoForm()
    if form.validate_on_submit():
        if form.new_name.data:
            current_user.name = form.new_name.data
        if form.new_mobile.data:
            current_user.mobile = form.new_mobile.data
        if form.new_department.data:
            current_user.department = form.new_department.data
        if form.new_post.data:
            current_user.post = form.new_post.data
        db.session.commit()
        flash("个人资料更新成功", "info")
        return redirect(url_for("main.index"))

    return render_template("auth/change-info.html", form=form)
