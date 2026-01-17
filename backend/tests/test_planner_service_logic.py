
import pytest
from unittest.mock import MagicMock, patch
from backend.services.planner_service import PlannerService
from backend.models.cocktail import Cocktail

@pytest.fixture
def mock_cocktails():
    return [
        Cocktail(id="1", name="C1", parsed_ingredients=["A", "B"]),
        Cocktail(id="2", name="C2", parsed_ingredients=["B", "C"]),
        Cocktail(id="3", name="C3", parsed_ingredients=["C", "D"])
    ]

@pytest.fixture
def planner_service(mock_cocktails):
    with patch("backend.services.planner_service.CocktailService") as MockCocktailService, \
         patch("backend.services.planner_service.IngredientService"):
        
        mock_service = MockCocktailService.return_value
        mock_service.get_all_cocktails.return_value = mock_cocktails
        
        service = PlannerService()
        return service

def test_optimize_playlist_mode(planner_service):
    # C1 needs A, B
    # C2 needs B, C
    # C3 needs C, D
    # The current implementation seems to select ingredients that appear in the most *remaining* cocktails.
    # And it considers a cocktail "covered" if *any* of its ingredients is selected? 
    # Let's verify the logic in the test based on code reading.
    
    # If I select B, it appears in C1 and C2.
    # If I select C, it appears in C2 and C3.
    
    # Code logic:
    # 1. Universe = {C1, C2, C3}
    # 2. Iteration 1:
    #    - Ingredient A covers {C1}
    #    - Ingredient B covers {C1, C2} -> Max cover 2, Best B
    #    - Ingredient C covers {C2, C3} -> Max cover 2 (tie)
    #    - Ingredient D covers {C3}
    #    Suppose it picks B.
    #    Selected = [B]
    #    Covered = {C1, C2}
    # 3. Iteration 2:
    #    - Remaining Universe to cover: {C3} (since C1, C2 are in covered)
    #    - Ingredient A covers {} (C1 already covered)
    #    - Ingredient C covers {C3} (C2 already covered) -> Max cover 1, Best C
    #    - Ingredient D covers {C3} -> Max cover 1 (tie)
    #    Suppose it picks C.
    #    Selected = [B, C]
    #    Covered = {C1, C2, C3}
    # 4. Universe covered. Stop.
    
    # Result should be [B, C] (or equivalent set) and all cocktails covered.
    
    result = planner_service.optimize_playlist_mode(["C1", "C2", "C3"])
    
    assert set(result['covered_cocktails']) == {"C1", "C2", "C3"}
    # The order depends on iteration order of set, but B and C are the optimal set cover for "any ingredient matches".
    selected = result['selected_ingredients']
    assert "B" in selected
    assert "C" in selected
    assert len(selected) == 2
