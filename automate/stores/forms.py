from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField, DateField, SelectField, DecimalField
from wtforms.fields.html5 import IntegerField

# Store Form
class storeForm(FlaskForm):
    submit = SubmitField('Submit')

# Egg-Store Form
class eggstoreForm(FlaskForm):
    submit = SubmitField('submit')