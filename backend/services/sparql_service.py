from ..utils.dbpedia_client import query_dbpedia

class SparqlService:
    def __init__(self):
        pass
    
    def execute_query(self, query: str):
        results = query_dbpedia(query)
        return results