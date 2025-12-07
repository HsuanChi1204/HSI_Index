import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv("backend/.env")

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

if not url or not key:
    print("Error: Supabase credentials not found.")
    exit(1)

supabase = create_client(url, key)

target_zip = "20001"

print(f"Checking data for ZIP: {target_zip}")

# 1. Check zipcode_stats
try:
    response = supabase.table("zipcode_stats").select("*").eq("zip_code", target_zip).execute()
    print(f"\n[zipcode_stats] Count: {len(response.data)}")
    if response.data:
        print(f"Sample: {response.data[0]}")
    else:
        print("[zipcode_stats] EMPTY")
except Exception as e:
    print(f"[zipcode_stats] Error: {e}")

# 2. Check house_ts
try:
    response = supabase.table("house_ts").select("*").eq("zip_code", target_zip).limit(5).execute()
    print(f"\n[house_ts] Count (limit 5): {len(response.data)}")
    if response.data:
        print(f"Sample: {response.data[0]}")
except Exception as e:
    print(f"[house_ts] Error: {e}")

# 3. Check crimes
try:
    response = supabase.table("crimes").select("*").eq("zip_code", target_zip).limit(5).execute()
    print(f"\n[crimes] Count (limit 5): {len(response.data)}")
    if response.data:
        print(f"Sample: {response.data[0]}")
except Exception as e:
    print(f"[crimes] Error: {e}")
