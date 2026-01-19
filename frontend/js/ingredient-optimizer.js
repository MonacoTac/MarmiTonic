// Ingredient Optimizer JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('optimizer-form');
    const resultsSection = document.getElementById('results-section');
    const loadingSection = document.getElementById('loading-section');
    const cocktailCount = document.getElementById('cocktail-count');
    const selectedIngredientsList = document.getElementById('selected-ingredients');
    const possibleCocktailsGrid = document.getElementById('possible-cocktails-grid');

    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        const N = document.getElementById('num-ingredients').value;

        // Show loading
        resultsSection.style.display = 'none';
        loadingSection.style.display = 'block';

        try {
            // Make API call
            const response = await fetch(`${API_BASE_URL}/ingredients/optimize?N=${N}`);
            if (!response.ok) {
                throw new Error('Failed to optimize ingredients');
            }
            const data = await response.json();

            // Display results
            displayResults(data);
        } catch (error) {
            console.error('Error:', error);
            alert('Erreur lors de l\'optimisation. Veuillez réessayer.');
        } finally {
            // Hide loading
            loadingSection.style.display = 'none';
        }
    });

    function displayResults(data) {
        console.log('Displaying results:', data);
        
        // Update cocktail count
        cocktailCount.textContent = data.cocktail_count;

        // Clear previous ingredients
        selectedIngredientsList.innerHTML = '';

        // Add selected ingredients
        if (data.ingredients && Array.isArray(data.ingredients)) {
            data.ingredients.forEach(ingredient => {
                const li = document.createElement('li');
                li.textContent = ingredient;
                selectedIngredientsList.appendChild(li);
            });
        }

        // Display possible cocktails
        const possibleCocktailsGrid = document.getElementById('possible-cocktails-grid');
        if (possibleCocktailsGrid) {
            possibleCocktailsGrid.innerHTML = '';
            
            if (data.cocktails && Array.isArray(data.cocktails) && data.cocktails.length > 0) {
                console.log('Rendering', data.cocktails.length, 'cocktails');
                const cocktailsHtml = data.cocktails.map(cocktail => {
                    // Safe access to properties
                    const id = cocktail.id || '';
                    const name = cocktail.name || 'Cocktail Inconnu';
                    const image = getCocktailImage(cocktail);
                    
                    return `
                    <div class="cocktail-card" onclick="location.href='cocktail-detail.html?id=${id}'">
                        <div class="cocktail-card-image">
                            <img src="${image}" alt="${name}" onerror="this.src='https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?w=300&h=300&fit=crop'">
                        </div>
                        <h3>${name}</h3>
                    </div>
                    `;
                }).join('');
                
                possibleCocktailsGrid.innerHTML = cocktailsHtml;
            } else {
                 console.log('No cocktails to render');
                 possibleCocktailsGrid.innerHTML = '<p class="no-results">Aucun cocktail trouvé avec ces ingrédients.</p>';
            }
        } else {
            console.error('Element #possible-cocktails-grid not found in DOM');
        }

        // Show results section
        resultsSection.style.display = 'block';
    }

    function getCocktailImage(cocktail) {
        if (cocktail.image && cocktail.image.startsWith('http')) {
            return cocktail.image;
        }
        return 'https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?w=300&h=300&fit=crop';
    }
});