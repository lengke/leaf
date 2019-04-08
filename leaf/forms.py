from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, PasswordField, BooleanField, SelectMultipleField, DateField
from flask_wtf.file import FileField, FileRequired
from wtforms.validators import DataRequired, EqualTo, Length, Email, ValidationError
from leaf.models import User, Project, File
from flask_login import current_user


# 创建项目的表单
class ProjectForm(FlaskForm):
    name = StringField("项目名称：", validators=[DataRequired(message="这项不能为空")])
    description = TextAreaField("一句话项目概述：", validators=[DataRequired(message="不能为空")])
    start_time = DateField("项目开始日期：", format='%Y-%m-%d', validators=[DataRequired(message="请注意格式要求且不能为空")])
    end_time = DateField("项目结束日期：", format='%Y-%m-%d', validators=[DataRequired(message="请注意格式要求且不能为空")])
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


# 忘记密码后重置密码的表单
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


# 选择为项目添加组员的表单
class ChooseMemberForm(FlaskForm):
    def __init__(self, project, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 查询用户名单并将自己和已是成员的人排除在外
        self.member.choices = []
        for user in User.query.all():
            if user.id != current_user.id and user not in project.its_member_users:
                self.member.choices.append((user.id, user.name))
            else:
                continue
        if len(self.member.choices) == 0:
            self.member.choices = [(-1, "没有可添加的用户"), ]
            self.submit.render_kw = {"class": "hideme"}

    member = SelectMultipleField("选择用户", coerce=int, validators=[DataRequired()])
    submit = SubmitField("提交")


# 登录状态下修改密码的表单
class ChangePasswordForm(FlaskForm):
    old_password = PasswordField("输入旧密码", validators=[DataRequired()])
    new_password = PasswordField("输入新密码", validators=[DataRequired(), Length(6,128), EqualTo('new_password2')])
    new_password2 = PasswordField("确认新密码", validators=[DataRequired()])
    submit = SubmitField("提交")


# 登录状态下修改邮箱的表单
class ChangeEmailForm(FlaskForm):
    new_email = StringField("新邮箱", validators=[DataRequired(), Email(message="请输入正确的email格式"), Length(1,254)])
    submit = SubmitField("提交")
    def validate_new_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('该邮箱地址已被注册')


# 修改其他个人信息的表单
class ChangeInfoForm(FlaskForm):
    new_name = StringField("修改真实姓名", validators=[Length(0,30)])
    new_mobile = StringField("修改手机号", validators=[Length(0,15)])
    new_department = StringField("修改所属部门", validators=[Length(0,15)])
    new_post = StringField("修改职位名称", validators=[Length(0,15)])
    submit = SubmitField("提交")

    # 防止姓名name重复
    def validate_new_name(self, field):
        if User.query.filter_by(name=field.data).first():
            raise ValidationError('该用户名字已被注册')

    # 防止手机号重复
    def validate_new_mobile(self, field):
        if User.query.filter_by(mobile=field.data).first():
            raise ValidationError('该手机号已被注册')


# 修改项目简介及起止时间的表格
class ChangeProjectForm(FlaskForm):

    # def __init__(self, project, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.new_start_time.default = project.start_time
    #     self.new_end_time.default = project.end_time

    new_name = StringField("项目名称：")
    new_description = TextAreaField("项目描述：")

    # TODO: 新建项目的时候用的DateField，这里用StringField，会有隐患吗？
    # 管他妈的，能用就行
    new_start_time = StringField("项目开始日期：")
    new_end_time = StringField("项目结束日期：")
    submit = SubmitField("提交")

    # 防止项目名称重复
    def validate_new_name(self, field):
        if Project.query.filter_by(name=field.data).first():
            raise ValidationError('项目名称不能与其他项目重复')

# 修改文件信息的表单
class ChangeFileForm(FlaskForm):
    new_origin_filename = StringField("文件名：")
    new_description = TextAreaField("文件简介：")
    new_author = StringField("文件作者：")
    new_reviewer = StringField("文件审核人：")
    submit = SubmitField('上传')

    # 防止文件名重复
    def validate_new_origin_filename(self, field):
        if File.query.filter_by(origin_filename=field.data).first():
            raise ValidationError('文件名不能与其他文件重复')

# 确认文件和项目删除操作的密码验证表
class ConfirmDeleteForm(FlaskForm):
    password = PasswordField("输入登录密码：", validators=[DataRequired(message="密码不能为空")])
    submit = SubmitField("确认删除")

    def validate_password(self, field):
        if not current_user.validate_password(field.data):
            raise ValidationError('密码错误')
