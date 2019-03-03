from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, PasswordField, BooleanField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.validators import DataRequired, EqualTo, Length, Email, ValidationError
from leap.models import User


# 创建项目的表单
class ProjectForm(FlaskForm):
    name = StringField("项目名称：", validators=[DataRequired()])
    description = TextAreaField("项目描述：", validators=[DataRequired()])
    start_time = StringField("项目开始时间：", validators=[DataRequired()])
    end_time = StringField("项目结束时间：", validators=[DataRequired()])
    submit = SubmitField("提交")


# 新用户注册的表单
class RegisterForm(FlaskForm):
    name = StringField("真实姓名", validators=[DataRequired(), Length(1,30)])
    # 将以手机号作为用户身份的唯一标识！
    mobile = StringField("手机号", validators=[DataRequired(), Length(1,15)])
    email = StringField("公司邮箱", validators=[DataRequired(), Email(), Length(1,254)])
    department = StringField("所属部门", validators=[DataRequired()])
    post = StringField("职位名称", validators=[DataRequired()])
    password = PasswordField("输入密码", validators=[DataRequired(), Length(6,128), EqualTo('password2')])
    password2 = PasswordField("确认密码", validators=[DataRequired()])
    submit = SubmitField("注册")

    # 防止email重复
    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('该邮箱地址已被注册')

    # 防止手机号重复
    def validate_mobile(self, field):
        if User.query.filter_by(mobile=field.data).first():
            raise ValidationError('该手机号已被注册')


# 用户登录的表单
class LoginForm(FlaskForm):
    mobile = StringField("手机号", validators=[DataRequired()])
    password = PasswordField("密码", validators=[DataRequired()])
    remember = BooleanField("记住我", default=True)
    submit = SubmitField("登录")

    def validate_mobile(self, field):
        if not User.query.filter_by(mobile=field.data).first():
            raise ValidationError("手机号未注册")


# 忘记密码的表单
class ForgetPasswordForm(FlaskForm):
    mobile = StringField("手机号", validators=[DataRequired()])
    submit = SubmitField("忘记密码")

    def validate_mobile(self, field):
        if not User.query.filter_by(mobile=field.data).first():
            raise ValidationError("该手机号未注册")


# 重置密码的表单
class ResetPasswordForm(FlaskForm):
    mobile = StringField("手机号", validators=[DataRequired()])
    password = PasswordField("新密码", validators=[DataRequired(), Length(6,128)])
    password2 = PasswordField("确认新密码", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("重置密码")

    def validate_mobile(self, field):
        if not User.query.filter_by(mobile=field.data).first():
            raise ValidationError("该手机号未注册")

# 上传文件的表单
class UploadForm(FlaskForm):
    file = FileField(
        "上传文件：",
        validators=[FileRequired(message='未选择文件')]
    )
    description = TextAreaField("文件简介：", validators=[DataRequired()])
    author = StringField("文件作者：", validators=[DataRequired()])
    reviewer = StringField("文件审核人：", validators=[DataRequired()])
    submit = SubmitField('上传')



