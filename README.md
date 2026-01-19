# MarmiTonic

**MarmiTonic** is a semantic web application designed for intelligent cocktail discovery and bar management. Developed as part of the "Web Sémantique" course at INSA Lyon, it leverages Linked Data technologies (DBpedia), SPARQL queries, and graph analysis to provide personalized recommendations and optimize ingredient usage.

## Key Features

### My Bar & Inventory
- **Smart Inventory**: Manage your available ingredients.
- **Feasibility Analysis**: Instantly see which cocktails you can make (0 missing ingredients) or almost make (1-2 missing).
- **Shopping Cart**: Easily add missing ingredients to your shopping list.

### Intelligent Discovery
- **Recommendation Engine**: Discover cocktails with similar ingredients, shared styles ("vibe"), or bridges between different cocktail families.
- **Graph Insights**: Visualize the relationships between cocktails and ingredients using interactive force-directed graphs.
- **SPARQL Explorer**: Advanced users can execute custom SPARQL queries directly against the knowledge graph.

### Optimization
- **Bar Minimum**: The "Playlist" mode optimizes your shopping list to create the maximum number of desired cocktails with the minimum number of ingredients.

## Getting Started

### Prerequisites
- **Python 3.8+**
- **Git**

### Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/MonacoTac/MarmiTonic.git
    cd MarmiTonic
    ```

2.  **Set up the environment**
     Navigate to the backend directory and create a virtual environment:
    ```bash
    cd backend
    python -m venv .venv
    
    # Windows
    .venv\Scripts\activate
    
    # Linux/MacOS
    source .venv/bin/activate
    ```

3.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the application**
    From the project root (ensure `.venv` is activated):
    ```bash
    uvicorn backend.main:app --reload
    ```
    - **Backend API**: `http://localhost:8000`
    - **Frontend**: `http://localhost:8000` (Static files served by backend) or open `frontend/index.html` directly.

## Architecture

MarmiTonic follows a **Client-Server** architecture:
- **Frontend**: Vanilla JavaScript (ES6+), HTML5, CSS3. Uses D3.js for graph visualizations.
- **Backend**: Python FastAPI. Handles SPARQL queries, graph logic (NetworkX), and REST API endpoints.
- **Data**: In-memory RDF graph loaded from `data.ttl` (extracted from DBpedia).

For detailed architecture documentation, see [ARCHITECTURE.md](deliverables/ARCHITECTURE.md).

## Testing

The project includes a comprehensive test suite covering services, APIs, and models.

```bash
# Run all tests
python -m pytest backend/tests/ -v
```

## Documentation

- [**Specifications**](deliverables/SPECIFICATIONS.md): Detailed functional requirements.
- [**Project Structure**](deliverables/PROJECT_STRUCTURE.md): File organization.
- [**SPARQL Queries**](deliverables/SPARQL-QUERIES.md): Catalog of semantic queries used.

## Team

- Elise Bachet
- Andy Gonzales
- Lou Reina-Kuntziger
- William Michaud
- Louis Labory
- Jason Laval

*Generative AI has been used to assist in code generation and documentation drafting.*

---
*Developed for INSA Lyon - 4IF Web Sémantique*

