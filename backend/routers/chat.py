from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from supabase import create_client, Client
import os
import google.generativeai as genai
from typing import List, Optional, Dict, Any
from google.generativeai.types import FunctionDeclaration, Tool

router = APIRouter()

class ClientContext(BaseModel):
    current_zip: Optional[str] = None
    weights: Optional[Dict[str, float]] = None

class ChatRequest(BaseModel):
    query: str
    history: Optional[List[dict]] = []
    client_context: Optional[ClientContext] = None

class ChatResponse(BaseModel):
    response: str
    data_sources: Optional[List[str]] = []

def get_supabase() -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        raise HTTPException(status_code=500, detail="Supabase credentials not configured")
    return create_client(url, key)

# --- Tool Definitions ---

def get_zipcode_data(zipcode: str):
    """
    Fetches comprehensive crime and real estate data for a specific DC ZIP code.
    Use this tool when the user asks about a specific area, safety, prices, or trends in a ZIP code.
    
    Args:
        zipcode: The 5-digit ZIP code (e.g., '20001').
    """
    print(f"🛠️ Tool Called: get_zipcode_data({zipcode})")
    supabase = get_supabase()
    
    data = {}
    
    # 1. Summary Stats
    try:
        stats = supabase.table("zipcode_stats").select("*").eq("zip_code", zipcode).execute()
        if stats.data:
            data["summary"] = stats.data[0]
    except Exception as e:
        print(f"Error fetching stats: {e}")

    # 2. Recent Crimes
    try:
        crimes = supabase.table("crimes").select("offense, report_dat, block").eq("zip_code", zipcode).order("report_dat", desc=True).limit(5).execute()
        if crimes.data:
            data["recent_crimes"] = crimes.data
    except Exception as e:
        print(f"Error fetching crimes: {e}")

    # 3. Housing Trends
    try:
        history = supabase.table("house_ts").select("*").eq("zip_code", zipcode).order("date", desc=True).limit(5).execute()
        if history.data:
            data["housing_trends"] = history.data
    except Exception as e:
        print(f"Error fetching history: {e}")
        
    if not data:
        return {"error": f"No data found for ZIP {zipcode}"}
        
    return data

def search_knowledge_base(query: str):
    """
    Searches the academic paper and knowledge base for concepts, formulas, and ethical guidelines.
    Use this tool when the user asks about:
    - HCI (Human-Context Index) definition or formula.
    - Methodology, ethics, or design principles.
    - "Why" questions related to the system's logic.
    
    Args:
        query: The search query string (e.g., "HCI formula", "ethics of crime data").
    """
    print(f"🛠️ Tool Called: search_knowledge_base({query})")
    supabase = get_supabase()
    
    try:
        # 1. Generate Embedding for query
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=query,
            task_type="retrieval_query"
        )
        query_embedding = result['embedding']
        
        # 2. Call RPC function
        response = supabase.rpc(
            'match_documents',
            {
                'query_embedding': query_embedding,
                'match_threshold': 0.5, # Adjust threshold as needed
                'match_count': 3
            }
        ).execute()
        
        if response.data:
            return {"documents": response.data}
        else:
            return {"message": "No relevant documents found in knowledge base."}
            
    except Exception as e:
        print(f"Error searching knowledge base: {e}")
        return {"error": str(e)}

# --- Chat Endpoint ---

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, supabase: Client = Depends(get_supabase)):
    """
    Context-Aware Chat endpoint using Gemini Function Calling.
    """
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        return ChatResponse(response="Error: GEMINI_API_KEY not configured.")

    genai.configure(api_key=gemini_api_key)

    # 1. Prepare Context String
    context_str = ""
    if request.client_context:
        if request.client_context.current_zip:
            context_str += f"User is currently viewing ZIP Code: {request.client_context.current_zip}.\n"
        if request.client_context.weights:
            w1 = request.client_context.weights.get("growth_w1", 0.5)
            w2 = request.client_context.weights.get("safety_w2", 0.5)
            context_str += f"User Preferences: Growth Weight (w1)={w1}, Safety Weight (w2)={w2}.\n"
            if w1 > w2:
                context_str += "User prioritizes Investment Potential over Safety.\n"
            elif w2 > w1:
                context_str += "User prioritizes Safety over Investment Potential.\n"

    # 2. System Prompt
    system_prompt = f"""You are an expert real estate and safety analyst for Washington DC.
    Your goal is to provide insightful, opinionated, and helpful advice.
    
    **Current Context:**
    {context_str}
    
    **Tools:**
    1. `get_zipcode_data(zipcode)`: For specific area stats, prices, crime.
    2. `search_knowledge_base(query)`: For explaining concepts, formulas (HCI), or ethics.
    
    **Guidelines:**
    1.  **Be Analytical**: Interpret the numbers.
    2.  **HCI Logic**: Use `search_knowledge_base` if you need to explain how HCI is calculated or the ethical stance (e.g., why we don't say "unsafe").
    3.  **Tone**: Professional, conversational, direct.
    """

    # 3. Initialize Model with Tools
    tools = [get_zipcode_data, search_knowledge_base]
    
    models_to_try = [
        "gemini-2.0-flash-exp",
        "gemini-1.5-flash-latest",
        "gemini-1.5-pro-latest"
    ]

    last_error = None

    # 4. Construct History
    chat_history = []
    for msg in request.history[-5:]:
        role = "user" if msg.get("role") == "user" else "model"
        chat_history.append({"role": role, "parts": [msg.get("content", "")]})

    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(model_name, tools=tools, system_instruction=system_prompt)
            
            # Enable automatic function calling
            chat = model.start_chat(history=chat_history, enable_automatic_function_calling=True)
            
            response = chat.send_message(request.query)
            
            return ChatResponse(response=response.text)

        except Exception as e:
            last_error = e
            print(f"Model {model_name} failed: {e}")
            continue

    return ChatResponse(response=f"Error: All models failed. Last error: {str(last_error)}")
