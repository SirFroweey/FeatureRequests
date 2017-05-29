from sqlalchemy_utils.types.choice import Choice
from sqlalchemy.orm.state import InstanceState
from datetime import datetime
from models import FeatureRequest

def dump_datetime(value):
    """Serialize datetime object into string form for JSON processing."""
    if value is None or type(value) != datetime:
        return None
    return [value.strftime("%Y-%m-%d"), value.strftime("%H:%M:%S")]

def serialize(model):
    """
    Serializes a FeatureRequest model object into JSON.
    """
    json = {}
    if type(model) == dict:
        data_type = model
    elif type(model) == FeatureRequest:
        data_type = model.__dict__
    else:
        return None
    for key, value in data_type.iteritems():
        _type = type(value)
        if _type == datetime:
            json[key] = dump_datetime(value)
        elif _type == Choice:
            json[key] = {
                "code": value.code,
                "value": value.value
            }
        elif _type == InstanceState:
            continue
        else:
            json[key] = value
    return json
