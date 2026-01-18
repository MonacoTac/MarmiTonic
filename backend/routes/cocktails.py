from fastapi import APIRouter, HTTPException, Query, Response
from typing import List
from ..services.cocktail_service import CocktailService
from ..services.similarity_service import SimilarityService

router = APIRouter()
similarity_service = SimilarityService()
cocktail_service = CocktailService()

@router.get("/")
async def get_cocktails(q: str = None):
    try:
        if q:
            return cocktail_service.search_cocktails(q)
        else:
            return cocktail_service.get_all_cocktails()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/feasible/{user_id}")
async def get_feasible_cocktails(user_id: str):
    try:
        return cocktail_service.get_feasible_cocktails(user_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid user_id or query failure: {str(e)}")

@router.get("/almost-feasible/{user_id}")
async def get_almost_feasible_cocktails(user_id: str):
    try:
        return cocktail_service.get_almost_feasible_cocktails(user_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid user_id or query failure: {str(e)}")

@router.get("/by-ingredients")
async def get_cocktails_by_ingredients(ingredients: List[str] = Query(..., description="List of ingredient names to search for")):
    try:
        return cocktail_service.get_cocktails_by_ingredients(ingredients)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/by-uris")
async def get_cocktails_by_uris(uris: List[str] = Query(..., description="List of ingredient URIs to search for")):
    try:
        return cocktail_service.get_cocktails_by_uris(uris)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# similarity endpoints
@router.get("/similar/{cocktail_id}")
async def get_similar_cocktails(cocktail_id: str, limit: int = Query(5, ge=1, le=20)):
    try:
        results = similarity_service.find_similar_cocktails(cocktail_id, top_k=limit)
        return {"cocktail_id": cocktail_id, "similar_cocktails": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error finding similar cocktails: {str(e)}")

@router.get("/search-semantic")
async def search_cocktails_semantic(query: str = Query(...), top_k: int = Query(5, ge=1, le=20)):
    try:
        results = similarity_service.find_similar_by_text(query, top_k=top_k)
        return {"query": query, "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in semantic search: {str(e)}")

@router.get("/similar-by-ingredients")
async def get_similar_by_ingredients(ingredients: List[str] = Query(...), top_k: int = Query(5, ge=1, le=20)):
    try:
        results = similarity_service.find_similar_by_ingredients(ingredients, top_k=top_k)
        return {"ingredients": ingredients, "similar_cocktails": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error finding similar cocktails: {str(e)}")

@router.post("/build-index")
async def build_similarity_index(force_rebuild: bool = False, response: Response = None):
    try:
        similarity_service.build_index(force_rebuild=force_rebuild)
        return {"status": "success", "message": f"Index built with {len(similarity_service.cocktails)} cocktails"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error building index: {str(e)}")
    
@router.post("/create-clusters")
async def create_cocktail_clusters(n_clusters: int = Query(6, ge=2, le=20)):
    try:
        clusters = similarity_service.create_cocktails_clusters(n_clusters=n_clusters)
        # Convert dict to list for easier serialization
        clusters_list = [cluster.dict() for cluster in clusters.values()]
        return {"status": "success", "n_clusters": n_clusters, "clusters": clusters_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating clusters: {str(e)}")

@router.get("/random")
async def get_random_cocktail():
    """Get a random cocktail from the database"""
    try:
        import random
        cocktails = cocktail_service.get_all_cocktails()
        if not cocktails:
            raise HTTPException(status_code=404, detail="No cocktails found")
        return random.choice(cocktails)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting random cocktail: {str(e)}")

@router.get("/clusters")
async def get_cocktail_clusters(n_clusters: int = Query(6, ge=2, le=20), with_cocktails: bool = Query(True)):
    """Get vibe clusters with full cocktail details"""
    try:
        # Generate clusters
        clusters = similarity_service.create_cocktails_clusters(n_clusters=n_clusters)
        
        if not with_cocktails:
            # Just return cluster metadata
            return {"clusters": [cluster.dict() for cluster in clusters.values()]}
        
        # Enrich with full cocktail details
        all_cocktails = cocktail_service.get_all_cocktails()
        cocktails_dict = {c.id: c for c in all_cocktails}
        
        enriched_clusters = []
        for cluster in clusters.values():
            # Get full cocktail objects for this cluster
            cluster_cocktails = [cocktails_dict[cid] for cid in cluster.cocktail_ids if cid in cocktails_dict]
            
            enriched_clusters.append({
                "cluster_id": cluster.cluster_id,
                "title": cluster.title or f"Vibe {cluster.cluster_id + 1}",
                "cocktails": cluster_cocktails[:15],  # Limit to 15 cocktails per cluster for performance
                "total_count": len(cluster.cocktail_ids)
            })
        
        return {"clusters": enriched_clusters}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting clusters: {str(e)}")

@router.get("/same-vibe/{cocktail_id}")
async def get_same_vibe_cocktails(cocktail_id: str, limit: int = Query(10, ge=1, le=50)):
    """Get cocktails in the same graph community/cluster as the given cocktail"""
    try:
        return cocktail_service.get_same_vibe_cocktails(cocktail_id, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error finding same vibe cocktails: {str(e)}")

@router.get("/bridge")
async def get_bridge_cocktails(limit: int = Query(10, ge=1, le=50)):
    """Get bridge cocktails that connect different communities"""
    try:
        return cocktail_service.get_bridge_cocktails(limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting bridge cocktails: {str(e)}")
