from flask import Blueprint, render_template, url_for, redirect
from leap.forms import ProjectForm
from leap.ext import db
from leap.models import Project


main = Blueprint(__name__, "main")


@main.route("/", methods=["GET", "POST"])
def index():
    # db.drop_all()
    # db.create_all()
    return render_template("main/index.html")


@main.route("/allprojects", methods=["GET", "POST"])
def all_projects():
    projects = Project.query.all()

    return render_template("main/all_projects.html", projects=projects)


@main.route("/create", methods=["GET", "POST"])
def create_project():
    form = ProjectForm()
    if form.validate_on_submit():
        name = form.name.data
        status = form.status.data
        new_project = Project(name=name, status=status)
        db.session.add(new_project)
        db.session.commit()
        return redirect(url_for(".all_projects"))
    return render_template("main/create_project.html", form=form)



