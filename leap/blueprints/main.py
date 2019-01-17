from flask import Blueprint, render_template, url_for, redirect
from leap.forms import ProjectForm

main = Blueprint(__name__, "main")


@main.route("/", methods=["GET", "POST"])
def index():
    return render_template("main/index.html")


@main.route("/create", methods=["GET", "POST"])
def create_project():
    form = ProjectForm()
    return render_template("main/create_project.html", form=form)



