import asyncio
import uuid
import httpx

API_URL = "http://localhost:8000/api/v1"
# Hardcoding a known case ID we used for the other tests, e.g. Arbitration Petition No. 19 of 2024
# We will fetch a list of cases first to find a valid case_id
async def main():
    async with httpx.AsyncClient() as client:
        print("Fetching cases to find a target...")
        resp = await client.get(f"{API_URL}/cases/")
        cases = resp.json()
        if not cases:
            print("No cases found in DB.")
            return
            
        case_id = cases[0]["id"]
        case_title = cases[0]["title"]
        print(f"Target case: {case_title} ({case_id})")
        
        print("\n--- EXTRACTING CITATIONS ---")
        extract_resp = await client.post(f"{API_URL}/cases/{case_id}/citations/extract", timeout=120.0)
        
        if extract_resp.status_code != 200:
            print(f"Extraction failed: {extract_resp.text}")
            return
            
        stats = extract_resp.json()
        print(f"Extraction Stats: {stats}")
        
        print("\n--- FETCHING CITATIONS ---")
        cit_resp = await client.get(f"{API_URL}/cases/{case_id}/citations")
        cit_data = cit_resp.json()
        
        print(f"Resolved Citations: {len(cit_data['resolved'])}")
        for cit in cit_data['resolved']:
            print(f" - [{cit['relationship_type']}] {cit['target_case_title']} -> {cit['citation_text']}")
            
        print(f"Unresolved Citations: {len(cit_data['unresolved'])}")
        for cit in cit_data['unresolved']:
            print(f" - [{cit['relationship_type']}] {cit['target_case_title']} -> {cit['citation_text']}")
            
        print("\n--- FETCHING CITED-BY (Should be empty for a new case unless it's targeted) ---")
        cited_resp = await client.get(f"{API_URL}/cases/{case_id}/cited-by")
        cited_data = cited_resp.json()
        print(f"Cited-by count: {len(cited_data)}")
        
if __name__ == "__main__":
    asyncio.run(main())
