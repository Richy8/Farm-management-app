from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField, DateField, SelectField, DecimalField
from wtforms.fields.html5 import IntegerField

# Store Form
class salesForm(FlaskForm):
    submit = SubmitField('Submit')
