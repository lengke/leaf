from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, RadioField
from wtforms.validators import DataRequired, Length


class ProjectForm(FlaskForm):
    name = StringField("项目名称：", validators=[DataRequired()])
    # status = RadioField("项目状态：")
    submit = SubmitField("提交")





