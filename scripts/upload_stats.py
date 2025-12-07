import json
import os
from supabase import create_client, Client
from dotenv import load_dotenv

def upload_stats():
    # Load env
    load_dotenv()
    if not os.getenv('SUPABASE_URL'):
        load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend', '.env'))
        
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')
    
    if not url or not key:
        print("Error: Supabase credentials not found.")
        return

    supabase: Client = create_client(url, key)
    
    # Read frontend_data.json
    input_file = 'frontend_data.json'
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found. Run extract_frontend_data.py first.")
        return

    with open(input_file, 'r') as f:
        data = json.load(f)

    stats_list = []
    
    print("Preparing data for upload...")
    for zip_code, info in data.get('data', {}).items():
        indices = info.get('indices', {})
        zillow = info.get('zillow_data', {}) or {}
        crime = info.get('crime_stats', {})
        
        # Get top crime
        top_crime = "N/A"
        if crime.get('by_offense'):
            top_crime = max(crime['by_offense'], key=crime['by_offense'].get)

        row = {
            'zip_code': zip_code,
            'total_crimes': crime.get('total_crimes', 0),
            'avg_price': zillow.get('current_price'),
            'safety_index': indices.get('safety_index'),
            'affordability_index': indices.get('affordability_index'),
            'quality_of_life_index': indices.get('quality_of_life_index'),
            'investment_index': indices.get('investment_index'),
            'crime_index': indices.get('crime_index'),
            'top_crime_type': top_crime
        }
        stats_list.append(row)

    print(f"Uploading {len(stats_list)} records to 'zipcode_stats'...")
    
    try:
        data = supabase.table('zipcode_stats').upsert(stats_list).execute()
        print("✅ Upload successful!")
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        print("\nMake sure you have created the table in Supabase with this SQL:")
        print("""
        create table zipcode_stats (
          zip_code text primary key,
          total_crimes int,
          avg_price float,
          safety_index float,
          affordability_index float,
          quality_of_life_index float,
          investment_index float,
          crime_index float,
          top_crime_type text,
          updated_at timestamp with time zone default timezone('utc'::text, now())
        );
        """)

if __name__ == "__main__":
    upload_stats()
