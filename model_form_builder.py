import re
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, BooleanField
from sqlalchemy import Column

def clean_field_name(name):
    name = re.sub(r'[^a-zA-Z0-9_]', '_', name.strip().replace(" ", "_").lower())
    if re.match(r'^\d', name):
        name = 'f_' + name
    return re.sub('_+', '_', name)

def is_required_field(aspect):
    return bool(aspect.get('aspectConstraint', {}).get('aspectRequired', False))

def is_ebay_yesno_aspect(aspect):
    values = aspect.get('aspectValues', [])
    if len(values) == 2:
        labels = sorted([(v.get('localizedValue') or v.get('value') or '').strip().lower() for v in values])
        return labels == ["no", "yes"]
    return False

def strip_asterisks(name):
    return name.replace('*', '').strip()

def generate_flask_model_and_form(category_id, aspects, db):
    attrs = {
        '__tablename__': f'ebay_item_{category_id}',
        '__table_args__': {'extend_existing': True},
        'id': db.Column(db.Integer, primary_key=True)
    }
    form_attrs = {}
    required_field_names = set()
    chip_fields = {}
    select_fields = {}
    datalist_fields = {}
    yesno_fields = set()

    for asp in aspects:
        name = asp.get('localizedAspectName') or asp.get('aspectName')
        is_required = is_required_field(asp)
        display_name = strip_asterisks(name)
        fname = clean_field_name(display_name)
        values = [v.get('value') or v.get('localizedValue') for v in asp.get('aspectValues', []) if v.get('value') or v.get('localizedValue')]
        constraint = asp.get('aspectConstraint', {})
        aspect_mode = constraint.get('aspectMode', '')
        aspect_cardinality = constraint.get('itemToAspectCardinality', '')
        is_free_text = aspect_mode == 'FREE_TEXT'
        is_multiselect = aspect_cardinality == 'MULTI'

        if is_ebay_yesno_aspect(asp):
            yesno_fields.add(fname)
            form_attrs[fname] = BooleanField(display_name)
            attrs[fname] = db.Column(db.String(10))
            if is_required:
                required_field_names.add(fname)
            continue

        if values:
            if is_multiselect:
                chip_fields[fname] = {'label': display_name, 'choices': values}
                attrs[fname] = db.Column(db.String(250))
                form_attrs[fname] = StringField(display_name)
            elif is_free_text:
                datalist_fields[fname] = values
                attrs[fname] = db.Column(db.String(100))
                form_attrs[fname] = StringField(display_name)
            else:
                select_fields[fname] = values
                attrs[fname] = db.Column(db.String(100))
                form_attrs[fname] = SelectField(display_name, choices=[(v, v) for v in values if v])
        else:
            form_attrs[fname] = StringField(display_name)
            attrs[fname] = db.Column(db.String(100))

        if is_required:
            required_field_names.add(fname)

    form_attrs['submit'] = SubmitField('Submit')
    Model = type(f'EbayItem_{category_id}', (db.Model,), attrs)
    Form = type(f'EbayItemForm_{category_id}', (FlaskForm,), form_attrs)

    return (
        Model,
        Form,
        required_field_names,
        chip_fields,
        {},  # single_value_fields not used
        select_fields,
        datalist_fields,
        {},  # initial_values not used
        {},  # forced_default_chip not used
        yesno_fields,
    )
