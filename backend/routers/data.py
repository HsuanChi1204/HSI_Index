from fastapi import APIRouter, HTTPException, Depends
from supabase import create_client, Client
import os
from typing import List, Optional

router = APIRouter()

def get_supabase() -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        raise HTTPException(status_code=500, detail="Supabase credentials not configured")
    return create_client(url, key)

@router.get("/stats/summary")
async def get_summary_stats(supabase: Client = Depends(get_supabase)):
    """Get overall summary statistics"""
    try:
        # This is a simplified example. In production, you might want to cache this or use a materialized view.
        crimes_response = supabase.table("crimes").select("count", count="exact").execute()
        zillow_response = supabase.table("zillow_data").select("count", count="exact").execute()
        
        return {
            "total_crimes": crimes_response.count,
            "total_zillow_regions": zillow_response.count,
            "timestamp": "2025-12-06" # Dynamic in real app
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/zipcode/{zipcode}")
async def get_zipcode_data(zipcode: str, supabase: Client = Depends(get_supabase)):
    """Get data for a specific zipcode"""
    try:
        # Fetch crime stats
        crimes = supabase.table("crimes").select("*").eq("zip_code", zipcode).execute()
        
        # Fetch zillow data
        zillow = supabase.table("zillow_data").select("*").eq("zip_code", zipcode).execute()
        
        return {
            "zip_code": zipcode,
            "crime_count": len(crimes.data),
            "zillow_data": zillow.data[0] if zillow.data else None,
            "crimes": crimes.data[:10] # Return top 10 recent crimes
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
