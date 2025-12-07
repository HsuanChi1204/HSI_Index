import json
import os

def main():
    input_file = 'dc_crime_zillow_combined.json'
    output_file = 'frontend_data.json'
    
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return

    print(f"Reading {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Create new structure based on user request
    new_data = {
        'metadata': data.get('metadata', {}),
        'data': {}
    }

    print("Processing data...")
    for zip_code, info in data.get('data', {}).items():
        # Extract only the requested fields
        new_data['data'][zip_code] = {
            'zip_code': info.get('zip_code'),
            'zillow_data': info.get('zillow_data'),
            'census_data': info.get('census_data'),
            'crime_stats': {
                'total_crimes': info.get('crime_stats', {}).get('total_crimes'),
                'by_offense': info.get('crime_stats', {}).get('by_offense'),
                'by_shift': info.get('crime_stats', {}).get('by_shift'),
                'by_ward': info.get('crime_stats', {}).get('by_ward')
            },
            'indices': info.get('indices'),
            'hci': info.get('hci')
        }

    print(f"Writing to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(new_data, f, indent=2, ensure_ascii=False)
    
    # Calculate size reduction
    original_size = os.path.getsize(input_file) / 1024 / 1024
    new_size = os.path.getsize(output_file) / 1024 / 1024
    
    print(f"Done! File saved as {output_file}")
    print(f"Original size: {original_size:.2f} MB")
    print(f"New size: {new_size:.2f} MB")
    print(f"Reduction: {(1 - new_size/original_size)*100:.1f}%")

if __name__ == "__main__":
    main()
