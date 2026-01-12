// API calls to the backend
const API_BASE_URL = 'http://localhost:8000';

// Fetch cocktails
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

// Fetch ingredients
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

// Execute SPARQL query
async function executeSparqlQuery(query) {
    try {
        const response = await fetch(`${API_BASE_URL}/sparql`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query }),
        });
        if (!response.ok) {
            throw new Error('Failed to execute SPARQL query');
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error executing SPARQL query:', error);
        return [];
    }
}

// Graph API functions
async function fetchBasicGraph() {
    try {
        const response = await fetch(`${API_BASE_URL}/graphs/basic`);
        if (!response.ok) {
            throw new Error('Failed to fetch basic graph');
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching basic graph:', error);
        return null;
    }
}

async function fetchForceDirectedGraph() {
    try {
        const response = await fetch(`${API_BASE_URL}/graphs/force-directed`);
        if (!response.ok) {
            throw new Error('Failed to fetch force-directed graph');
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching force-directed graph:', error);
        return null;
    }
}

async function fetchSparqlGraph() {
    try {
        const response = await fetch(`${API_BASE_URL}/graphs/sparql`);
        if (!response.ok) {
            throw new Error('Failed to fetch SPARQL graph');
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching SPARQL graph:', error);
        return null;
    }
}

async function fetchCentralityGraph() {
    try {
        const response = await fetch(`${API_BASE_URL}/graphs/centrality`);
        if (!response.ok) {
            throw new Error('Failed to fetch centrality graph');
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching centrality graph:', error);
        return null;
    }
}

async function fetchCommunityGraph() {
    try {
        const response = await fetch(`${API_BASE_URL}/graphs/communities`);
        if (!response.ok) {
            throw new Error('Failed to fetch community graph');
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching community graph:', error);
        return null;
    }
}

async function fetchGraphStatistics() {
    try {
        const response = await fetch(`${API_BASE_URL}/graphs/statistics`);
        if (!response.ok) {
            throw new Error('Failed to fetch graph statistics');
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching graph statistics:', error);
        return null;
    }
}

async function fetchGraphComponents() {
    try {
        const response = await fetch(`${API_BASE_URL}/graphs/components`);
        if (!response.ok) {
            throw new Error('Failed to fetch graph components');
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching graph components:', error);
        return null;
    }
}