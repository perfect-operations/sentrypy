import requests

from sentrypy.transceiver import Transceiver


def test_get_request_call(mocker):
    """Verify that ``requests.get`` is called with the right arguments"""
    token = "the_token"
    endpoint = "the_endpoint"
    params = {"param": "value"}
    expected_header = {"Authorization": f"Bearer {token}"}

    mocker.patch("requests.get")
    handler = Transceiver(token=token)
    handler.get(endpoint, params=params)
    requests.get.assert_called_with(url=endpoint, headers=expected_header, params=params)
