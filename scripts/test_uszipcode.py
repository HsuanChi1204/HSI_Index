from uszipcode import SearchEngine

def check_zip(zipcode):
    search = SearchEngine()
    z = search.by_zipcode(zipcode)
    if z:
        print(f"ZIP: {zipcode}")
        print(f"Attributes: {dir(z)}")
        print(f"Dict: {z.to_dict()}")
    else:
        print("Not found")

check_zip("20024")
