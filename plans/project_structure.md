# Project Structure Plan for MarmiTonic

## Overview
This document outlines the planned folder structure and template files for the MarmiTonic project, which includes a pure HTML, CSS, and JavaScript frontend and a Python FastAPI backend.

## Folder Structure

### Frontend
- `frontend/`
  - `index.html`: Main entry point for the application.
  - `css/`
    - `styles.css`: Main stylesheet.
  - `js/`
    - `app.js`: Main JavaScript file for handling frontend logic.
    - `api.js`: JavaScript file for API calls to the backend.
  - `pages/`
    - `my-bar.html`: Template for the "My Bar" feature.
    - `discovery.html`: Template for the "Discovery" feature.
    - `planner.html`: Template for the "Planner" feature.
    - `insights.html`: Template for the "Insights" feature.

### Backend
- `backend/`
  - `main.py`: Main FastAPI application file.
  - `models/`
    - `cocktail.py`: Model for cocktails.
    - `ingredient.py`: Model for ingredients.
  - `routes/`
    - `cocktails.py`: Routes for cocktail-related endpoints.
    - `ingredients.py`: Routes for ingredient-related endpoints.
  - `services/`
    - `cocktail_service.py`: Service for cocktail-related operations.
    - `ingredient_service.py`: Service for ingredient-related operations.
  - `data/`
    - `cocktails.json`: Sample data for cocktails.
    - `ingredients.json`: Sample data for ingredients.

## Template Files

### Frontend Templates

#### `frontend/index.html`
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MarmiTonic</title>
    <link rel="stylesheet" href="css/styles.css">
</head>
<body>
    <header>
        <h1>MarmiTonic</h1>
        <nav>
            <ul>
                <li><a href="pages/my-bar.html">My Bar</a></li>
                <li><a href="pages/discovery.html">Discovery</a></li>
                <li><a href="pages/planner.html">Planner</a></li>
                <li><a href="pages/insights.html">Insights</a></li>
            </ul>
        </nav>
    </header>
    <main>
        <section id="welcome">
            <h2>Welcome to MarmiTonic</h2>
            <p>Discover cocktails based on your ingredients and optimize your bar inventory.</p>
        </section>
    </main>
    <footer>
        <p>&copy; 2026 MarmiTonic</p>
    </footer>
    <script src="js/app.js"></script>
</body>
</html>
```

#### `frontend/css/styles.css`
```css
/* Global Styles */
body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 0;
    background-color: #f4f4f9;
    color: #333;
}

header {
    background-color: #333;
    color: #fff;
    padding: 1rem;
    text-align: center;
}

nav ul {
    list-style-type: none;
    padding: 0;
    display: flex;
    justify-content: center;
    gap: 1rem;
}

nav a {
    color: #fff;
    text-decoration: none;
}

main {
    padding: 1rem;
}

footer {
    background-color: #333;
    color: #fff;
    text-align: center;
    padding: 1rem;
    position: fixed;
    bottom: 0;
    width: 100%;
}
```

#### `frontend/js/app.js`
```javascript
// Main application logic
console.log("MarmiTonic app initialized");

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    console.log("DOM fully loaded and parsed");
    
    // Add event listeners or other initialization logic here
});
```

#### `frontend/js/api.js`
```javascript
// API calls to the backend
const API_BASE_URL = 'http://localhost:8000';

// Example API call to fetch cocktails
async function fetchCocktails() {
    try {
        const response = await fetch(`${API_BASE_URL}/cocktails`);
        if (!response.ok) {
            throw new Error('Failed to fetch cocktails');
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching cocktails:', error);
        return [];
    }
}

// Example API call to fetch ingredients
async function fetchIngredients() {
    try {
        const response = await fetch(`${API_BASE_URL}/ingredients`);
        if (!response.ok) {
            throw new Error('Failed to fetch ingredients');
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching ingredients:', error);
        return [];
    }
}
```

#### `frontend/pages/my-bar.html`
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Bar - MarmiTonic</title>
    <link rel="stylesheet" href="../css/styles.css">
</head>
<body>
    <header>
        <h1>My Bar</h1>
        <nav>
            <ul>
                <li><a href="../index.html">Home</a></li>
                <li><a href="discovery.html">Discovery</a></li>
                <li><a href="planner.html">Planner</a></li>
                <li><a href="insights.html">Insights</a></li>
            </ul>
        </nav>
    </header>
    <main>
        <section id="my-bar">
            <h2>Your Ingredients</h2>
            <div id="ingredients-list">
                <!-- Ingredients will be dynamically loaded here -->
            </div>
            <h2>Feasible Cocktails</h2>
            <div id="feasible-cocktails">
                <!-- Feasible cocktails will be dynamically loaded here -->
            </div>
        </section>
    </main>
    <footer>
        <p>&copy; 2026 MarmiTonic</p>
    </footer>
    <script src="../js/app.js"></script>
    <script src="../js/api.js"></script>
</body>
</html>
```

#### `frontend/pages/discovery.html`
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Discovery - MarmiTonic</title>
    <link rel="stylesheet" href="../css/styles.css">
</head>
<body>
    <header>
        <h1>Discovery</h1>
        <nav>
            <ul>
                <li><a href="../index.html">Home</a></li>
                <li><a href="my-bar.html">My Bar</a></li>
                <li><a href="planner.html">Planner</a></li>
                <li><a href="insights.html">Insights</a></li>
            </ul>
        </nav>
    </header>
    <main>
        <section id="discovery">
            <h2>Discover New Cocktails</h2>
            <div id="cocktail-list">
                <!-- Cocktails will be dynamically loaded here -->
            </div>
        </section>
    </main>
    <footer>
        <p>&copy; 2026 MarmiTonic</p>
    </footer>
    <script src="../js/app.js"></script>
    <script src="../js/api.js"></script>
</body>
</html>
```

#### `frontend/pages/planner.html`
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Planner - MarmiTonic</title>
    <link rel="stylesheet" href="../css/styles.css">
</head>
<body>
    <header>
        <h1>Planner</h1>
        <nav>
            <ul>
                <li><a href="../index.html">Home</a></li>
                <li><a href="my-bar.html">My Bar</a></li>
                <li><a href="discovery.html">Discovery</a></li>
                <li><a href="insights.html">Insights</a></li>
            </ul>
        </nav>
    </header>
    <main>
        <section id="planner">
            <h2>Plan Your Bar</h2>
            <div id="planner-options">
                <!-- Planner options will be dynamically loaded here -->
            </div>
        </section>
    </main>
    <footer>
        <p>&copy; 2026 MarmiTonic</p>
    </footer>
    <script src="../js/app.js"></script>
    <script src="../js/api.js"></script>
</body>
</html>
```

#### `frontend/pages/insights.html`
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Insights - MarmiTonic</title>
    <link rel="stylesheet" href="../css/styles.css">
</head>
<body>
    <header>
        <h1>Insights</h1>
        <nav>
            <ul>
                <li><a href="../index.html">Home</a></li>
                <li><a href="my-bar.html">My Bar</a></li>
                <li><a href="discovery.html">Discovery</a></li>
                <li><a href="planner.html">Planner</a></li>
            </ul>
        </nav>
    </header>
    <main>
        <section id="insights">
            <h2>Insights</h2>
            <div id="insights-data">
                <!-- Insights data will be dynamically loaded here -->
            </div>
        </section>
    </main>
    <footer>
        <p>&copy; 2026 MarmiTonic</p>
    </footer>
    <script src="../js/app.js"></script>
    <script src="../js/api.js"></script>
</body>
</html>
```

### Backend Templates

#### `backend/main.py`
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to MarmiTonic API"}

@app.get("/cocktails")
def get_cocktails():
    # Placeholder for fetching cocktails
    return {"cocktails": []}

@app.get("/ingredients")
def get_ingredients():
    # Placeholder for fetching ingredients
    return {"ingredients": []}
```

#### `backend/models/cocktail.py`
```python
from pydantic import BaseModel
from typing import List

class Cocktail(BaseModel):
    id: int
    name: str
    ingredients: List[str]
    instructions: str
```

#### `backend/models/ingredient.py`
```python
from pydantic import BaseModel

class Ingredient(BaseModel):
    id: int
    name: str
    category: str
```

#### `backend/routes/cocktails.py`
```python
from fastapi import APIRouter
from ..models.cocktail import Cocktail

router = APIRouter()

@router.get("/cocktails", response_model=List[Cocktail])
def get_cocktails():
    # Placeholder for fetching cocktails
    return []
```

#### `backend/routes/ingredients.py`
```python
from fastapi import APIRouter
from ..models.ingredient import Ingredient

router = APIRouter()

@router.get("/ingredients", response_model=List[Ingredient])
def get_ingredients():
    # Placeholder for fetching ingredients
    return []
```

#### `backend/services/cocktail_service.py`
```python
from ..models.cocktail import Cocktail
from typing import List

class CocktailService:
    def __init__(self):
        pass
    
    def get_cocktails(self) -> List[Cocktail]:
        # Placeholder for fetching cocktails
        return []
```

#### `backend/services/ingredient_service.py`
```python
from ..models.ingredient import Ingredient
from typing import List

class IngredientService:
    def __init__(self):
        pass
    
    def get_ingredients(self) -> List[Ingredient]:
        # Placeholder for fetching ingredients
        return []
```

#### `backend/data/cocktails.json`
```json
[
    {
        "id": 1,
        "name": "Martini",
        "ingredients": ["gin", "vermouth"],
        "instructions": "Mix gin and vermouth in a shaker with ice. Strain into a chilled glass."
    }
]
```

#### `backend/data/ingredients.json`
```json
[
    {
        "id": 1,
        "name": "gin",
        "category": "spirit"
    }
]
```

## Next Steps
1. Review the plan with the user.
2. Switch to Orchestrator mode for implementation.