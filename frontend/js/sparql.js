// SPARQL query utilities
async function queryCocktails() {
    const query = `
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX dbp: <http://dbpedia.org/property/>
        
        SELECT ?cocktail ?ingredient WHERE {
            ?cocktail a dbo:Cocktail .
            ?cocktail dbp:ingredient ?ingredient .
        }
    `;
    
    const results = await executeSparqlQuery(query);
    return results;
}

async function queryIngredients() {
    const query = `
        PREFIX dbo: <http://dbpedia.org/ontology/>
        
        SELECT ?ingredient WHERE {
            ?ingredient a dbo:Ingredient .
        }
    `;
    
    const results = await executeSparqlQuery(query);
    return results;
}