import requests

DBPEDIA_ENDPOINT = "http://dbpedia.org/sparql"

def query_dbpedia(query: str):
    headers = {
        "Accept": "application/sparql-results+json"
    }
    
    response = requests.get(DBPEDIA_ENDPOINT, params={"query": query}, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to query DBpedia: {response.status_code}")