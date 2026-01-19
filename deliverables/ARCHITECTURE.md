# Architecture de MarmiTonic 🍸

## Vue d'ensemble

MarmiTonic est une application web de gestion et découverte de cocktails basée sur les données sémantiques (RDF/SPARQL). L'architecture suit un modèle **client-serveur** avec une séparation claire entre le frontend et le backend.

```
┌─────────────────────────────────────────────────────────────────┐
│                         UTILISATEUR                             │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           │ HTTP/REST
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FRONTEND (SPA)                             │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Pages HTML + JavaScript + CSS                           │   │
│  │  • index.html (Home)                                     │   │
│  │  • discovery.html (Découverte)                           │   │
│  │  • my-bar.html (Mon Bar)                                 │   │
│  │  • planner.html (Planificateur)                          │   │
│  │  • graph-visualization.html (Visualisation)              │   │
│  │  • sparql-explorer.html (Explorateur SPARQL)             │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Modules JavaScript                                      │   │
│  │  • api.js (Client API REST)                              │   │
│  │  • app.js (Initialisation)                               │   │
│  │  • visualization.js / d3_visualization.js (D3.js)        │   │
│  │  • navbar.js, cocktail-detail.js, planner.js...          │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           │ Fetch API (GET/POST)
                           │ http://localhost:8000
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND API (FastAPI)                        │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  main.py - Application principale                        │   │
│  │  • Middleware CORS                                       │   │
│  │  • Chargement du graphe RDF au démarrage                 │   │
│  │  • Serveur frontend intégré                              │   │
│  └──────────────────────────────────────────────────────────┘   │
│                           │                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  ROUTES (Contrôleurs)                                    │   │
│  │  ┌────────────────────────────────────────────────────┐  │   │
│  │  │ /cocktails    → cocktails.py                       │  │   │
│  │  │ /ingredients  → ingredients.py                     │  │   │
│  │  │ /planner      → planner.py                         │  │   │
│  │  │ /insights     → insights.py                        │  │   │
│  │  │ /graphs       → graphs.py                          │  │   │
│  │  │ /llm          → llm.py                             │  │   │
│  │  └────────────────────────────────────────────────────┘  │   │
│  └──────────────────┬───────────────────────────────────────┘   │
│                     │                                           │
│  ┌──────────────────▼───────────────────────────────────────┐   │
│  │  SERVICES (Couche métier)                                │   │
│  │  • cocktail_service.py      - Logique métier cocktails   │   │
│  │  • ingredient_service.py    - Logique métier ingrédients │   │
│  │  • planner_service.py       - Optimisation de recettes   │   │
│  │  • graph_service.py         - Graphes de visualisation   │   │
│  │  • sparql_service.py        - Requêtes SPARQL            │   │
│  │  • llm_service.py           - Intégration IA/LLM         │   │
│  └──────────────────┬───────────────────────────────────────┘   │
│                     │                                           │
│  ┌──────────────────▼───────────────────────────────────────┐   │
│  │  MODELS (Modèles de données)                             │   │
│  │  • cocktail.py              - Modèle Cocktail            │   │
│  │  • ingredient.py            - Modèle Ingredient          │   │
│  │  • sparql_query.py          - Requêtes SPARQL            │   │
│  └──────────────────┬───────────────────────────────────────┘   │
│                     │                                           │
│  ┌──────────────────▼───────────────────────────────────────┐   │
│  │  DATA LAYER (Accès aux données)                          │   │
│  │  • rdfbinder.py             - Import données DBpedia     │   │
│  │  • ttl_parser.py            - Parsing fichiers TTL       │   │
│  │  • data.ttl                 - Base de données RDF        │   │
│  └────────────────────────────────────────────────────────┬─┘   │
│                                                           │     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  UTILS (Utilitaires)                                     │   │
│  │  • graph_loader.py          - Chargement graphe RDF      │   │
│  │  • graph_utils.py           - Manipulation graphes       │   │
│  │  • front_server.py          - Serveur frontend           │   │
│  │  • force_directed_graphs/   - Génération graphes Force   │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                  SOURCES DE DONNÉES                             │
│  • RDF Graph (RDFLib)    - Graphe sémantique en mémoire         │
│  • data.ttl              - Base de données Turtle/RDF           │
│  • DBpedia SPARQL        - Endpoint externe (import)            │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📦 Composants principaux

### 1. Frontend (SPA - Single Page Application)

**Technologies:** HTML5, CSS3, JavaScript (Vanilla), D3.js

**Structure:**
```
frontend/
├── index.html              # Page d'accueil
├── pages/                  # Pages de l'application
│   ├── discovery.html      # Découverte de cocktails
│   ├── my-bar.html         # Gestion du bar personnel
│   ├── planner.html        # Planification d'achats
│   ├── graph-visualization.html
│   └── sparql-explorer.html
├── js/                     # Scripts JavaScript
│   ├── api.js              # Client API REST
│   ├── app.js              # Point d'entrée
│   ├── visualization.js    # Visualisations D3.js
│   └── ...
└── css/                    # Feuilles de style
    ├── styles.css
    ├── common.css
    └── ...
```

**Responsabilités:**
- Interface utilisateur interactive
- Appels REST vers le backend
- Visualisations de graphes (D3.js)
- Navigation SPA
- Gestion du state local

---

### 2. Backend API (FastAPI)

**Technologies:** Python 3.x, FastAPI, RDFLib, SPARQL

#### 2.1 Couche Routes (API Endpoints)

| Route | Fichier | Description |
|-------|---------|-------------|
| `/cocktails/*` | `cocktails.py` | CRUD et recherche de cocktails |
| `/ingredients/*` | `ingredients.py` | Gestion des ingrédients |
| `/planner/*` | `planner.py` | Optimisation des achats |
| `/insights/*` | `insights.py` | Statistiques et analyses |
| `/graphs/*` | `graphs.py` | Graphes de visualisation |
| `/llm/*` | `llm.py` | Intégration IA/LLM |

**Exemple d'endpoints:**
```
GET  /cocktails                    # Liste tous les cocktails
GET  /cocktails/feasible/{user_id} # Cocktails réalisables
GET  /cocktails/by-ingredients     # Recherche par ingrédients
POST /planner/playlist-mode        # Optimisation playlist
GET  /graphs/force-directed        # Graphe de force
```

#### 2.2 Couche Services (Business Logic)

| Service | Responsabilité |
|---------|----------------|
| `sparql_service.py` | Exécution de requêtes SPARQL sur le graphe RDF |
| `cocktail_service.py` | Logique métier pour les cocktails |
| `ingredient_service.py` | Logique métier pour les ingrédients |
| `planner_service.py` | Algorithmes d'optimisation (recherche de chemins, minimisation) |
| `graph_service.py` | Génération de graphes de visualisation |
| `llm_service.py` | Intégration avec des modèles de langage |

**Flux typique:**
```
Route → Service → SPARQL Query → RDF Graph → Résultat
```

#### 2.3 Couche Data (Accès aux données)

- **`rdfbinder.py`**: Import de données depuis DBpedia
- **`ttl_parser.py`**: Parsing de fichiers Turtle (RDF)
- **`data.ttl`**: Base de données sémantique (format Turtle)
- **`graph_loader.py`**: Chargement et cache du graphe RDF

**Format des données:** RDF (Resource Description Framework)
- Triplets Subject-Predicate-Object
- Ontologies: DBpedia, RDFS, FOAF, DCT

---

### 3. Modèles de données

**`cocktail.py`**: Représentation d'un cocktail
```python
class Cocktail:
    uri: str
    name: str
    description: str
    ingredients: List[Ingredient]
    garnish: str
    served: str
    image: str
    ...
```

**`ingredient.py`**: Représentation d'un ingrédient
```python
class Ingredient:
    uri: str
    name: str
    category: str
    ...
```

---

## 🔄 Flux de données

### Exemple: Recherche de cocktails par ingrédients

```
1. USER → Frontend (my-bar.html)
   └─ Sélectionne ["Vodka", "Lime juice"]

2. Frontend (api.js) → Backend
   └─ GET /cocktails/by-ingredients?ingredients=Vodka&ingredients=Lime+juice

3. Backend (cocktails.py)
   └─ Route reçoit la requête
      └─ Appelle cocktail_service.get_cocktails_by_ingredients()

4. CocktailService
   └─ Appelle sparql_service.query()
      └─ Construit une requête SPARQL
         └─ Ex: SELECT ?cocktail WHERE { ?cocktail dbp:ingredients ?ing ... }

5. SparqlService
   └─ Exécute la requête sur le graphe RDF (RDFLib)
      └─ Retourne les résultats bruts

6. CocktailService
   └─ Parse les résultats
      └─ Construit des objets Cocktail
         └─ Retourne JSON

7. Backend → Frontend
   └─ JSON Response: [{"name": "Moscow Mule", ...}, ...]

8. Frontend
   └─ Affiche les résultats dans l'interface
```

---

## 🗄️ Gestion des données RDF

### Structure du graphe sémantique

```turtle
@prefix dbo: <http://dbpedia.org/ontology/> .
@prefix dbp: <http://dbpedia.org/property/> .
@prefix dbr: <http://dbpedia.org/resource/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

# Exemple de triplets RDF
dbr:Moscow_Mule 
    rdfs:label "Moscow Mule"@en ;
    dbo:description "A cocktail made with vodka..."@en ;
    dbp:ingredients "Vodka, Ginger beer, Lime juice" ;
    dbp:served "On the rocks" ;
    foaf:depiction <http://...image.jpg> .
```

### Chargement du graphe

1. **Au démarrage** (`main.py`):
   ```python
   RDF_GRAPH = get_shared_graph()  # Singleton
   ```

2. **`graph_loader.py`**:
   - Parse `data.ttl`
   - Crée un graphe RDFLib en mémoire
   - Partagé par tous les services (performance)

3. **Requêtes SPARQL**:
   - Exécutées via `sparql_service.py`
   - Utilisent la syntaxe SPARQL 1.1

---

## 🔧 Services utilitaires

### Force Directed Graphs (`utils/force_directed_graphs/`)

Module de génération de graphes force-directed pour la visualisation:
- **`main.py`**: Point d'entrée
- **`layout.py`**: Algorithme de positionnement (force-based)
- **`render.py`**: Rendu du graphe
- **`data.py`**: Préparation des données
- **`config.py`**: Configuration

### Graph Utilities

- **`graph_utils.py`**: Fonctions de manipulation de graphes RDF
- **`front_server.py`**: Serveur HTTP pour le frontend (intégré au backend)

---

## 🧪 Tests

Structure des tests:
```
backend/tests/
├── conftest.py                    # Configuration pytest
├── test_api_routes.py             # Tests d'intégration API
├── test_cocktail_service.py       # Tests unitaires services
├── test_sparql_service.py         # Tests requêtes SPARQL
├── test_planner_service.py        # Tests algorithmes
└── ...
```

Configuration: `pytest.ini`

---

## 🚀 Déploiement et exécution

### Démarrage de l'application

1. **Activation environnement virtuel:**
   ```bash
   .venv\Scripts\Activate.ps1
   ```

2. **Installation dépendances:**
   ```bash
   pip install -r backend/requirements.txt
   ```

3. **Lancement du serveur:**
   ```bash
   uvicorn backend.main:app --reload
   ```

4. **Accès:**
   - API: http://localhost:8000
   - Frontend: http://localhost:8000 (servi par le backend)
   - Docs API: http://localhost:8000/docs

---

## 🏗️ Patterns et principes architecturaux

### 1. Architecture en couches

```
Présentation → Routes → Services → Data Access → Data Store
```

### 2. Séparation des responsabilités

- **Routes**: Gestion HTTP, validation, erreurs
- **Services**: Logique métier, orchestration
- **Data**: Accès aux données, parsing RDF

### 3. Singleton pour le graphe RDF

- Un seul graphe chargé en mémoire
- Partagé par tous les services
- Améliore les performances

### 4. API REST

- Endpoints RESTful
- JSON comme format d'échange
- CORS activé pour le frontend

### 5. Web sémantique

- Utilisation de RDF/SPARQL
- Ontologies standardisées (DBpedia, RDFS)
- Requêtes déclaratives puissantes

---

## 📊 Technologies clés

| Couche | Technologie | Utilisation |
|--------|-------------|-------------|
| Frontend | HTML/CSS/JS | Interface utilisateur |
| Frontend | D3.js | Visualisations interactives |
| Backend | FastAPI | Framework API REST |
| Backend | Python 3.x | Langage principal |
| Data | RDFLib | Manipulation graphes RDF |
| Data | SPARQL | Requêtes sémantiques |
| Data | Turtle (TTL) | Format de sérialisation RDF |
| Dev | pytest | Tests automatisés |
| Dev | uvicorn | Serveur ASGI |

---

## 🔐 Sécurité et bonnes pratiques

- ✅ CORS configuré (middleware)
- ✅ Validation des entrées (FastAPI)
- ✅ Gestion des erreurs (HTTPException)
- ✅ Séparation des environnements (.venv)
- ✅ Tests automatisés

---

## 📝 Notes d'architecture

### Points forts

1. **Séparation claire frontend/backend**
2. **Utilisation du web sémantique** (flexibilité, requêtes puissantes)
3. **Architecture modulaire** (services réutilisables)
4. **API REST documentée** (FastAPI auto-génère /docs)
5. **Graphe en mémoire** (performance)

### Points d'attention

1. **Scalabilité**: Le graphe RDF est en mémoire (limite pour très gros volumes)
2. **Caching**: Possibilité d'ajouter un cache Redis pour les requêtes fréquentes
3. **Authentification**: Pas d'authentification actuellement (user_id en param)
4. **Base de données**: TTL statique (pas de persistance des modifications)

### Évolutions possibles

- 🔄 Ajout d'un système d'authentification (JWT)
- 🗄️ Migration vers une base de données triple store (GraphDB, Virtuoso)
- 📱 API mobile (adaptation endpoints)
- 🤖 Extension du module LLM (recommandations personnalisées)
- 📊 Tableau de bord analytics avancé
- 🔔 Notifications temps réel (WebSockets)

---

## 📚 Références

- **FastAPI**: https://fastapi.tiangolo.com/
- **RDFLib**: https://rdflib.readthedocs.io/
- **SPARQL**: https://www.w3.org/TR/sparql11-query/
- **D3.js**: https://d3js.org/
- **DBpedia**: https://www.dbpedia.org/

---

*Document généré le 17 janvier 2026*
