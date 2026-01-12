from SPARQLWrapper import SPARQLWrapper, JSON
from rdflib import Graph
from typing import Optional, Union
from ..utils.graph_loader import get_shared_graph

class SparqlService:
    def __init__(self, local_graph: Optional[Union[str, Graph]] = None):
        self.local_graph = None
        if isinstance(local_graph, Graph):
            self.local_graph = local_graph
        elif isinstance(local_graph, str):
            self.local_graph = Graph()
            try:
                self.local_graph.parse(local_graph, format="turtle")
            except Exception as e:
                print(f"Error loading local graph from {local_graph}: {e}")
                self.local_graph = None
        else:
            # Default to shared graph
            self.local_graph = get_shared_graph()

    def execute_query(self, query: str):
        """Execute SPARQL query on DBpedia"""
        sparql = SPARQLWrapper("https://dbpedia.org/sparql")

        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        return results

    def execute_local_query(self, query: str):
        """Execute SPARQL query on local RDF graph"""
        if not self.local_graph:
            raise ValueError("Local graph not loaded")

        results = self.local_graph.query(query)
        # Convert to similar format as SPARQLWrapper for consistency
        bindings = []
        for row in results:
            binding = {}
            for var in results.vars:
                value = row[var]
                if value is not None:
                    binding[str(var)] = {"value": str(value), "type": "uri" if hasattr(value, 'n3') and value.n3().startswith('<') else "literal"}
                else:
                    binding[str(var)] = {"value": None}
            bindings.append(binding)

        return {"results": {"bindings": bindings}}