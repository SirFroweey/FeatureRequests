from environmentals import *
from feature_requests.utils import dump_datetime, serialize
from feature_requests.app import db, create_first_feature_request
from feature_requests.models import Base, FeatureRequest
from test import test_support
from datetime import datetime
import unittest
import json

class DateTimeDumpTestCase(unittest.TestCase):
    def test_dump1(self):
        self.assertEqual(
            dump_datetime(datetime(year=2017, month=5, day=29, hour=12, minute=30, second=25)),
            ["2017-05-29", "12:30:25"]
        )

    def test_dump2(self):
        self.assertFalse(
            dump_datetime(("2017", "05", "29", "12", "30", "25"))
        )

class SerializeModelTestCase(unittest.TestCase):
    def setUp(self):
        Base.metadata.create_all(bind=db.engine)
        create_first_feature_request()
        self.model = db.session.query(FeatureRequest).first()

    def tearDown(self):
        db.session.rollback()

    def test_serialize1(self):
        self.assertEqual(
            serialize(self.model),
            {
                "description": "A long description",
                "title": "1 Sample",
                "target_date": ["2017-05-29", "12:30:25"],
                "client": {"code": "client-a", "value": "Client A"},
                "client_priority": 1,
                "id": 1,
                "product_area": {"code": "policies", "value": "Policies"}
            }
        )

    def test_serialize2(self):
        self.assertFalse(
            serialize(["a", "b", "c"])
        )

    def test_serialize3(self):
        self.assertFalse(
            serialize(None)
        )

def test_main():
    test_support.run_unittest(
        DateTimeDumpTestCase,
        SerializeModelTestCase
    )

if __name__ == "__main__":
    test_main()
