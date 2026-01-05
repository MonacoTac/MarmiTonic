from fastapi import APIRouter, HTTPException
from ..models.sparql_query import SparqlQuery
from ..services.sparql_service import SparqlService

router = APIRouter()

@router.post("/query")
def execute_sparql_query(query: SparqlQuery):
    try:
        results = SparqlService().execute_query(query.query)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))