import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from backend.main import app
from backend.models.cocktail import Cocktail
from backend.models.ingredient import Ingredient

client = TestClient(app)

# Mock Data
mock_cocktail = Cocktail(
    uri="http://example.org/c1",
    id="mojito",
    name="Mojito",
    ingredients="Rum, Mint",
    parsed_ingredients=["Rum", "Mint"]
)

mock_ingredient = Ingredient(
    id="http://example.org/i1",
    name="Rum",
    category="Spirit"
)

# Test Cocktails Routes
@patch("backend.routes.cocktails.cocktail_service")
def test_get_cocktails(mock_service):
    mock_service.get_all_cocktails.return_value = [mock_cocktail]
    mock_service.search_cocktails.return_value = [mock_cocktail]

    # Test list
    response = client.get("/cocktails/")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Mojito"

    # Test search
    response = client.get("/cocktails/?q=mojito")
    assert response.status_code == 200
    assert len(response.json()) == 1
    mock_service.search_cocktails.assert_called_with("mojito")

@patch("backend.routes.cocktails.cocktail_service")
def test_get_feasible_cocktails(mock_service):
    mock_service.get_feasible_cocktails.return_value = [mock_cocktail]

    response = client.get("/cocktails/feasible/user1")
    assert response.status_code == 200
    assert len(response.json()) == 1
    mock_service.get_feasible_cocktails.assert_called_with("user1")

@patch("backend.routes.cocktails.cocktail_service")
def test_get_almost_feasible_cocktails(mock_service):
    mock_service.get_almost_feasible_cocktails.return_value = [
        {"cocktail": mock_cocktail, "missing": ["Sugar"]}
    ]

    response = client.get("/cocktails/almost-feasible/user1")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["cocktail"]["name"] == "Mojito"
    assert "Sugar" in data[0]["missing"]

@patch("backend.routes.cocktails.cocktail_service")
def test_get_cocktails_by_ingredients(mock_service):
    mock_service.get_cocktails_by_ingredients.return_value = [mock_cocktail]

    response = client.get("/cocktails/by-ingredients", params={"ingredients": ["Rum", "Mint"]})
    assert response.status_code == 200
    assert len(response.json()) == 1
    mock_service.get_cocktails_by_ingredients.assert_called_with(["Rum", "Mint"])

@patch("backend.routes.cocktails.similarity_service")
def test_get_similar_cocktails(mock_service):
    mock_service.find_similar_cocktails.return_value = [{"cocktail": mock_cocktail, "similarity_score": 0.9}]

    response = client.get("/cocktails/similar/mojito")
    assert response.status_code == 200
    assert response.json()["similar_cocktails"][0]["cocktail"]["name"] == "Mojito"

# Test Ingredients Routes
@patch("backend.routes.ingredients.service")
def test_get_all_ingredients(mock_service):
    mock_service.get_all_ingredients.return_value = [mock_ingredient]
    
    response = client.get("/ingredients/")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Rum"

@patch("backend.routes.ingredients.service")
def test_search_ingredients(mock_service):
    mock_service.search_ingredients.return_value = [mock_ingredient]
    
    response = client.get("/ingredients/search?q=rum")
    assert response.status_code == 200
    assert response.json()[0]["name"] == "Rum"
    mock_service.search_ingredients.assert_called_with("rum")

@patch("backend.routes.ingredients.service")
def test_inventory_operations(mock_service):
    # Test update
    payload = {"user_id": "u1", "ingredients": ["Rum"]}
    response = client.post("/ingredients/inventory", json=payload)
    assert response.status_code == 200
    mock_service.update_inventory.assert_called_with("u1", ["Rum"])
    
    # Test get
    mock_service.get_inventory.return_value = ["Rum"]
    response = client.get("/ingredients/inventory/u1")
    assert response.status_code == 200
    assert response.json()["ingredients"] == ["Rum"]
