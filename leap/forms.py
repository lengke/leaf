from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired


class ProjectForm(FlaskForm):
    name = StringField("项目名称：", validators=[DataRequired()])
    status = SelectField("项目状态：", validators=[DataRequired()], choices=[("ongoing", "进行中"), ("todo", "尚未开始"), ("over", "已结束")])
    submit = SubmitField("提交")





