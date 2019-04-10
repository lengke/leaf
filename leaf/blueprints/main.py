from flask import Blueprint, render_template, url_for, redirect, abort, flash, request, current_app, send_from_directory
from leaf.forms import ProjectForm, UploadForm, ChooseMemberForm, ChangeProjectForm, ChangeFileForm, ConfirmDeleteForm
from leaf.ext import db
from leaf.models import Project, File, User
from flask_login import login_required, current_user, fresh_login_required
from leaf.decorators import confirm_required
from leaf.utils import redirect_back
import os, uuid
from leaf.emails import send_add_new_member_email, send_upload_file_email

main = Blueprint("main", __name__)


# 网站首页
@main.route("/", methods=["GET", "POST"])
def index():
    # db.drop_all()
    # db.create_all()

    latest_project = Project.query.order_by(Project.create_time.desc()).first()
    latest_file = File.query.order_by(File.upload_time.desc()).first()
    projects_sum = Project.query.count()
    files_sum = File.query.count()
    users_sum = User.query.count()

    return render_template("main/index.html",
                           files_sum=files_sum,
                           projects_sum=projects_sum,
                           users_sum=users_sum,
                           latest_project=latest_project,
                           latest_file=latest_file
                           )


# 显示所有项目列表
@main.route("/allprojects", methods=["GET", "POST"])
@login_required
@confirm_required
def show_all_projects():
    projects = Project.query.order_by(Project.create_time.desc()).all()
    return render_template("main/show_all_projects.html", projects=projects)


# 创建新项目
@main.route("/create", methods=["GET", "POST"])
@login_required
@confirm_required
def create_project():
    form = ProjectForm()
    if form.validate_on_submit():
        name = form.name.data
        description = form.description.data
        start_time = form.start_time.data
        end_time = form.end_time.data
        new_project = Project(
            name=name,
            description=description,
            start_time=start_time,
            end_time=end_time,
            its_creator = current_user._get_current_object()
        )
        new_project.its_member_users.append(current_user._get_current_object())
        db.session.add(new_project)
        db.session.commit()
        # return redirect(url_for("main.show_all_projects"))
        return redirect( url_for("main.add_user", project_id=new_project.id ) )
    return render_template("main/create_project.html", form=form)


# "我的上传"
@main.route("/my_uploads", methods=["GET", "POST"])
@login_required
@confirm_required
def my_uploads():
    files = User.query.filter_by(name=current_user.name).first().its_upload_files

    return render_template("main/my_uploads.html", files=files)


# @我的/提醒我看
@main.route("/atme")
@login_required
@confirm_required
def atme():
    return render_template("main/atme.html")


# 上传文件
@main.route("/upload/<project_id>", methods=["GET", "POST"])
@login_required
@confirm_required
def upload(project_id):
    project = Project.query.filter_by(id=project_id).first()
    if project:
        form = UploadForm()

        if form.validate_on_submit():
            file = form.file.data
            origin_filename = str(file.filename)
            secure_filename = str(uuid.uuid1())
            # file_size = len(file.read())
            description = form.description.data
            author = form.author.data
            reviewer = form.reviewer.data
            file.save(os.path.join(current_app.config['UPLOAD_PATH'], secure_filename))
            file_size = int(os.path.getsize(os.path.join(current_app.config['UPLOAD_PATH'], secure_filename)))
            file =File(
                secure_filename=secure_filename,
                origin_filename=origin_filename,
                file_size=file_size,
                description=description,
                author=author,
                reviewer=reviewer
            )

            file.its_uploader = current_user._get_current_object()
            file.its_project = project

            db.session.add(file)
            db.session.commit()

            # 自动将文件上传消息邮件通知给项目组其他成员
            to_email_list = []
            for item in project.its_member_users:
                if item.email != current_user.email:
                    to_email_list.append(item.email)
            send_upload_file_email(user=current_user, file=file, to_email_list=to_email_list, to=None)

            flash("文件上传成功", "success")
            return redirect(url_for("main.project_detail", project_id=project_id))

        return render_template("main/upload.html", form=form, project=project)
    else:
        abort(404)


# 查看项目详情页
@main.route("/detail/<project_id>")
@login_required
@confirm_required
def project_detail(project_id):
    project = Project.query.filter_by(id=project_id).first()
    download_path = current_app.config['UPLOAD_PATH'] + '/'
    return render_template("main/project_detail.html", project=project, download_path=download_path)


# 下载文件
@main.route("/download/<file_id>")
@login_required
@confirm_required
def download(file_id):
    file = File.query.filter_by(id=file_id).first()
    filename = file.secure_filename
    path = current_app.config['UPLOAD_PATH'] + "/"
    return send_from_directory(path, filename, attachment_filename=file.origin_filename ,as_attachment=True)


# 添加项目成员
@main.route("/adduser/<project_id>", methods=["GET", "POST"])
@login_required
@confirm_required
def add_user(project_id):
    project = Project.query.filter_by(id=project_id).first()
    form = ChooseMemberForm(project=project)
    if form.validate_on_submit():
        choosen_id_list = form.member.data
        to_email_list = []
        for item in choosen_id_list:
            user = User.query.filter_by(id=item).first()
            project.its_member_users.append(user)
            to_email_list.append(user.email)
        db.session.commit()

        # 给被添加的新成员发邮件通知
        send_add_new_member_email(to_email_list=to_email_list, project=project, user=current_user)

        flash("添加成员成功", "success")
        return redirect_back()

    return render_template("main/add_user.html", form=form, project=project)


# 修改项目简介
@main.route("/change-project/<project_id>", methods=["GET", "POST"])
@login_required
def change_project(project_id):
    project = Project.query.filter_by(id=project_id).first()
    form = ChangeProjectForm()

    if form.validate_on_submit():
        if form.new_name.data:
            project.name = form.new_name.data
        if form.new_description.data:
            project.description = form.new_description.data
        if form.new_start_time.data:
            project.start_time = form.new_start_time.data
        if form.new_end_time.data:
            project.end_time = form.new_end_time.data
        db.session.commit()
        flash("项目简介更新成功", "info")
        return redirect(url_for('main.show_all_projects'))

    return render_template("main/change-project.html", form=form, project=project)


# 修改文件简介
@main.route("/change-file/<file_id>", methods=["POST", "GET"])
@login_required
def change_file(file_id):
    form = ChangeFileForm()
    file = File.query.filter_by(id=file_id).first()
    if form.validate_on_submit():
        if form.new_origin_filename.data:
            file.origin_filename = form.new_origin_filename.data
        if form.new_description.data:
            file.description = form.new_description.data
        if form.new_author.data:
            file.author = form.new_author.data
        if form.new_reviewer.data:
            file.reviewer = form.new_reviewer.data
        db.session.commit()
        flash("文件信息修改成功", "success")
        return redirect(url_for('main.my_uploads'))

    return render_template("main/change-file.html", form=form, file=file)


# 删除文件
@main.route("/delete-file/<file_id>", methods=["GET", "POST"])
@fresh_login_required
def delete_file(file_id):
    file = File.query.filter_by(id=file_id).first()
    form = ConfirmDeleteForm()
    if form.validate_on_submit():
        try:
            os.remove(os.path.join(current_app.config['UPLOAD_PATH'], file.secure_filename))
            db.session.delete(file)
            db.session.commit()
            flash("指定文件已经被删除", "info")
            return redirect(url_for("main.show_all_projects"))
        except Exception as e:
            db.session.delete(file)
            db.session.commit()
            flash("文件已从数据库中被删除，但未找到文件本体，请联系网站作者", "warning")
            return redirect(url_for("main.show_all_projects"))

    return render_template("main/confirm-delete.html", form=form)


# 删除项目
@main.route("/delete-project/<project_id>", methods=["GET", "POST"])
@fresh_login_required
def delete_project(project_id):
    project = Project.query.filter_by(id=project_id).first()
    form = ConfirmDeleteForm()
    if form.validate_on_submit():
        # 删除项目下属的文件本体
        for each_file in project.its_files:
            os.remove(os.path.join(current_app.config['UPLOAD_PATH'], each_file.secure_filename))
        # 直接删除项目
        db.session.delete(project)
        db.session.commit()
        flash("指定项目及其所有文件已经被删除", "info")
        return redirect(url_for("main.show_all_projects"))

    return render_template("main/confirm-delete.html", form=form)


# 删除项目成员
@main.route("/delete-member/<project_id>/<user_id>", methods=["GET", "POST"])
@fresh_login_required
def delete_member(project_id, user_id):
    project = Project.query.filter_by(id=project_id).first()
    user = User.query.filter_by(id=user_id).first()
    form = ConfirmDeleteForm()
    if form.validate_on_submit():
        # 直接删除成员
        project.its_member_users.remove(user)
        db.session.commit()
        flash("用户已从项目组中删除", "info")
        return redirect(url_for("main.show_all_projects"))

    return render_template("main/delete-member.html", form=form)


