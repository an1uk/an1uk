# forms.py 
from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional, Length, NumberRange

class ItemForm(FlaskForm):
    sku = StringField('SKU', validators=[Optional(), Length(max=64)])
    title = StringField('Title', validators=[DataRequired(), Length(max=255)])
    description = TextAreaField('Description', validators=[Optional()])
    price = DecimalField('Price', validators=[DataRequired(), NumberRange(min=0)], places=2)
    local_category = StringField('Local Category', validators=[Optional(), Length(max=128)])
    ebay_category_id = StringField('eBay Category ID', validators=[Optional(), Length(max=16)])
    ebay_status = StringField('eBay Status', validators=[Optional(), Length(max=64)])
    image_url = StringField('Image URL', validators=[Optional(), Length(max=255)])
    aspect_values = TextAreaField('Aspect Values (JSON)', validators=[Optional()])
    submit = SubmitField('Add Item')
