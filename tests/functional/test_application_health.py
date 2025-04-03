import json


def test_api_health(test_client):
    """
    GIVEN a USSD App configured for testing
    WHEN the '/app/health' endpoint is requested (GET)
    THEN check that the response
    :return:
    """
    response = test_client.get("/app/health")
    assert response.status_code == 200

    data = json.loads(response.get_data())
    assert True == data["success"]
    assert "API is up and running!" in data["data"]["message"]

    response = test_client.post("/app/health")
    assert response.status_code == 405  # method no allowed

    response = test_client.put("/app/health")
    assert response.status_code == 405  # method no allowed

    response = test_client.delete("/app/health")
    assert response.status_code == 405  # method no allowed

    response = test_client.trace("/app/health")
    assert response.status_code == 405  # method no allowed

    response = test_client.patch("/app/health")
    assert response.status_code == 405  # method no allowed
