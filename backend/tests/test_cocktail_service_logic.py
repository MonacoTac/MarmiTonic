
import pytest
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add backend directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.cocktail_service import CocktailService
from models.cocktail import Cocktail

@pytest.fixture
def mock_cocktails():
    return [
        Cocktail(
            uri="http://example.org/cocktail/1",
            id="mojito",
            name="Mojito",
            ingredients="* 50ml Rum\n* 30ml Lime Juice\n* Mint\n* Soda Water",
            parsed_ingredients=["Rum", "Lime Juice", "Mint", "Soda Water"]
        ),
        Cocktail(
            uri="http://example.org/cocktail/2",
            id="daiquiri",
            name="Daiquiri",
            ingredients="* 50ml Rum\n* 30ml Lime Juice\n* Sugar Syrup",
            parsed_ingredients=["Rum", "Lime Juice", "Sugar Syrup"]
        ),
        Cocktail(
            uri="http://example.org/cocktail/3",
            id="gin-tonic",
            name="Gin and Tonic",
            ingredients="* 50ml Gin\n* 150ml Tonic Water",
            parsed_ingredients=["Gin", "Tonic Water"]
        )
    ]

@pytest.fixture
def cocktail_service(mock_cocktails):
    # Mock dependencies
    with patch("backend.services.cocktail_service.SparqlService"), \
         patch("backend.services.cocktail_service.IngredientService"), \
         patch("backend.services.cocktail_service.get_shared_graph"):
        
        service = CocktailService()
        
        # Mock get_all_cocktails to return our test data
        service.get_all_cocktails = MagicMock(return_value=mock_cocktails)
        
        # Mock ingredient service inventory
        service.ingredient_service.get_inventory = MagicMock(return_value=[])
        
        return service

def test_search_cocktails(cocktail_service):
    results = cocktail_service.search_cocktails("Mojito")
    assert len(results) == 1
    assert results[0].name == "Mojito"+

    results = cocktail_service.search_cocktails("rum")
    # Mojito and Daiquiri contain rum, but search usually checks name/alt names. 
    # Let's check implementation: `query_lower in cocktail.name.lower()`
    # "rum" is not in "Mojito" or "Daiquiri" names.
    assert len(results) == 0
    
    # Test case insensitive
    results = cocktail_service.search_cocktails("mojito")
    assert len(results) == 1

def test_get_feasible_cocktails(cocktail_service):
    # User has Rum, Lime Juice, Mint, Soda Water (Mojito ingredients)
    cocktail_service.ingredient_service.get_inventory.return_value = ["Rum", "Lime Juice", "Mint", "Soda Water"]
    
    feasible = cocktail_service.get_feasible_cocktails("user1")
    
    # Mojito should be feasible
    assert any(c.name == "Mojito" for c in feasible)
    # Daiquiri needs Sugar Syrup, so not feasible
    assert not any(c.name == "Daiquiri" for c in feasible)

def test_get_feasible_cocktails_partial_inventory(cocktail_service):
    # User has only Rum
    cocktail_service.ingredient_service.get_inventory.return_value = ["Rum"]
    
    feasible = cocktail_service.get_feasible_cocktails("user1")
    assert len(feasible) == 0

def test_get_almost_feasible_cocktails(cocktail_service):
    # User has Rum, Lime Juice (Missing Sugar Syrup for Daiquiri - 1 missing)
    # Mojito needs Mint and Soda (2 missing)
    cocktail_service.ingredient_service.get_inventory.return_value = ["Rum", "Lime Juice"]
    
    almost = cocktail_service.get_almost_feasible_cocktails("user1")
    
    daiquiri_match = next((item for item in almost if item["cocktail"].name == "Daiquiri"), None)
    mojito_match = next((item for item in almost if item["cocktail"].name == "Mojito"), None)
    
    assert daiquiri_match is not None
    assert len(daiquiri_match["missing"]) == 1
    assert "Sugar Syrup" in daiquiri_match["missing"]
    
    assert mojito_match is not None
    assert len(mojito_match["missing"]) == 2

def test_get_cocktails_by_ingredients(cocktail_service):
    # Search for cocktails with Rum
    results = cocktail_service.get_cocktails_by_ingredients(["Rum"])
    names = [c.name for c in results]
    assert "Mojito" in names
    assert "Daiquiri" in names
    assert "Gin and Tonic" not in names
    
    # Search for cocktails with Rum AND Mint
    results = cocktail_service.get_cocktails_by_ingredients(["Rum", "Mint"])
    names = [c.name for c in results]
    assert "Mojito" in names
    assert "Daiquiri" not in names

def test_parse_ingredient_names(cocktail_service):
    # Test the parsing logic directly (even though it's used internally)
    text = "* 50ml White Rum\n* 2 dashes Angostura Bitters"
    parsed = cocktail_service._parse_ingredient_names(text)
    assert "White Rum" in parsed
    assert "Angostura Bitters" in parsed
    
    text_bullets = "• 30ml Gin\n• Tonic"
    parsed = cocktail_service._parse_ingredient_names(text_bullets)
    assert "Gin" in parsed
    assert "Tonic" in parsed

def test_get_similar_cocktails(cocktail_service):
    # Mojito and Daiquiri share Rum, Lime Juice (2 common)
    # Mojito has 4 total, Daiquiri has 3 total. Union is {Rum, Lime, Mint, Soda, Sugar} = 5.
    # Similarity = 2/5 = 0.4
    
    similar = cocktail_service.get_similar_cocktails("mojito")
    
    # Should find Daiquiri
    daiquiri_sim = next((s for s in similar if s["cocktail"].name == "Daiquiri"), None)
    assert daiquiri_sim is not None
    assert daiquiri_sim["similarity_score"] > 0
