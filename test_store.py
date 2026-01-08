from jsonschema import validate
import pytest
import schemas
import api_helpers
from hamcrest import assert_that, contains_string, is_

def test_patch_order_by_id():

    '''Test PATCH /store/order/{order_id}'''
    
    # create an order to update
    order_data = {"pet_id": 2}
    create_response = api_helpers.post_api_data("/store/order", order_data)
    assert create_response.status_code == 201
    
    order = create_response.json()
    order_id = order["id"]
    
    # test PATCH with valid status update
    test_endpoint = f"/store/order/{order_id}"
    update_data = {"status": "sold"}
    
    response = api_helpers.patch_api_data(test_endpoint, update_data)
    
    # validate response code
    assert response.status_code == 200
    
    # validate response message
    response_data = response.json()
    assert "message" in response_data
    assert response_data["message"] == "Order and pet status updated successfully"
    
    # verify pet status was updated
    pet_response = api_helpers.get_api_data(f"/pets/{order['pet_id']}")
    pet_data = pet_response.json()
    assert pet_data["status"] == "sold"


@pytest.fixture
def setup_order():

    """Fixture to create an order for testing and return order data"""

    # get available pet
    pets_response = api_helpers.get_api_data('/pets/')
    pets = pets_response.json()
    
    # Find an available pet
    available_pet = None
    for pet in pets:
        if pet['status'] == 'available':
            available_pet = pet
            break
    
    if not available_pet:
        pytest.skip("No available pets found for testing")
    
    # create order
    order_data = {"pet_id": available_pet['id']}
    order_response = api_helpers.post_api_data('/store/order', order_data)
    
    assert order_response.status_code == 201
    
    return order_response.json()

def test_patch_order_with_fixture(setup_order):
    """Test using pytest fixture"""
    order = setup_order
    order_id = order["id"]
    
    # test multiple status updates
    statuses_to_test = ["pending", "sold", "available"]
    
    for status in statuses_to_test:
        response = api_helpers.patch_api_data(
            f"/store/order/{order_id}",
            {"status": status}
        )
        
        assert response.status_code == 200
        assert response.json()["message"] == "Order and pet status updated successfully"