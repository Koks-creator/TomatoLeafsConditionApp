import pytest
from TomatoLeafs.webapp import app


class TestApp:
    images = "images"
    expected_results = {
        "mixed3.png": {
            "StatusCode": 200,
            "Status": "Mostly Healthy",
            "Res": "Results (7)",
        },

        "blight_1.jpg": {
            "StatusCode": 200,
            "Status": "Very Diseased!",
            "Res": "Results (4)",
        },

        "img.txt": {
            "StatusCode": 400,
            "Status": "File should be png or jpg",
            "Res": "File should be png or jpg",
        },
    }

    main_page = "/"
    test_detections_page = "/test/detections"

    @pytest.fixture()
    def app_client(self):
        app.config.update({
            "TESTING": True,
        })

        yield app

    def test_index_route(self, app_client):
        response = app_client.test_client().get(self.main_page)

        assert response.status_code == 200

    def test_detections(self, app_client):
        for image in list(self.expected_results.keys()):
            files = {"image": open(rf"{self.images}/{image}", "rb")}

            response = app_client.test_client().post(self.test_detections_page, data=files)

            assert response.status_code == self.expected_results[image]["StatusCode"]
            assert response.json["Status"] == self.expected_results[image]["Status"]

    def test_upload(self, app_client):
        for image in list(self.expected_results.keys()):
            files = {"image": open(rf"{self.images}/{image}", "rb")}

            response = app_client.test_client().post(self.main_page, data=files,
                                                     content_type="multipart/form-data",
                                                     follow_redirects=True)

            assert response.status_code == self.expected_results[image]["StatusCode"]
            assert self.expected_results[image]["Res"] in response.data.decode('utf-8')
