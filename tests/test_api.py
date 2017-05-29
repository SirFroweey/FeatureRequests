from environmentals import *
from test import test_support
from feature_requests.app import db, create_first_feature_request
from feature_requests.models import Base
import unittest
import requests

class TestCrudApi(unittest.TestCase):
    def setUp(self):
        self.base = "http://127.0.0.1:5000/"
        Base.metadata.create_all(bind=db.engine)
        create_first_feature_request()

    def test_get1(self):
        response = requests.get(self.base + "api/features/")
        model_count = len(response.json()['requests'])
        self.assertTrue(
            model_count > 0
        )

    def test_get2(self):
        response = requests.get(self.base + "api/features/1/")
        self.assertEqual(
            response.json(),
            {
                "requests": [{
                    "description": "A long description",
                    "title": "1 Sample",
                    "target_date": ["2017-05-29", "12:30:25"],
                    "client": {"code": "client-a", "value": "Client A"},
                    "client_priority": 1,
                    "id": 1,
                    "product_area": {"code": "policies", "value": "Policies"}
                }]
            }
        )

    def test_post(self):
        get_response = requests.get(self.base + "api/features/")
        last_model_id = get_response.json()['requests'][-1]['id']
        next_id = last_model_id + 1
        data = {
            "title": "{next_id} Sample".format(next_id=next_id),
            "description": "A long description",
            "target_date": "2017-05-29T12:30:25",
            "client": "client-a",
            "client_priority": 1,
            "product_area": "policies"
        }
        response = requests.post(self.base + "api/features/", data=data)
        response_json = response.json()
        self.assertEqual(
            response.json(),
            {
                "id": response_json['id'],
                "title": "{next_id} Sample".format(next_id=next_id),
                "description": "A long description",
                "target_date": ["2017-05-29", "12:30:25"],
                "client": {"code": "client-a", "value": "Client A"},
                "client_priority": 1,
                "product_area": {"code": "policies", "value": "Policies"}
            }
        )

    def test_put(self):
        get_response = requests.get(self.base + "api/features/")
        last_model = get_response.json()['requests'][-1]
        last_model["client"] = "client-a"
        last_model["product_area"] = "policies"
        last_model["target_date"] = "2017-05-29T12:30:25"
        last_model["description"] = "A long description (edit)"
        response = requests.put(
            self.base + "api/features/{model_id}/".format(model_id=last_model["id"]),
            data=last_model
        )
        self.assertEqual(
            response.json(),
            {
                "description": "A long description (edit)",
                "title": "{model_id} Sample".format(model_id=last_model["id"]),
                "target_date": ["2017-05-29", "12:30:25"],
                "client": {"code": "client-a", "value": "Client A"},
                "client_priority": 1,
                "id": last_model["id"],
                "product_area": {"code": "policies", "value": "Policies"}}
        )

    def test_delete(self):
        get_response = requests.get(self.base + "api/features/")
        last_model = get_response.json()['requests'][-1]
        response = requests.delete(
            self.base + "api/features/{model_id}/".format(model_id=last_model['id'])
        )
        self.assertEqual(
            response.json(),
            {"removed": last_model["id"]}
        )

def test_main():
    test_support.run_unittest(
        TestCrudApi
    )

if __name__ == "__main__":
    test_main()
