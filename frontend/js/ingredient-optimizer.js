// Ingredient Optimizer JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('optimizer-form');
    const resultsSection = document.getElementById('results-section');
    const loadingSection = document.getElementById('loading-section');
    const cocktailCount = document.getElementById('cocktail-count');
    const selectedIngredientsList = document.getElementById('selected-ingredients');

    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        const N = document.getElementById('num-ingredients').value;

        // Show loading
        resultsSection.style.display = 'none';
        loadingSection.style.display = 'block';

        try {
            // Make API call
            const response = await fetch(`http://localhost:8000/ingredients/optimize?N=${N}`);
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
        // Update cocktail count
        cocktailCount.textContent = data.cocktail_count;

        // Clear previous ingredients
        selectedIngredientsList.innerHTML = '';

        // Add selected ingredients
        data.ingredients.forEach(ingredient => {
            const li = document.createElement('li');
            li.textContent = ingredient;
            selectedIngredientsList.appendChild(li);
        });

        // Show results section
        resultsSection.style.display = 'block';
    }
});