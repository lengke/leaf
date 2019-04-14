from flask import Flask, render_template
from leaf.settings import config_list
from leaf.blueprints.main import main
from leaf.blueprints.auth import auth
from leaf.blueprints.admin import admin
from leaf.ext import db, login_manager, mail, bootstrap, moment
from leaf.utils import handle_file_size
from leaf.models import User
import click


def create_app(config_name=None):
    if config_name is None:
        current_config = config_list["development"]
    else:
        current_config = config_list[config_name]

    app = Flask("leaf")
    app.config.from_object(current_config)
    register_exts(app)
    register_blueprints(app)
    register_commands(app)
    register_errorhandlers(app)
    return app


def register_blueprints(app):
    app.register_blueprint(main)
    app.register_blueprint(auth, url_prefix="/auth")
    app.register_blueprint(admin, url_prefix="/admin")


def register_exts(app):
    db.init_app(app)
    login_manager.init_app(app)
    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    app.add_template_filter(handle_file_size, 'size')


# 自定义错误页面
def register_errorhandlers(app):
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404


# 自定义操作命令
def register_commands(app):

    # 初始化数据库并生成1个默认的admin账号
    # 注意：运行该命令会清空数据库
    # 注意：请仅在第一次部署时运行该命令
    @app.cli.command()
    def init():
        click.echo("清空数据库...")
        db.drop_all()
        click.echo("完成!")
        click.echo("重新生成数据库...")
        db.create_all()
        click.echo("完成！")

        click.echo("正在生成默认的管理员账号")
        default_admin = User(
            name="默认系统管理员",
            department="系统管理员",
            post="系统管理员",
            email="default_admin@leaf.com",
            mobile="88888888888"
        )
        default_admin.set_password("123456")
        default_admin.is_confirmed = True
        default_admin.is_admin = True
        db.session.add(default_admin)
        db.session.commit()
        click.echo("已完成全部初始化设置，祝您使用愉快！")
        click.echo("请登录后立即修改邮箱、手机号和登录密码等信息")

    # 创建管理员账号的命令
    @app.cli.command()
    @click.option("--name", prompt="输入管理员姓名", help="请输入管理员账号的姓名")
    @click.option("--mobile", prompt="输入管理员手机号", help="请输入管理员账号的手机号")
    @click.option("--email", prompt="输入管理员邮箱地址", help="请输入管理员账号的邮箱地址")
    @click.option("--password", prompt="输入管理员登录密码", help="请为管理员账号设置密码",
                  confirmation_prompt="请再次输入登录密码")
    def setadmin(name, mobile, email, password):

        new_admin = User(
            name=name,
            department="系统管理员",
            post="系统管理员",
            email=email.lower(),
            mobile=mobile
        )
        new_admin.set_password(password)
        new_admin.is_confirmed = True
        new_admin.is_admin = True
        db.session.add(new_admin)
        db.session.commit()

        click.echo(f"管理员账号 {name} 设置完成")
        click.echo("若需要修改账号信息，请登陆后在个人资料页面修改")

    # 封禁管理员账号的命令
    # 警告：删除用户账号可能引发一系列潜在bug
    # 不到万不得已，不建议使用本命令，请用blockadmin来替代
    @app.cli.command()
    @click.option("--mobile", prompt="输入要封禁的管理员手机号", confirmation_prompt="请再次确认手机号", help="请输入手机号")
    def blockadmin(mobile):

        admin_to_block = User.query.filter_by(mobile=mobile).first()

        if admin:
            name = admin_to_block.name
            admin_to_block.is_blocked = True
            db.session.commit()
            click.echo(f"管理员账号 {name} 封禁成功")
        else:
            click.echo("未找到该账号，请确认手机号输入正确")
            pass

    # 删除管理员/普通用户账号的命令
    # 警告：删除用户账号可能引发一系列潜在bug
    # 不到万不得已，不建议使用本命令，请用blockadmin来替代
    @app.cli.command()
    @click.option("--mobile", prompt="输入要删除用户的手机号", confirmation_prompt="请再次确认手机号", help="请输入要删除的手机号")
    def dropadmin(mobile):

        user_to_delete = User.query.filter_by(mobile=mobile).first()

        if admin:
            name = user_to_delete.name
            db.session.delete(user_to_delete)
            db.session.commit()
            click.echo(f"账号 {name} 删除成功")
        else:
            click.echo("未找到该账号，请确认手机号输入正确")
            pass



