import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from uuid import uuid4
from sqlalchemy.exc import IntegrityError

# Import your router and other necessary components
from your_module import router  # Update with your actual module name

# Create a FastAPI instance and include the router
app = FastAPI()
app.include_router(router)

# Set up a test client
client = TestClient(app)

# Mocking the database access layer
def mock_get_address_with_id(address_id):
    if address_id == valid_address_id:
        return {
            "address_id": valid_address_id,
            "location_name": "Home",
            "address_line_1": "123 Main St",
            "address_line_2": None,
            "city": "Anytown",
            "state": "CA",
            "postal_code": "12345",
        }
    else:
        raise HTTPException(status_code=404)

# Replace the actual `get_address_with_id` with the mock
router.dependency_overrides[get_address_with_id] = mock_get_address_with_id

# Test data
valid_address_id = uuid4()
invalid_address_id = uuid4()

def test_get_address_success():
    response = client.get(f"/address/{valid_address_id}")
    assert response.status_code == 200
    assert response.json() == {
        "address_id": str(valid_address_id),
        "location_name": "Home",
        "address_line_1": "123 Main St",
        "address_line_2": None,
        "city": "Anytown",
        "state": "CA",
        "postal_code": "12345",
    }

def test_get_address_not_found():
    response = client.get(f"/address/{invalid_address_id}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}

# Optionally add more tests for other routes and methods
