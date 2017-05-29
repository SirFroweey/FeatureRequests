from sqlalchemy_utils.types.choice import Choice
from sqlalchemy.orm.state import InstanceState
from datetime import datetime

def dump_datetime(value):
    """Serialize datetime object into string form for JSON processing."""
    if value is None:
        return None
    return [value.strftime("%Y-%m-%d"), value.strftime("%H:%M:%S")]

def serialize(model):
	"""
	Serializes a Flask SQLAlchemy model object into JSON.
	"""
	json = {}
	if type(model) == dict:
		data_type = model
	else:
		data_type = model.__dict__
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