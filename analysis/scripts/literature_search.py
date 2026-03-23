#!/usr/bin/env python3
"""
Literature Search Tool — API-based academic paper retrieval
Uses free APIs: CrossRef, OpenAlex, Europe PMC
No web scraping, no Brave API required
"""

import requests
import json
import sys
from urllib.parse import quote
from typing import Optional, List, Dict

# APIs
CROSSREF_API = "https://api.crossref.org/works"
OPENALEX_API = "https://api.openalex.org/works"
EUROPE_PMC_API = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"

HEADERS = {
    "User-Agent": "OpenClaw-Literature-Search/1.0 (academic research bot)"
}


def search_crossref(query: str, rows: int = 10) -> List[Dict]:
    """Search CrossRef API for works matching query"""
    url = f"{CROSSREF_API}?query.title={quote(query)}&rows={rows}&select=title,author,DOI,published,abstract,publisher,type"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        items = data.get("message", {}).get("items", [])
        results = []
        for item in items:
            results.append({
                "source": "CrossRef",
                "title": item.get("title", [""])[0],
                "authors": [a.get("given", "") + " " + a.get("family", "") for a in item.get("author", [])],
                "doi": item.get("DOI"),
                "year": item.get("published", {}).get("date-parts", [[""]])[0][0],
                "publisher": item.get("publisher"),
                "type": item.get("type"),
                "abstract": item.get("abstract", "")
            })
        return results
    except Exception as e:
        print(f"CrossRef error: {e}", file=sys.stderr)
        return []


def search_openalex(query: str, per_page: int = 10) -> List[Dict]:
    """Search OpenAlex API for works matching query"""
    url = f"{OPENALEX_API}?search={quote(query)}&per_page={per_page}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        results = []
        for item in data.get("results", []):
            results.append({
                "source": "OpenAlex",
                "title": item.get("title"),
                "authors": [a.get("author", {}).get("display_name") for a in item.get("authorships", [])],
                "doi": item.get("doi"),
                "year": (item.get("publication_year") or ""),
                "publisher": item.get("host_organization_name"),
                "type": item.get("type"),
                "abstract": item.get("abstract", ""),
                "cites": item.get("cited_by_count"),
                "open_access": item.get("open_access", {}).get("is_oa")
            })
        return results
    except Exception as e:
        print(f"OpenAlex error: {e}", file=sys.stderr)
        return []


def search_europe_pmc(query: str, page_size: int = 10) -> List[Dict]:
    """Search Europe PMC API for literature"""
    url = f"{EUROPE_PMC_API}?query={quote(query)}&format=json&pageSize={page_size}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        results = []
        for item in data.get("resultList", {}).get("result", []):
            results.append({
                "source": "Europe PMC",
                "title": item.get("title"),
                "authors": item.get("authorList", {}).get("author", []),
                "doi": item.get("doi"),
                "pmid": item.get("pmid"),
                "year": item.get("pubYear"),
                "journal": item.get("journalTitle"),
                "type": item.get("articleType"),
                "abstract": item.get("abstractText")
            })
        return results
    except Exception as e:
        print(f"Europe PMC error: {e}", file=sys.stderr)
        return []


def fetch_by_doi(doi: str) -> Optional[Dict]:
    """Fetch single paper metadata by DOI"""
    url = f"{CROSSREF_API}/{doi}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        item = resp.json().get("message", {})
        return {
            "source": "CrossRef (DOI)",
            "title": item.get("title", [""])[0],
            "authors": [a.get("given", "") + " " + a.get("family", "") for a in item.get("author", [])],
            "doi": item.get("DOI"),
            "year": item.get("published", {}).get("date-parts", [[""]])[0][0],
            "publisher": item.get("publisher"),
            "type": item.get("type"),
            "abstract": item.get("abstract", ""),
            "references_count": len(item.get("reference", []))
        }
    except Exception as e:
        print(f"DOI fetch error: {e}", file=sys.stderr)
        return None


def search_all(query: str, combine: bool = True) -> List[Dict]:
    """Search all three APIs and optionally combine results"""
    crossref = search_crossref(query)
    openalex = search_openalex(query)
    europe_pmc = search_europe_pmc(query)
    
    if combine:
        # Deduplicate by DOI
        seen_dois = set()
        combined = []
        for item in crossref + openalex + europe_pmc:
            doi = item.get("doi")
            if doi and doi in seen_dois:
                continue
            if doi:
                seen_dois.add(doi)
            combined.append(item)
        return combined
    else:
        return {
            "crossref": crossref,
            "openalex": openalex,
            "europe_pmc": europe_pmc
        }


def main():
    if len(sys.argv) < 2:
        print("Usage: literature_search.py <query> [output.json]")
        print("       literature_search.py --doi <DOI>")
        sys.exit(1)
    
    if sys.argv[1] == "--doi" and len(sys.argv) >= 3:
        doi = sys.argv[2]
        result = fetch_by_doi(doi)
        if result:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"Could not fetch DOI: {doi}", file=sys.stderr)
            sys.exit(1)
    else:
        query = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else None
        
        results = search_all(query, combine=True)
        output = {
            "query": query,
            "count": len(results),
            "results": results
        }
        
        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(output, f, indent=2, ensure_ascii=False)
            print(f"Saved {len(results)} results to {output_file}")
        else:
            print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
