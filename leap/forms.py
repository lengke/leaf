from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, PasswordField, IntegerField
from wtforms.validators import DataRequired, EqualTo


# 创建项目的表单
class ProjectForm(FlaskForm):
    name = StringField("项目名称：", validators=[DataRequired()])
    description = TextAreaField("项目描述：", validators=[DataRequired()])
    start_time = StringField("项目开始时间：", validators=[DataRequired()])
    end_time = StringField("项目结束时间：", validators=[DataRequired()])
    submit = SubmitField("提交")


# 新用户注册的表单
class RegisterForm(FlaskForm):
    name = StringField("真实姓名", validators=[DataRequired()])
    mobile = IntegerField("手机号", validators=[DataRequired()])
    email = StringField("公司邮箱", validators=[DataRequired()])
    department = StringField("所属部门", validators=[DataRequired()])
    post = StringField("职位名称", validators=[DataRequired()])
    password = PasswordField("输入密码", validators=[DataRequired()])
    password2 = PasswordField("确认密码", validators=[DataRequired(), EqualTo(password)])
    submit = SubmitField("提交")
    

# 用户登录的表单
class LoginForm(FlaskForm):
    email = StringField("输入公司邮箱", validators=[DataRequired()])
    password = PasswordField("输入密码", validators=[DataRequired()])
    submit = SubmitField("提交")





