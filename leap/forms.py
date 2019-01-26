from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired


# 创建项目的表单
class ProjectForm(FlaskForm):
    name = StringField("项目名称：", validators=[DataRequired()])
    description = TextAreaField("项目描述：", validators=[DataRequired()])
    start_time = StringField("项目开始时间：", validators=[DataRequired()])
    end_time = StringField("项目结束时间：", validators=[DataRequired()])
    submit = SubmitField("提交")



