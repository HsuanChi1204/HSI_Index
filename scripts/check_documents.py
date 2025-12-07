import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv("backend/.env")
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

response = supabase.table("documents").select("id, metadata").order("id").execute()

print(f"Total documents: {len(response.data)}")
for doc in response.data:
    source = doc['metadata'].get('source', 'Unknown')
    section = doc['metadata'].get('section', 'Unknown')
    print(f"ID: {doc['id']} | Source: {source} | Section: {section}")
