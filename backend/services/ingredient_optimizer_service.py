from typing import List, Dict, Set
from ..services.cocktail_service import CocktailService
from ..services.ingredient_service import IngredientService

class IngredientOptimizerService:
    def __init__(self):
        self.cocktail_service = CocktailService()
        self.ingredient_service = IngredientService()

    def find_optimal_ingredients(self, N: int) -> Dict[str, any]:
        """
        Find the optimal set of N ingredients that can produce the largest number of cocktails.
        Uses a greedy algorithm to iteratively select ingredients that add the most new cocktails.
        
        Args:
            N (int): Number of ingredients to select
            
        Returns:
            Dict[str, any]: Dictionary containing selected ingredients and cocktail count
        """
        # Step 1: Get all cocktails and their ingredients
        cocktails = self.cocktail_service.get_all_cocktails()
        
        # Step 2: Build ingredient frequency map
        ingredient_freq = {}
        for cocktail in cocktails:
            if cocktail.parsed_ingredients:
                for ingredient in cocktail.parsed_ingredients:
                    ingredient_freq[ingredient] = ingredient_freq.get(ingredient, 0) + 1
        
        # Step 3: Greedy selection
        selected_ingredients = []
        covered_cocktails = set()
        
        for _ in range(N):
            best_ingredient = None
            best_count = 0
            
            for ingredient, freq in ingredient_freq.items():
                if ingredient in selected_ingredients:
                    continue
                
                # Calculate how many new cocktails this ingredient would add
                new_cocktails = 0
                for cocktail in cocktails:
                    if cocktail.name not in covered_cocktails and cocktail.parsed_ingredients and ingredient in cocktail.parsed_ingredients:
                        new_cocktails += 1
                
                if new_cocktails > best_count:
                    best_count = new_cocktails
                    best_ingredient = ingredient
            
            if best_ingredient:
                selected_ingredients.append(best_ingredient)
                # Update covered cocktails
                for cocktail in cocktails:
                    if cocktail.parsed_ingredients and best_ingredient in cocktail.parsed_ingredients:
                        covered_cocktails.add(cocktail.name)
        
        return {
            "ingredients": selected_ingredients,
            "cocktail_count": len(covered_cocktails)
        }