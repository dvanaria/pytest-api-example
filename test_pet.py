from jsonschema import validate
import pytest
import schemas
import api_helpers
from hamcrest import assert_that, contains_string, is_

def test_pet_schema():
    test_endpoint = "/pets/1"

    response = api_helpers.get_api_data(test_endpoint)

    assert response.status_code == 200

    # Validate the response schema against the defined schema in schemas.py
    validate(instance=response.json(), schema=schemas.pet)


@pytest.mark.parametrize("status", ["available", "sold", "pending"])
def test_find_by_status_200(status):

    test_endpoint = "/pets/findByStatus"

    params = {
        "status": status
    }

    response = api_helpers.get_api_data(test_endpoint, params)
    
    # parameterization includes all available statuses
    # validate the correct response code
    assert response.status_code == 200
    
    response_data = response.json()
    
    # validate the 'status' property in the response is equal to expected status
    if response_data: 
        for pet_data in response_data:
            assert pet_data["status"] == status
    
    # validate the schema for each object in the response
    for pet_data in response_data:
        
        try:
            validate(instance=pet_data, schema=schemas.pet)
        except jsonschema.exceptions.ValidationError as e:
            pytest.fail(f"Schema validation failed for pet data: {pet_data}. Error: {e.message}")


@pytest.mark.parametrize("pet_id, expected_status, description", [
    (-1, 404, "negative integer ID"),
    (999, 404, "non-existent positive ID"),
    (100, 404, "another non-existent ID"),
    ("abc", 404, "string ID"),
    ("1.5", 404, "decimal string ID"),
    ("-1", 404, "negative string ID"),
    (None, 404, "null ID"),
])
def test_get_by_id_404(pet_id, expected_status, description):

    test_endpoint = f"/pets/{pet_id}"
    
    response = api_helpers.get_api_data(test_endpoint)
    
    assert response.status_code == expected_status, \
        f"Expected {expected_status} for {description} (ID: {pet_id}), got {response.status_code}"
    