from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, List


class Ingredient(BaseModel):
    id: str = Field(..., description="DBpedia resource URI for the ingredient")
    name: str = Field(..., min_length=1, description="Name of the ingredient")
    description: Optional[str] = Field(None, description="Description of the ingredient")
    image: Optional[str] = Field(None, description="URL to ingredient image")
    categories: Optional[List[str]] = Field(None, description="Categories the ingredient belongs to")

    model_config = ConfigDict(
        json_encoders = {
            # Custom encoders if needed
        }
    )