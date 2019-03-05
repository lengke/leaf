from flask import Blueprint, render_template, url_for, redirect, abort, flash, request, current_app, send_from_directory
from leaf.forms import ProjectForm, UploadForm, ChooseMemberForm
from leaf.ext import db
from leaf.models import Project, File, User
from flask_login import login_required, current_user
from leaf.decorators import confirm_required
from leaf.utils import redirect_back
import os, uuid

main = Blueprint("main", __name__)


# 网站首页
@main.route("/", methods=["GET", "POST"])
def index():
    # db.drop_all()
    # db.create_all()

    projects_sum = Project.query.count()
    files_sum = File.query.count()
    users_sum = User.query.count()

    return render_template("main/index.html",
                           files_sum=files_sum,
                           projects_sum=projects_sum,
                           users_sum=users_sum
                           )


# 显示所有项目列表
@main.route("/allprojects", methods=["GET", "POST"])
@login_required
@confirm_required
def show_all_projects():
    projects = Project.query.all()
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
        return redirect(url_for("main.show_all_projects"))
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

            flash("文件上传成功", "success")
            return redirect(url_for("main.show_all_projects"))

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
    form = ChooseMemberForm()
    if form.validate_on_submit():

        choosen_id_list = form.member.data
        for item in choosen_id_list:
            user = User.query.filter_by(id = item).first()
            project.its_member_users.append(user)
        db.session.commit()
        flash("添加成员成功", "success")
        return redirect_back()

    return render_template("main/add_user.html", form=form, project=project)
