from marshmallow import Schema, ValidationError, fields, validate
from sqlalchemy.exc import IntegrityError
from app import app
from helpers import error, get_json, login_required
from models import Category
from config import db 

class CategorySchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=50))

