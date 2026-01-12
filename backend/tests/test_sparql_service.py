import pytest
from unittest.mock import Mock, patch
from backend.services.sparql_service import SparqlService


@pytest.fixture
def sparql_service():
    service = SparqlService()
    return service


class TestSparqlService:

    def test_init(self, sparql_service):
        assert sparql_service.endpoint == "https://dbpedia.org/sparql"
        assert sparql_service.local_graph_path == "data/data.ttl"
        assert sparql_service.local_endpoint == "http://localhost:3030/marmitonic"

    def test_execute_query_success(self, sparql_service):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": {"bindings": [{"test": {"value": "test_value"}}]}}

        with patch('backend.services.sparql_service.requests.get', return_value=mock_response) as mock_get:
            result = sparql_service.execute_query("SELECT * WHERE { ?s ?p ?o }")

            mock_get.assert_called_once()
            assert "SELECT" in mock_get.call_args[0][0]
            assert "test_value" in str(result)

    def test_execute_query_http_error(self, sparql_service):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = Exception("HTTP 500 Error")

        with patch('backend.services.sparql_service.requests.get', return_value=mock_response):
            result = sparql_service.execute_query("SELECT * WHERE { ?s ?p ?o }")

            assert result is None

    def test_execute_query_timeout(self, sparql_service):
        import requests
        with patch('backend.services.sparql_service.requests.get', side_effect=requests.Timeout()):
            result = sparql_service.execute_query("SELECT * WHERE { ?s ?p ?o }")
            assert result is None

    def test_execute_query_invalid_json(self, sparql_service):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")

        with patch('backend.services.sparql_service.requests.get', return_value=mock_response):
            result = sparql_service.execute_query("SELECT * WHERE { ?s ?p ?o }")
            assert result is None

    def test_execute_local_query_success(self, sparql_service):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": {"bindings": [{"test": {"value": "local_value"}}]}}

        with patch('backend.services.sparql_service.requests.get', return_value=mock_response) as mock_get:
            result = sparql_service.execute_local_query("SELECT * WHERE { ?s ?p ?o }")

            mock_get.assert_called_once()
            assert sparql_service.local_endpoint in mock_get.call_args[0][0]
            assert "local_value" in str(result)

    def test_execute_local_query_connection_error(self, sparql_service):
        import requests
        with patch('backend.services.sparql_service.requests.get', side_effect=requests.ConnectionError()):
            result = sparql_service.execute_local_query("SELECT * WHERE { ?s ?p ?o }")
            assert result is None

    def test_execute_local_query_empty_result(self, sparql_service):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": {"bindings": []}}

        with patch('backend.services.sparql_service.requests.get', return_value=mock_response):
            result = sparql_service.execute_local_query("SELECT * WHERE { ?s ?p ?o }")
            assert result == {"results": {"bindings": []}}

    def test_build_query_empty_params(self, sparql_service):
        result = SparqlService._build_query("", "test_uri")
        assert "test_uri" in result
        assert "rdf:type" in result

    def test_build_query_with_params(self, sparql_service):
        params = ["rdfs:label", "rdfs:comment"]
        result = SparqlService._build_query("", "test_uri", additional_properties=params)
        assert "rdfs:label" in result
        assert "rdfs:comment" in result

    def test_build_query_ingredients(self, sparql_service):
        result = SparqlService._build_query("ingredients", "cocktail_uri")
        assert "cocktail:hasIngredient" in result or "cocktail_uri" in result

    def test_build_query_different_types(self, sparql_service):
        result_cocktail = SparqlService._build_query("cocktail", "uri")
        result_ingredient = SparqlService._build_query("ingredient", "uri")

        # Different queries should be different
        assert result_cocktail != result_ingredient

    def test_query_local_data_no_file(self, sparql_service):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": {"bindings": [{"cocktail": {"value": "http://example.com/c1"}}]}}

        with patch('backend.services.sparql_service.requests.get', return_value=mock_response):
            result = sparql_service.query_local_data("cocktails")

            assert "c1" in str(result)

    def test_query_local_data_with_params(self, sparql_service):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": {"bindings": []}}

        with patch('backend.services.sparql_service.requests.get', return_value=mock_response):
            result = sparql_service.query_local_data("cocktail", "http://example.com/c1", ["rdfs:label"])

            mock_response.json.assert_called_once()
            assert result == {"results": {"bindings": []}}

    def test_query_local_data_connection_error(self, sparql_service):
        import requests
        with patch('backend.services.sparql_service.requests.get', side_effect=requests.ConnectionError()):
            result = sparql_service.query_local_data("cocktails")
            assert result is None

    def test_query_local_data_invalid_json(self, sparql_service):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")

        with patch('backend.services.sparql_service.requests.get', return_value=mock_response):
            result = sparql_service.query_local_data("cocktails")
            assert result is None

    def test_query_local_data_http_error(self, sparql_service):
        mock_response = Mock()
        mock_response.status_code = 404

        with patch('backend.services.sparql_service.requests.get', return_value=mock_response):
            result = sparql_service.query_local_data("cocktails")
            assert result is None

    def test_get_all_cocktails_from_dbpedia(self, sparql_service):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": {
                "bindings": [
                    {"cocktail": {"value": "http://dbpedia.org/resource/Mojito"}},
                    {"cocktail": {"value": "http://dbpedia.org/resource/Martini"}}
                ]
            }
        }

        with patch('backend.services.sparql_service.requests.get', return_value=mock_response):
            result = sparql_service.get_all_cocktails_from_dbpedia()

            assert len(result) == 2
            assert "Mojito" in str(result)
            assert "Martini" in str(result)

    def test_get_all_cocktails_from_dbpedia_empty(self, sparql_service):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": {"bindings": []}}

        with patch('backend.services.sparql_service.requests.get', return_value=mock_response):
            result = sparql_service.get_all_cocktails_from_dbpedia()
            assert result == []

    def test_get_all_cocktails_from_dbpedia_error(self, sparql_service):
        import requests
        with patch('backend.services.sparql_service.requests.get', side_effect=requests.ConnectionError()):
            result = sparql_service.get_all_cocktails_from_dbpedia()
            assert result is None
