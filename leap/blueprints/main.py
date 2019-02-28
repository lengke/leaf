from flask import Blueprint, render_template, url_for, redirect
from leap.forms import ProjectForm
from leap.ext import db
from leap.models import Project
from flask_login import login_required
from leap.decorators import confirm_required

main = Blueprint("main", __name__)


# 网站首页
@main.route("/", methods=["GET", "POST"])
def index():
    # db.drop_all()
    # db.create_all()
    return render_template("main/index.html")


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
            end_time=end_time
        )
        db.session.add(new_project)
        db.session.commit()
        return redirect(url_for("main.show_all_projects"))
    return render_template("main/create_project.html", form=form)



