from app.core.tools import search_stations
import json

def test_search():
    print("Testing search for 'chengannur'...")
    res1 = search_stations("chengannur")
    print(json.dumps(res1, indent=2))

    print("\nTesting search for 'kazhakuttam'...")
    res2 = search_stations("kazhakuttam")
    print(json.dumps(res2, indent=2))

if __name__ == "__main__":
    test_search()
