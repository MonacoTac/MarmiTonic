from pydantic import BaseModel

class SparqlQuery(BaseModel):
    query: str