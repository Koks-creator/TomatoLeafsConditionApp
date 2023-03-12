from flask_wtf import FlaskForm
from wtforms import SubmitField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileAllowed


class MainForm(FlaskForm):
    image = FileField("Upload file", validators=[DataRequired(), FileAllowed(["jpg", "png", "jpeg"])])
    submit = SubmitField("Submit")
