"""
Comprehensive error handling tests for backend services.

This module tests exception handling, network failure recovery, invalid data handling,
missing file handling, and fallback mechanisms across all backend services:
- SparqlService
- CocktailService
- IngredientService
- GraphService
- PlannerService
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import os
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDFS

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import services
from services.sparql_service import SparqlService
from services.cocktail_service import CocktailService
from services.ingredient_service import IngredientService
from services.graph_service import GraphService
from services.planner_service import PlannerService

# Import models
from models.cocktail import Cocktail
from models.ingredient import Ingredient


class TestSparqlServiceErrorHandling:
    """Test error handling in SparqlService"""

    @patch('services.sparql_service.IBADataParser')
    def test_init_missing_ttl_file(self, mock_parser):
        """Test initialization when TTL file doesn't exist"""
        mock_parser.side_effect = FileNotFoundError("File not found")
        
        service = SparqlService("nonexistent.ttl")
        # Check if fallback to shared graph works
        assert service.local_graph is not None

    @patch('services.sparql_service.IBADataParser')
    def test_init_corrupted_ttl_file(self, mock_parser):
        """Test initialization with corrupted TTL file"""
        mock_parser.side_effect = Exception("Parse error: Invalid syntax")
        
        service = SparqlService("corrupted.ttl")
        # Check if fallback to shared graph works
        assert service.local_graph is not None

    @patch('services.sparql_service.SPARQLWrapper')
    @patch('services.sparql_service.requests')
    def test_execute_query_network_timeout(self, mock_requests, mock_wrapper):
        """Test network timeout during remote query"""
        mock_instance = Mock()
        mock_wrapper.return_value = mock_instance
        mock_instance.query.side_effect = Exception("Connection timeout")
        
        # Also mock requests to fail
        mock_requests.get.side_effect = Exception("Request failed")
        
        service = SparqlService()
        result = service.execute_query("SELECT * WHERE { ?s ?p ?o }")
        assert result is None

    @patch('services.sparql_service.SPARQLWrapper')
    @patch('services.sparql_service.requests')
    def test_execute_query_service_unavailable(self, mock_requests, mock_wrapper):
        """Test when DBpedia service is unavailable"""
        mock_instance = Mock()
        mock_wrapper.return_value = mock_instance
        mock_instance.query.side_effect = Exception("503 Service Unavailable")
        
        # Also mock requests to fail
        mock_requests.get.side_effect = Exception("Request failed")
        
        service = SparqlService()
        result = service.execute_query("SELECT * WHERE { ?s ?p ?o }")
        assert result is None

    @patch('services.sparql_service.SPARQLWrapper')
    def test_execute_query_invalid_sparql_syntax(self, mock_wrapper):
        """Test execution with invalid SPARQL syntax"""
        mock_instance = Mock()
        mock_wrapper.return_value = mock_instance
        mock_instance.query.side_effect = Exception("Malformed query")
        
        service = SparqlService()
        result = service.execute_query("INVALID SPARQL QUERY")
        assert result is None

    def test_execute_local_query_no_graph_loaded(self):
        """Test local query when graph failed to load"""
        service = SparqlService()
        service.local_graph = None
        
        result = service.execute_local_query("SELECT * WHERE { ?s ?p ?o }")
        assert result is None

    @patch('services.sparql_service.IBADataParser')
    def test_execute_local_query_invalid_sparql(self, mock_parser):
        """Test local query with invalid SPARQL"""
        mock_instance = Mock()
        mock_instance.graph.query.side_effect = Exception("Invalid SPARQL syntax")
        mock_parser.return_value = mock_instance
        
        service = SparqlService("test.ttl")
        result = service.execute_local_query("INVALID QUERY")
        assert result is None

    @patch('services.sparql_service.IBADataParser')
    def test_execute_local_query_empty_result(self, mock_parser):
        """Test local query returning empty results"""
        mock_instance = Mock()
        # Mock query to return empty result
        mock_result = Mock()
        mock_result.vars = []
        type(mock_result).__iter__ = Mock(return_value=iter([]))
        mock_instance.graph.query.return_value = mock_result
        mock_parser.return_value = mock_instance
        
        service = SparqlService("test.ttl")
        result = service.execute_local_query("SELECT * WHERE { ?s ?p ?o }")
        
        # Should return None for empty results
        assert result is None


class TestCocktailServiceErrorHandling:
    """Test error handling in CocktailService"""

    @patch('services.cocktail_service.SparqlService')
    @patch('services.cocktail_service.IngredientService')
    def test_get_all_cocktails_sparql_failure(self, mock_ingredient, mock_sparql):
        """Test get_all_cocktails when SPARQL query fails"""
        mock_sparql_instance = Mock()
        mock_sparql_instance.execute_local_query.side_effect = Exception("SPARQL service error")
        mock_sparql.return_value = mock_sparql_instance
        
        service = CocktailService()
        cocktails = service.get_all_cocktails()
        
        assert cocktails == []

    @patch('services.cocktail_service.SparqlService')
    @patch('services.cocktail_service.IngredientService')
    def test_get_all_cocktails_malformed_results(self, mock_ingredient, mock_sparql):
        """Test get_all_cocktails with malformed SPARQL results"""
        mock_sparql_instance = Mock()
        mock_sparql.return_value = mock_sparql_instance
        
        # Mock malformed results
        mock_sparql_instance.execute_local_query.return_value = {
            "results": {
                "bindings": [
                    {
                        "cocktail": {"value": "http://example.com/cocktail1"},
                        # Missing required 'name' field
                    }
                ]
            }
        }
        
        service = CocktailService()
        
        cocktails = service.get_all_cocktails()
        
        # Should handle missing fields gracefully - creates cocktail with "Unknown Cocktail" name
        assert len(cocktails) == 1
        assert cocktails[0].name == "Unknown Cocktail"

    @patch('services.cocktail_service.SparqlService')
    @patch('services.cocktail_service.IngredientService')
    def test_parse_cocktail_from_graph_no_graph(self, mock_ingredient, mock_sparql):
        """Test parsing cocktail when graph is None"""
        mock_sparql_instance = Mock()
        mock_sparql.return_value = mock_sparql_instance
        
        service = CocktailService()
        service.graph = None
        
        result = service._parse_cocktail_from_graph(URIRef("http://example.com/cocktail"))
        assert result is None

    @patch('services.cocktail_service.SparqlService')
    @patch('services.cocktail_service.IngredientService')
    def test_get_feasible_cocktails_inventory_service_failure(self, mock_ingredient, mock_sparql):
        """Test get_feasible_cocktails when inventory service fails"""
        mock_sparql_instance = Mock()
        mock_sparql.return_value = mock_sparql_instance
        
        mock_ingredient_instance = Mock()
        mock_ingredient_instance.get_inventory.side_effect = Exception("Inventory service error")
        mock_ingredient.return_value = mock_ingredient_instance
        
        service = CocktailService()
        service.get_all_cocktails = Mock(return_value=[])
        
        # Should propagate the exception
        with pytest.raises(Exception, match="Inventory service error"):
            service.get_feasible_cocktails("user1")

    @patch('services.cocktail_service.SparqlService')
    @patch('services.cocktail_service.IngredientService')
    def test_get_feasible_cocktails_none_ingredients(self, mock_ingredient, mock_sparql):
        """Test get_feasible_cocktails with cocktails having None ingredients"""
        mock_sparql_instance = Mock()
        mock_sparql.return_value = mock_sparql_instance
        
        mock_ingredient_instance = Mock()
        mock_ingredient_instance.get_inventory.return_value = ["Rum"]
        mock_ingredient.return_value = mock_ingredient_instance
        
        service = CocktailService()
        
        mock_cocktail = Mock()
        mock_cocktail.ingredients = None
        service.get_all_cocktails = Mock(return_value=[mock_cocktail])
        
        feasible = service.get_feasible_cocktails("user1")
        assert feasible == []

    @patch('services.cocktail_service.SparqlService')
    @patch('services.cocktail_service.IngredientService')
    def test_get_similar_cocktails_target_not_found(self, mock_ingredient, mock_sparql):
        """Test get_similar_cocktails with non-existent target"""
        mock_sparql_instance = Mock()
        mock_sparql.return_value = mock_sparql_instance
        
        service = CocktailService()
        
        mock_cocktail = Mock()
        mock_cocktail.id = "different_id"
        service.get_all_cocktails = Mock(return_value=[mock_cocktail])
        
        results = service.get_similar_cocktails("nonexistent_id")
        assert results == []

    @patch('services.cocktail_service.SparqlService')
    @patch('services.cocktail_service.IngredientService')
    def test_get_same_vibe_cocktails_graph_service_failure(self, mock_ingredient, mock_sparql):
        """Test get_same_vibe_cocktails when GraphService fails"""
        mock_sparql_instance = Mock()
        mock_sparql.return_value = mock_sparql_instance
        
        service = CocktailService()
        
        mock_cocktail = Mock()
        mock_cocktail.id = "target_id"
        mock_cocktail.name = "Mojito"
        service.get_all_cocktails = Mock(return_value=[mock_cocktail])
        
        # Mock the GraphService to fail - patch the actual module
        with patch('services.graph_service.GraphService') as MockGraphService:
            mock_graph_service_instance = Mock()
            MockGraphService.return_value = mock_graph_service_instance
            mock_graph_service_instance.build_graph.side_effect = Exception("Graph build failed")
            
            # Should handle gracefully and return empty list
            results = service.get_same_vibe_cocktails("target_id")
            assert results == []

    @patch('services.cocktail_service.SparqlService')
    @patch('services.cocktail_service.IngredientService')
    def test_parse_ingredient_names_edge_cases(self, mock_ingredient, mock_sparql):
        """Test _parse_ingredient_names with edge cases"""
        mock_sparql_instance = Mock()
        mock_sparql.return_value = mock_sparql_instance
        
        service = CocktailService()
        
        # Empty string
        assert service._parse_ingredient_names("") == []
        
        # None
        assert service._parse_ingredient_names(None) == []
        
        # No bullets
        assert service._parse_ingredient_names("Just text") == []
        
        # Mixed bullets
        assert service._parse_ingredient_names("* Rum\n• Vodka\n- Gin") == ["Rum", "Vodka", "Gin"]
        
        # Special characters
        assert service._parse_ingredient_names("* 45 ml White Rum (Aged)") == ["White Rum (Aged)"]


class TestIngredientServiceErrorHandling:
    """Test error handling in IngredientService"""

    @patch('services.ingredient_service.get_local_ingredients')
    @patch('services.ingredient_service.SparqlService')
    def test_get_all_ingredients_local_query_failure(self, mock_sparql, mock_get_local):
        """Test get_all_ingredients when local query fails"""
        mock_sparql_instance = Mock()
        mock_sparql.return_value = mock_sparql_instance
        
        # Local parser fails
        mock_get_local.side_effect = Exception("Local query failed")
        # DBpedia succeeds but returns empty
        mock_sparql_instance.execute_query.return_value = {"results": {"bindings": []}}
        
        service = IngredientService()
        ingredients = service.get_all_ingredients()
        
        # Should return empty list, not crash
        assert ingredients == []

    @patch('services.ingredient_service.get_local_ingredients')
    @patch('services.ingredient_service.SparqlService')
    def test_get_all_ingredients_dbpedia_failure(self, mock_sparql, mock_get_local):
        """Test get_all_ingredients when DBpedia query fails"""
        mock_sparql_instance = Mock()
        mock_sparql.return_value = mock_sparql_instance
        
        # Local parser succeeds but returns empty
        mock_get_local.return_value = []
        # DBpedia query fails
        mock_sparql_instance.execute_query.side_effect = Exception("DBpedia unavailable")
        
        service = IngredientService()
        ingredients = service.get_all_ingredients()
        
        # Should return empty list, not crash
        assert ingredients == []

    @patch('services.ingredient_service.SparqlService')
    def test_search_ingredients_network_error(self, mock_sparql):
        """Test search_ingredients with network error"""
        mock_sparql_instance = Mock()
        mock_sparql.return_value = mock_sparql_instance
        mock_sparql_instance.execute_query.side_effect = Exception("Network error")
        
        service = IngredientService()
        ingredients = service.search_ingredients("vodka")
        
        # Should return empty list on error
        assert ingredients == []

    @patch('services.ingredient_service.SparqlService')
    def test_search_ingredients_empty_results(self, mock_sparql):
        """Test search_ingredients with no results"""
        mock_sparql_instance = Mock()
        mock_sparql.return_value = mock_sparql_instance
        mock_sparql_instance.execute_query.return_value = {"results": {"bindings": []}}
        
        service = IngredientService()
        ingredients = service.search_ingredients("nonexistent")
        
        assert ingredients == []


class TestGraphServiceErrorHandling:
    """Test error handling in GraphService"""

    @patch('services.graph_service.CocktailService')
    @patch('services.graph_service.IngredientService')
    def test_build_graph_cocktail_service_failure(self, mock_ingredient, mock_cocktail):
        """Test build_graph when CocktailService fails"""
        mock_cocktail_instance = Mock()
        mock_cocktail_instance.get_all_cocktails.side_effect = Exception("Cocktail service error")
        mock_cocktail.return_value = mock_cocktail_instance
        
        service = GraphService()
        
        with pytest.raises(Exception, match="Failed to build graph"):
            service.build_graph()

    @patch('services.graph_service.CocktailService')
    @patch('services.graph_service.IngredientService')
    def test_build_graph_ingredient_service_failure(self, mock_ingredient, mock_cocktail):
        """Test build_graph when IngredientService fails"""
        mock_cocktail_instance = Mock()
        mock_cocktail_instance.get_all_cocktails.return_value = []
        mock_cocktail.return_value = mock_cocktail_instance
        
        mock_ingredient_instance = Mock()
        mock_ingredient_instance.get_all_ingredients.side_effect = Exception("Ingredient service error")
        mock_ingredient.return_value = mock_ingredient_instance
        
        service = GraphService()
        
        with pytest.raises(Exception, match="Failed to build graph"):
            service.build_graph()

    @patch('services.graph_service.CocktailService')
    @patch('services.graph_service.IngredientService')
    def test_build_graph_empty_data(self, mock_ingredient, mock_cocktail):
        """Test build_graph with completely empty data"""
        mock_cocktail_instance = Mock()
        mock_cocktail_instance.get_all_cocktails.return_value = []
        mock_cocktail.return_value = mock_cocktail_instance
        
        mock_ingredient_instance = Mock()
        mock_ingredient_instance.get_all_ingredients.return_value = []
        mock_ingredient.return_value = mock_ingredient_instance
        
        service = GraphService()
        graph = service.build_graph()
        
        assert len(graph['nodes']) == 0
        assert len(graph['edges']) == 0

    @patch('services.graph_service.CocktailService')
    @patch('services.graph_service.IngredientService')
    def test_build_graph_cocktail_with_none_parsed_ingredients(self, mock_ingredient, mock_cocktail):
        """Test build_graph with cocktail having None parsed_ingredients"""
        mock_cocktail_instance = Mock()
        cocktail = Cocktail(
            uri="http://example.com/cocktail", id="cocktail",
            name="Mojito",
            parsed_ingredients=None
        )
        mock_cocktail_instance.get_all_cocktails.return_value = [cocktail]
        mock_cocktail.return_value = mock_cocktail_instance
        
        mock_ingredient_instance = Mock()
        mock_ingredient_instance.get_all_ingredients.return_value = []
        mock_ingredient.return_value = mock_ingredient_instance
        
        service = GraphService()
        graph = service.build_graph()
        
        # Should have cocktail node but no edges
        assert len(graph['nodes']) == 1
        assert len(graph['edges']) == 0

    @patch('services.graph_service.CocktailService')
    @patch('services.graph_service.IngredientService')
    def test_analyze_graph_build_failure(self, mock_ingredient, mock_cocktail):
        """Test analyze_graph when graph data is invalid"""
        mock_cocktail_instance = Mock()
        mock_cocktail_instance.get_all_cocktails.return_value = []
        mock_cocktail.return_value = mock_cocktail_instance
        
        mock_ingredient_instance = Mock()
        mock_ingredient_instance.get_all_ingredients.return_value = []
        mock_ingredient.return_value = mock_ingredient_instance
        
        service = GraphService()
        
        # Mock invalid graph data
        result = service.analyze_graph(None)
        assert result is None

    @patch('services.graph_service.CocktailService')
    @patch('services.graph_service.IngredientService')
    def test_analyze_graph_community_detection_failure(self, mock_ingredient, mock_cocktail):
        """Test analyze_graph when community detection fails"""
        mock_cocktail_instance = Mock()
        cocktail = Cocktail(
            uri="http://example.com/cocktail", id="cocktail",
            name="Mojito",
            parsed_ingredients=["Rum"]
        )
        mock_cocktail_instance.get_all_cocktails.return_value = [cocktail]
        mock_cocktail.return_value = mock_cocktail_instance
        
        mock_ingredient_instance = Mock()
        ingredient = Ingredient(id="http://example.com/rum", name="Rum")
        mock_ingredient_instance.get_all_ingredients.return_value = [ingredient]
        mock_ingredient.return_value = mock_ingredient_instance
        
        service = GraphService()
        
        # Build valid graph first
        graph_data = service.build_graph()
        
        # Mock networkx to fail during community detection
        with patch('services.graph_service.nx') as mock_nx:
            mock_graph = Mock()
            mock_nx.Graph.return_value = mock_graph
            mock_graph.nodes.return_value = {"Mojito": {"type": "cocktail"}, "Rum": {"type": "ingredient"}}
            mock_graph.edges.return_value = [("Mojito", "Rum")]
            mock_nx.degree_centrality.return_value = {"Mojito": 1.0, "Rum": 1.0}
            mock_nx.betweenness_centrality.return_value = {"Mojito": 0.0, "Rum": 0.0}
            mock_nx.closeness_centrality.return_value = {"Mojito": 1.0, "Rum": 1.0}
            mock_nx.algorithms.community.louvain_communities.side_effect = Exception("Community detection failed")
            
            result = service.analyze_graph(graph_data)
            assert result is None

    @patch('services.graph_service.CocktailService')
    @patch('services.graph_service.IngredientService')
    def test_analyze_graph_empty_graph(self, mock_ingredient, mock_cocktail):
        """Test analyze_graph with empty graph"""
        mock_cocktail_instance = Mock()
        mock_cocktail_instance.get_all_cocktails.return_value = []
        mock_cocktail.return_value = mock_cocktail_instance
        
        mock_ingredient_instance = Mock()
        mock_ingredient_instance.get_all_ingredients.return_value = []
        mock_ingredient.return_value = mock_ingredient_instance
        
        service = GraphService()
        graph_data = service.build_graph()
        result = service.analyze_graph(graph_data)
        
        assert result['node_count'] == 0
        assert result['edge_count'] == 0

    @patch('services.graph_service.CocktailService')
    @patch('services.graph_service.IngredientService')
    def test_visualize_graph_build_failure(self, mock_ingredient, mock_cocktail):
        """Test visualize_graph when graph data is invalid"""
        service = GraphService()
        
        result = service.visualize_graph(None)
        assert result is None

    @patch('services.graph_service.CocktailService')
    @patch('services.graph_service.IngredientService')
    def test_analyze_disjoint_components_build_failure(self, mock_ingredient, mock_cocktail):
        """Test analyze_disjoint_components when graph data is invalid"""
        service = GraphService()
        
        result = service.analyze_disjoint_components(None)
        assert result is None

    @patch('services.graph_service.CocktailService')
    @patch('services.graph_service.IngredientService')
    def test_export_graph_build_failure(self, mock_ingredient, mock_cocktail):
        """Test export_graph when graph data is invalid"""
        service = GraphService()
        
        result = service.export_graph(None)
        assert result is None

    @patch('services.graph_service.CocktailService')
    @patch('services.graph_service.IngredientService')
    def test_export_graph_networkx_failure(self, mock_ingredient, mock_cocktail):
        """Test export_graph when networkx write_gexf fails"""
        mock_cocktail_instance = Mock()
        cocktail = Cocktail(
            uri="http://example.com/cocktail", id="cocktail",
            name="Mojito",
            parsed_ingredients=["Rum"]
        )
        mock_cocktail_instance.get_all_cocktails.return_value = [cocktail]
        mock_cocktail.return_value = mock_cocktail_instance
        
        mock_ingredient_instance = Mock()
        ingredient = Ingredient(id="http://example.com/rum", name="Rum")
        mock_ingredient_instance.get_all_ingredients.return_value = [ingredient]
        mock_ingredient.return_value = mock_ingredient_instance
        
        service = GraphService()
        
        graph_data = service.build_graph()
        
        # Mock networkx to fail during export
        with patch('services.graph_service.nx') as mock_nx:
            mock_graph = Mock()
            mock_nx.Graph.return_value = mock_graph
            mock_graph.nodes.return_value = {"Mojito": {"type": "cocktail"}, "Rum": {"type": "ingredient"}}
            mock_graph.edges.return_value = [("Mojito", "Rum")]
            mock_nx.write_gexf.side_effect = Exception("Export failed")
            
            result = service.export_graph(graph_data)
            assert result is None


class TestPlannerServiceErrorHandling:
    """Test error handling in PlannerService"""

    @patch('services.planner_service.CocktailService')
    @patch('services.planner_service.IngredientService')
    def test_init_cocktail_service_failure(self, mock_ingredient, mock_cocktail):
        """Test initialization when CocktailService fails"""
        mock_cocktail_instance = Mock()
        mock_cocktail_instance.get_all_cocktails.side_effect = Exception("Cocktail service error")
        mock_cocktail.return_value = mock_cocktail_instance
        
        with pytest.raises(Exception):
            PlannerService()

    @patch('services.planner_service.CocktailService')
    @patch('services.planner_service.IngredientService')
    def test_init_empty_cocktails(self, mock_ingredient, mock_cocktail):
        """Test initialization with no cocktails"""
        mock_cocktail_instance = Mock()
        mock_cocktail_instance.get_all_cocktails.return_value = []
        mock_cocktail.return_value = mock_cocktail_instance
        
        service = PlannerService()
        assert service.cocktail_ingredients == {}

    @patch('services.planner_service.CocktailService')
    @patch('services.planner_service.IngredientService')
    def test_init_cocktail_with_none_parsed_ingredients(self, mock_ingredient, mock_cocktail):
        """Test initialization with cocktail having None parsed_ingredients"""
        mock_cocktail_instance = Mock()
        cocktail = Cocktail(
            uri="http://example.com/cocktail", id="cocktail",
            name="Mojito",
            parsed_ingredients=None
        )
        mock_cocktail_instance.get_all_cocktails.return_value = [cocktail]
        mock_cocktail.return_value = mock_cocktail_instance
        
        service = PlannerService()
        assert service.cocktail_ingredients["Mojito"] == set()

    @patch('services.planner_service.CocktailService')
    @patch('services.planner_service.IngredientService')
    def test_optimize_playlist_mode_empty_list(self, mock_ingredient, mock_cocktail):
        """Test optimize_playlist_mode with empty cocktail list"""
        mock_cocktail_instance = Mock()
        mock_cocktail_instance.get_all_cocktails.return_value = []
        mock_cocktail.return_value = mock_cocktail_instance
        
        service = PlannerService()
        result = service.optimize_playlist_mode([])
        
        assert result == {'selected_ingredients': [], 'covered_cocktails': []}

    @patch('services.planner_service.CocktailService')
    @patch('services.planner_service.IngredientService')
    def test_optimize_playlist_mode_nonexistent_cocktails(self, mock_ingredient, mock_cocktail):
        """Test optimize_playlist_mode with non-existent cocktail names"""
        mock_cocktail_instance = Mock()
        cocktail = Cocktail(
            uri="http://example.com/cocktail", id="cocktail",
            name="Mojito",
            parsed_ingredients=["Rum", "Lime"]
        )
        mock_cocktail_instance.get_all_cocktails.return_value = [cocktail]
        mock_cocktail.return_value = mock_cocktail_instance
        
        service = PlannerService()
        result = service.optimize_playlist_mode(["Nonexistent1", "Nonexistent2"])
        
        assert result == {'selected_ingredients': [], 'covered_cocktails': []}

    @patch('services.planner_service.CocktailService')
    @patch('services.planner_service.IngredientService')
    def test_optimize_playlist_mode_partial_match(self, mock_ingredient, mock_cocktail):
        """Test optimize_playlist_mode with some cocktails existing and some not"""
        mock_cocktail_instance = Mock()
        cocktail1 = Cocktail(
            uri="http://example.com/cocktail1", id="cocktail1",
            name="Mojito",
            parsed_ingredients=["Rum", "Lime"]
        )
        cocktail2 = Cocktail(
            uri="http://example.com/cocktail2", id="cocktail2",
            name="Martini",
            parsed_ingredients=["Gin", "Vermouth"]
        )
        mock_cocktail_instance.get_all_cocktails.return_value = [cocktail1, cocktail2]
        mock_cocktail.return_value = mock_cocktail_instance
        
        service = PlannerService()
        result = service.optimize_playlist_mode(["Mojito", "Nonexistent"])
        
        # Should only cover existing cocktail
        assert len(result['covered_cocktails']) == 1
        assert "Mojito" in result['covered_cocktails']


class TestCrossServiceErrorHandling:
    """Test error scenarios that span multiple services"""

    @patch('services.cocktail_service.SparqlService')
    @patch('services.cocktail_service.IngredientService')
    def test_cocktail_service_chain_failure(self, mock_ingredient, mock_sparql):
        """Test when CocktailService depends on failing SparqlService"""
        mock_sparql_instance = Mock()
        mock_sparql.return_value = mock_sparql_instance
        
        # SparqlService fails during query
        mock_sparql_instance.execute_local_query.side_effect = Exception("SPARQL chain failure")
        
        service = CocktailService()
        
        # All methods that depend on SPARQL should handle gracefully
        assert service.get_all_cocktails() == []
        assert service.search_cocktails("test") == []
        
        # Methods that need cocktails should also handle empty results
        mock_ingredient_instance = Mock()
        mock_ingredient_instance.get_inventory.return_value = ["Rum"]
        mock_ingredient.return_value = mock_ingredient_instance
        
        assert service.get_feasible_cocktails("user1") == []
        assert service.get_almost_feasible_cocktails("user1") == []

    @patch('services.graph_service.CocktailService')
    @patch('services.graph_service.IngredientService')
    def test_graph_service_chain_failure(self, mock_ingredient, mock_cocktail):
        """Test when GraphService depends on failing services"""
        mock_cocktail_instance = Mock()
        mock_cocktail_instance.get_all_cocktails.side_effect = Exception("Cocktail service unavailable")
        mock_cocktail.return_value = mock_cocktail_instance
        
        mock_ingredient_instance = Mock()
        mock_ingredient.return_value = mock_ingredient_instance
        
        service = GraphService()
        
        # All methods should fail with appropriate error messages
        with pytest.raises(Exception, match="Failed to build graph"):
            service.build_graph()

    @patch('services.planner_service.CocktailService')
    @patch('services.planner_service.IngredientService')
    def test_planner_service_chain_failure(self, mock_ingredient, mock_cocktail):
        """Test when PlannerService depends on failing CocktailService"""
        mock_cocktail_instance = Mock()
        mock_cocktail_instance.get_all_cocktails.side_effect = Exception("Cocktail service unavailable")
        mock_cocktail.return_value = mock_cocktail_instance
        
        # Should fail during initialization
        with pytest.raises(Exception):
            PlannerService()

    @patch('services.ingredient_service.get_local_ingredients')
    @patch('services.ingredient_service.SparqlService')
    def test_ingredient_service_fallback_to_dbpedia(self, mock_sparql, mock_get_local):
        """Test IngredientService fallback when local queries fail"""
        mock_sparql_instance = Mock()
        mock_sparql.return_value = mock_sparql_instance
        
        # Local parser fails
        mock_get_local.side_effect = Exception("Local unavailable")
        
        # DBpedia works
        mock_sparql_instance.execute_query.return_value = {
            "results": {
                "bindings": [
                    {"id": {"value": "http://dbpedia.org/resource/Vodka"}, "name": {"value": "Vodka"}}
                ]
            }
        }
        
        service = IngredientService()
        ingredients = service.get_all_ingredients()
        
        # Should still get ingredients from DBpedia
        assert len(ingredients) == 1
        assert ingredients[0].name == "Vodka"

    @patch('services.cocktail_service.SparqlService')
    @patch('services.cocktail_service.IngredientService')
    def test_cocktail_service_partial_data_recovery(self, mock_ingredient, mock_sparql):
        """Test CocktailService recovery with partial data"""
        mock_sparql_instance = Mock()
        mock_sparql.return_value = mock_sparql_instance
        
        # First query fails, second succeeds
        mock_sparql_instance.execute_local_query.side_effect = [
            Exception("First query fails"),
            {"results": {"bindings": [{"cocktail": {"value": "http://example.com/cocktail"}}]}}
        ]
        
        service = CocktailService()
        
        # First call fails
        assert service.get_all_cocktails() == []
        
        # Second call succeeds (if called again)
        mock_sparql_instance.execute_local_query.side_effect = [
            {"results": {"bindings": [{"cocktail": {"value": "http://example.com/cocktail"}, "name": {"value": "Test"}}]}}
        ]
        
        cocktails = service.get_all_cocktails()
        assert len(cocktails) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])