from leaf.ext import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

#User和Project的多对多关系中间表
user_project_table = db.Table(
    "user_project_table",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
    db.Column("project_id", db.Integer, db.ForeignKey("project.id"))
)


class User(db.Model, UserMixin):

    # 以下为数据字段：
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), nullable=False, unique=True)
    # 将以手机号作为用户身份的唯一标识！
    mobile = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(64), unique=True)
    department = db.Column(db.String(40))
    post = db.Column(db.String(40))
    signup_time = db.Column(db.DateTime, default=datetime.utcnow)
    password_hash = db.Column(db.String(128))

    # 用户的确认、封禁
    is_confirmed = db.Column(db.Boolean, default=False)
    is_blocked = db.Column(db.Boolean, default=False)
    # 默认不是系统管理员
    is_admin = db.Column(db.Boolean, default=False)

    # 以下为一对多关系属性：

    # 用户创建的项目
    its_creation = db.relationship("Project", back_populates="its_creator")
    # 用户上传的文件
    its_upload_files = db.relationship("File", back_populates="its_uploader")

    # 以下为与Project表的多对多关系属性：

    # 该用户参与的所有项目
    its_involve_projects = db.relationship(
        "Project",
        secondary=user_project_table,
        back_populates="its_member_users")

    # 存储用户密码hash的方法
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # 校验用户密码的方法
    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)


class Project(db.Model):

    # 以下为数据字段：

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    start_time = db.Column(db.String(40))
    end_time = db.Column(db.String(40))

    # 与User表关联的外键
    creator_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    # 以下为一对多关系属性：

    # 项目的创建者
    its_creator = db.relationship("User", back_populates="its_creation")

    # 项目所有的文件
    # 设置级联操作，当项目被删除则对应的文件也自动删除
    its_files = db.relationship("File", back_populates="its_project", cascade="all")

    # 以下为与User表的多对多关系属性：

    # 项目的所有成员用户
    its_member_users = db.relationship(
        "User",
        secondary=user_project_table,
        back_populates="its_involve_projects")


class File(db.Model):

    # 以下为数据字段：详情页

    id = db.Column(db.Integer, primary_key=True)
    origin_filename = db.Column(db.String(128), nullable=False)
    secure_filename = db.Column(db.String(128), nullable=False)
    # 文件大小统一用MB做单位
    file_size =  db.Column(db.String(64))
    upload_time = db.Column(db.DateTime, default=datetime.utcnow)
    description= db.Column(db.Text, nullable=False)

    # author和reviewer靠uploader上传时填写并存储姓名
    # 目前暂不支持链接User表查询作者和审核人
    # 主要是考虑到作者或审核人可能不在注册用户中
    author = db.Column(db.String(64), nullable=False)
    reviewer = db.Column(db.String(64), nullable=False)

    # 与User和Project表关联的外键
    uploader_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"))

    # 以下为一对多关系属性：

    # 文件所属的项目
    its_project = db.relationship("Project", back_populates="its_files")

    # 文件的上传者
    its_uploader = db.relationship("User", back_populates="its_upload_files")

