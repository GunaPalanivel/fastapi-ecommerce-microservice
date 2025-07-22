"""
Test suite for product endpoints.
"""

import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient

from main import app


@pytest.mark.asyncio
class TestProducts:
    """Test cases for product endpoints."""
    
    async def test_create_product_success(self):
        """Test successful product creation."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            product_data = {
                "name": "Test Product",
                "price": 99.99,
                "size": ["small", "medium", "large"],
                "available_quantity": 100
            }
            
            response = await client.post("/products", json=product_data)
            
            assert response.status_code == 201
            data = response.json()
            assert data["name"] == product_data["name"]
            assert data["price"] == product_data["price"]
            assert "id" in data
    
    async def test_create_product_invalid_data(self):
        """Test product creation with invalid data."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            invalid_data = {
                "name": "",  # Empty name
                "price": -10,  # Negative price
                "size": [],  # Empty size array
                "available_quantity": -5  # Negative quantity
            }
            
            response = await client.post("/products", json=invalid_data)
            assert response.status_code == 400
    
    async def test_list_products_success(self):
        """Test successful product listing."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/products")
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
    
    async def test_list_products_with_filters(self):
        """Test product listing with filters."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Test name filter
            response = await client.get("/products?name=test")
            assert response.status_code == 200
            
            # Test size filter
            response = await client.get("/products?size=large")
            assert response.status_code == 200
            
            # Test pagination
            response = await client.get("/products?limit=5&offset=10")
            assert response.status_code == 200
    
    async def test_list_products_pagination_limits(self):
        """Test pagination parameter limits."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Test limit too high
            response = await client.get("/products?limit=1000")
            assert response.status_code == 422
            
            # Test negative offset
            response = await client.get("/products?offset=-1")
            assert response.status_code == 422
