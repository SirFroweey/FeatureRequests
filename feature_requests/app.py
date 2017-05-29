from flask import Flask, abort, make_response, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api, reqparse
from flask.views import View
from models import Base, FeatureRequest
from sqlalchemy import exc
from utils import serialize
from datetime import datetime
import os

DB_LOCATION = os.path.join(os.path.dirname(os.path.normpath(__file__)), "feature_requests.db")
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{location}'.format(location=DB_LOCATION)
db = SQLAlchemy(app)
api = Api(app)

def create_first_feature_request():
    """
    Creates a sample feature request for showcase.
    """
    if not db.session.query(FeatureRequest).count():
        db.session.add(
            FeatureRequest(
                '1 Sample',
                'A long description',
                'client-a',
                1,
                datetime(year=2017, month=5, day=29, hour=12, minute=30, second=25),
                'policies'
            )
        )
        db.session.commit()

@app.before_first_request
def setup():
    Base.metadata.create_all(bind=db.engine)
    create_first_feature_request()

class CRUD(Resource):
    """
    Provides a CRUD RESTful interface for Feature Requests.
    @param fr_id (integer): existing feature request model id
    """
    def _safe_exit_and_error(self, message):
        """
        Safely rollback a database commit attempt and return
        a friendly error message detailing the error involved.
        """
        db.session().rollback()
        if type(message) != str:
            message = str(message)
        return {"error": message}, 400

    def _valid_arguments(self, args):
        """
        Return True if all expected arguments have been supplied,
        otherwise, return False.
        """
        for argument, argument_value in args.iteritems():
            if not argument_value:
                return False
        return True

    def _valid_choice_field(self, supplied_key, options):
        """
        Ensure that the supplied_key exists within' the options list; defined in models.py.
        """
        keys = [entry[0] for entry in options]
        if supplied_key not in keys:
            return False
        return True

    def get(self, fr_id=None):
        if fr_id:
            model = db.session.query(FeatureRequest).filter_by(id=fr_id).first()
            requests = [serialize(model)] if model else []
        else:
            requests = [
                serialize(entry)
                for entry in db.session.query(FeatureRequest).all()
            ]
        return {"requests": requests}

    def put(self, fr_id=None):
        if not fr_id:
            return abort(400)
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, help='Unique ID of Feature Request record')
        parser.add_argument('title', type=str, help='Title for this feature, must be unique')
        parser.add_argument('description', type=str, help='Description for this feature')
        parser.add_argument('client', type=str, help="Client to appoint for this feature, choices defined in models.py")
        parser.add_argument('client_priority', type=int, help="Priority number for this feature (1 being the lowest)")
        parser.add_argument('target_date', type=lambda x: datetime.strptime(x,'%Y-%m-%dT%H:%M:%S'), help="Target date for completion in the format of Y-m-dTH:M:S; i.e.: 2016-07-12T23:13:3")
        parser.add_argument('product_area', type=str, help="Area for target feature, choices defined in models.py")
        args = parser.parse_args(strict=True)
        if not self._valid_choice_field(args['client'], FeatureRequest.CLIENTS):
            return serialize(args), 400
        if not self._valid_choice_field(args['product_area'], FeatureRequest.PRODUCT_AREAS):
            return serialize(args), 400
        models = db.session.query(FeatureRequest).filter(FeatureRequest.id==args['id'])
        if models.count():
            try:
                models.update(dict(
                    title=args['title'],
                    description=args['description'],
                    client=args['client'],
                    client_priority=args['client_priority'],
                    target_date=args['target_date'],
                    product_area=args['product_area']
                ))
                db.session.commit()
            except exc.IntegrityError as e:
                return self._safe_exit_and_error(e)
        else:
            return self._safe_exit_and_error("Invalid id: {pk}.".format(
                pk=fr_id
            ))
        return serialize(
            db.session.query(FeatureRequest).filter_by(id=fr_id).first())


    def post(self, fr_id=None):
        parser = reqparse.RequestParser()
        parser.add_argument('title', type=str, help='Title for this feature, must be unique')
        parser.add_argument('description', type=str, help='Description for this feature')
        parser.add_argument('client', type=str, help="Client to appoint for this feature, choices defined in models.py")
        parser.add_argument('client_priority', type=int, help="Priority number for this feature (1 being the lowest)")
        parser.add_argument('target_date', type=lambda x: datetime.strptime(x,'%Y-%m-%dT%H:%M:%S'), help="Target date for completion in the format of Y-m-dTH:M:S; i.e.: 2016-07-12T23:13:3")
        parser.add_argument('product_area', type=str, help="Area for target feature, choices defined in models.py")
        args = parser.parse_args(strict=True)
        if not self._valid_arguments(args):
            return serialize(args), 400
        if not self._valid_choice_field(args['client'], FeatureRequest.CLIENTS):
            return serialize(args), 400
        if not self._valid_choice_field(args['product_area'], FeatureRequest.PRODUCT_AREAS):
            return serialize(args), 400
        new_feature_request = FeatureRequest(
            title=args['title'],
            description=args['description'],
            client=args['client'],
            client_priority=args['client_priority'],
            target_date=args['target_date'],
            product_area=args['product_area']
        )
        try:
            db.session.add(new_feature_request)
            db.session.commit()
        except exc.IntegrityError as e:
            return self._safe_exit_and_error(e)
        return serialize(
            db.session.query(FeatureRequest).filter_by(title=args['title']).first())

    def delete(self, fr_id=None):
        if not fr_id:
            return abort(400)
        model = db.session.query(FeatureRequest).filter(FeatureRequest.id==fr_id)
        if not model.count():
            return self._safe_exit_and_error("Invalid model id.")
        model.delete()
        db.session.commit()
        return {"removed": fr_id}

class TemplateView(View):
    """
    Pluggable template class-based view.
    """
    def get_template_name(self):
        raise NotImplementedError()

    def render_template(self, context):
        return render_template(self.get_template_name(), **context)

    def dispatch_request(self):
        return self.render_template({})

class ShowFeaturesView(TemplateView):
    def get_template_name(self):
        return 'show_features.html'

api.add_resource(CRUD, '/api/features/', '/api/features/<int:fr_id>/')
app.add_url_rule('/', view_func=ShowFeaturesView.as_view('show_features'))

if __name__ == '__main__':
    app.run('127.0.0.1', 5000, debug=True)
