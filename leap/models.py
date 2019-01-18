from leap.ext import db
from datetime import datetime


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), unique=True, nullable=False)
    status = db.Column(db.String(10))
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    # owner_id = db.Column(db.Integer, foreign_key="user.id")

    # its_owner
    # its_files
    # its_tasks


# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(40), unique=True, nullable=False) # 名字
#     is_admin = db.Column(db.Boolean, default=False) #默认不是系统管理员
#     dept = db.Column(db.String(40)) # 部门
#     post = db.Column(db.String(40)) # 职位
#
#     # its_projects = db.Relationship(back_populates="")
#     # its_tasks
#     # its_users
#     # its_files
#
#
# class Task(db.Model):
#     pass
#
#
# class File(db.Model):
#     pass
#
#


