from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField, DateField, SelectField, DecimalField
from wtforms.fields.html5 import IntegerField
from wtforms.validators import InputRequired, ValidationError
from automate.models import Feeditem, Feedtype, Formulation, Feedcost, Feedstock


class FeeditemForm(FlaskForm):
    feeditem = StringField('Feed Item',
                validators=[InputRequired(message='Field is Required')])
    quantity = IntegerField('Feed Quantity (Kg)', 
                validators=[InputRequired(message='Field is Required')])
    unitprice = IntegerField('Feed Unit Price (Naira)', 
                validators=[InputRequired(message='Field is Required')])
    submit = SubmitField('ADD FEED ITEM')

    def validate_feeditem(self, feeditem):
        feed = Feeditem.query.filter_by(item=feeditem.data).first()
        if feed:
            raise ValidationError('Feed Item already exist!')

class RenameitemForm(FlaskForm):
    oldname = StringField('Old Name',
                validators=[InputRequired(message='Field is Required')])
    newname = StringField('New Name',
                validators=[InputRequired(message='Field is Required')])
    submit = SubmitField('RENAME ITEM')

class ProductionUpdateForm(FlaskForm):
    date = DateField('Date', format='%Y-%m-%d', 
                validators=[InputRequired(message='Field is Required')])
    item = SelectField('Feeditem',
                choices=[('','Select Feed Item'), ('Maize', 'Maize'), ('Soya', 'Soya'), ('Limestone', 'Limestone'), ('Bone', 'Bone')])
    quantity = IntegerField('Quantity (Kg)',
                validators=[InputRequired(message='Field is Required')])
    submit = SubmitField('UPDATE ITEM')

class VendorForm(FlaskForm):
    date = DateField('Date', format='%Y-%m-%d', 
                validators=[InputRequired(message='Field is Required')])
    vendor = StringField('Vendor',
                validators=[InputRequired(message='Field is Required')])
    item = SelectField('Feeditem',
                choices=[('','Select Feed Item'), ('Maize', 'Maize'), ('Soya', 'Soya'), ('Limestone', 'Limestone'), ('Bone', 'Bone')])
    quantity = IntegerField('Quantity (Kg)',
                validators=[InputRequired(message='Field is Required')])
    price = FloatField('Unit Price',
                validators=[InputRequired(message='Field is Required')])
    submit = SubmitField('SUBMIT')

class FeedTypeForm(FlaskForm):
    feedtype = StringField('Feed Type',
            validators=[InputRequired(message='Field is Required')])
    quantity = FloatField('Quantity (Kg)',
            validators=[InputRequired(message='Field is Required')])
    submit = SubmitField('ADD FEED')

class OverheadCostForm(FlaskForm):
    overhead = IntegerField('Overhead Cost',
            validators=[InputRequired(message='Field is Required')])
    submit = SubmitField('UPDATE')
