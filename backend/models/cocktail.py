from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict


class Cocktail(BaseModel):
    uri: str = Field(..., description="DBpedia resource URI for the cocktail")
    id: str = Field(..., description="URL-friendly slug generated from name")
    name: str = Field(..., min_length=1, description="Name of the cocktail")
    description: Optional[str] = Field(None, description="Description of the cocktail")
    image: Optional[str] = Field(None, description="URL to cocktail image")
    ingredients: Optional[str] = Field(None, description="Ingredients list with measurements")
    parsed_ingredients: Optional[List[str]] = Field(None, description="Extracted ingredient names")
    ingredient_uris: Optional[List[str]] = Field(None, description="Semantic URIs for ingredients")
    preparation: Optional[str] = Field(None, description="Preparation instructions")
    source_link: Optional[str] = Field(None, description="Source link for the recipe")
    categories: Optional[List[str]] = Field(None, description="Categories the cocktail belongs to")
    related_ingredients: Optional[List[str]] = Field(None, description="Related ingredients and concepts")

    model_config = ConfigDict(
        json_encoders = {
            # Custom encoders if needed
        }
    )