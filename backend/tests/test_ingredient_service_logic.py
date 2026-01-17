
import pytest
from unittest.mock import MagicMock, patch
from backend.services.ingredient_service import IngredientService
from backend.models.ingredient import Ingredient

@pytest.fixture
def ingredient_service():
    with patch("backend.services.ingredient_service.SparqlService"), \
         patch("backend.services.ingredient_service.get_shared_graph"), \
         patch("backend.services.ingredient_service.get_local_ingredients"):
        
        service = IngredientService()
        return service

def test_inventory_management(ingredient_service):
    user_id = "test_user"
    
    # Initially empty
    assert ingredient_service.get_inventory(user_id) == []
    
    # Add items
    ingredient_service.add_to_inventory(user_id, "Rum")
    assert ingredient_service.get_inventory(user_id) == ["Rum"]
    
    # Add duplicate (should not duplicate)
    ingredient_service.add_to_inventory(user_id, "Rum")
    assert ingredient_service.get_inventory(user_id) == ["Rum"]
    
    # Add another
    ingredient_service.add_to_inventory(user_id, "Mint")
    assert set(ingredient_service.get_inventory(user_id)) == {"Rum", "Mint"}
    
    # Remove item
    ingredient_service.remove_from_inventory(user_id, "Rum")
    assert ingredient_service.get_inventory(user_id) == ["Mint"]
    
    # Update full inventory
    ingredient_service.update_inventory(user_id, ["Gin", "Tonic"])
    assert set(ingredient_service.get_inventory(user_id)) == {"Gin", "Tonic"}
    
    # Clear inventory
    ingredient_service.clear_inventory(user_id)
    assert ingredient_service.get_inventory(user_id) == []

def test_get_all_ingredients(ingredient_service):
    # Mock local ingredients
    mock_local = [
        Ingredient(id="1", name="Rum"),
        Ingredient(id="2", name="Gin")
    ]
    
    with patch("backend.services.ingredient_service.get_local_ingredients", return_value=mock_local):
        ingredients = ingredient_service.get_all_ingredients()
        assert len(ingredients) >= 2
        names = [i.name for i in ingredients]
        assert "Rum" in names
        assert "Gin" in names

def test_get_ingredient_by_id_local(ingredient_service):
    # Mock _query_local_ingredient
    mock_ing = Ingredient(id="http://test/rum", name="Rum")
    ingredient_service._query_local_ingredient = MagicMock(return_value=mock_ing)
    
    result = ingredient_service.get_ingredient_by_id("http://test/rum")
    assert result.name == "Rum"

def test_search_ingredients(ingredient_service):
    # Mock sparql_service.execute_query
    mock_results = {
        "results": {
            "bindings": [
                {
                    "id": {"value": "http://test/vodka"},
                    "name": {"value": "Vodka"},
                    "category": {"value": "Spirit"}
                }
            ]
        }
    }
    ingredient_service.sparql_service.execute_query.return_value = mock_results
    
    results = ingredient_service.search_ingredients("vodka")
    assert len(results) == 1
    assert results[0].name == "Vodka"
