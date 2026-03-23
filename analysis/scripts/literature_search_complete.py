#!/usr/bin/env python3
"""
Literature Search Tool — Complete Pipeline
API-based academic paper retrieval + Unpaywall OA detection + PDF parsing
Uses: CrossRef, OpenAlex, Europe PMC, Unpaywall, pdfplumber
"""

import requests
import json
import sys
import os
from urllib.parse import quote
from typing import Optional, List, Dict
from datetime import datetime

# Try import pdfplumber, fall back to PyPDF2
try:
    import pdfplumber
    PDF_LIBRARY = "pdfplumber"
except ImportError:
    try:
        import PyPDF2
        PDF_LIBRARY = "PyPDF2"
    except ImportError:
        PDF_LIBRARY = None

# APIs
CROSSREF_API = "https://api.crossref.org/works"
OPENALEX_API = "https://api.openalex.org/works"
EUROPE_PMC_API = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
UNPAYWALL_API = "https://api.unpaywall.org/v2"

HEADERS = {
    "User-Agent": "OpenClaw-Literature-Search/2.0 (academic research bot)"
}

# Config
UNPAYWALL_EMAIL = os.environ.get("UNPAYWALL_EMAIL", "research@openclaw.ai")  # Required by Unpaywall


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


def check_unpaywall(doi: str) -> Optional[Dict]:
    """Check Unpaywall for open access version of paper"""
    url = f"{UNPAYWALL_API}/{doi}?email={UNPAYWALL_EMAIL}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        
        if data.get("is_oa"):
            return {
                "is_oa": True,
                "oa_url": data.get("best_oa_location", {}).get("url"),
                "oa_host": data.get("best_oa_location", {}).get("host_type"),
                "license": data.get("best_oa_location", {}).get("license"),
                "version": data.get("best_oa_location", {}).get("version"),
                "pdf_url": data.get("best_oa_location", {}).get("url_for_pdf")
            }
        else:
            return {
                "is_oa": False,
                "oa_url": None,
                "reason": "No open access version found"
            }
    except Exception as e:
        print(f"Unpaywall error: {e}", file=sys.stderr)
        return None


def parse_pdf(pdf_path: str) -> Optional[Dict]:
    """Parse PDF file and extract text content"""
    if PDF_LIBRARY is None:
        print("No PDF library installed (pdfplumber or PyPDF2)", file=sys.stderr)
        return None
    
    if not os.path.exists(pdf_path):
        print(f"PDF not found: {pdf_path}", file=sys.stderr)
        return None
    
    if PDF_LIBRARY == "pdfplumber":
        try:
            with pdfplumber.open(pdf_path) as pdf:
                full_text = ""
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        full_text += text + "\n"
                
                # Basic section detection (simple heuristic)
                sections = {}
                current_section = "abstract"
                section_text = ""
                
                for line in full_text.split("\n"):
                    if len(line) < 50 and line.upper() == line:
                        # Potential section header
                        if section_text:
                            sections[current_section] = section_text
                        current_section = line.lower().strip()
                        section_text = ""
                    else:
                        section_text += line + "\n"
                
                if section_text:
                    sections[current_section] = section_text
                
                return {
                    "full_text": full_text,
                    "sections": sections,
                    "pages": len(pdf.pages),
                    "metadata": pdf.metadata
                }
        except Exception as e:
            print(f"PDF parsing error (pdfplumber): {e}", file=sys.stderr)
            return None
    
    elif PDF_LIBRARY == "PyPDF2":
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(pdf_path)
            full_text = ""
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n"
            
            return {
                "full_text": full_text,
                "pages": len(reader.pages),
                "metadata": reader.metadata
            }
        except Exception as e:
            print(f"PDF parsing error (PyPDF2): {e}", file=sys.stderr)
            return None
    
    return None


def search_all(query: str, combine: bool = True, check_oa: bool = False) -> List[Dict]:
    """Search all three APIs and optionally combine results + check OA status"""
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
            
            # Check Unpaywall if requested
            if check_oa and doi:
                oa_info = check_unpaywall(doi)
                item["open_access"] = oa_info
            
            combined.append(item)
        return combined
    else:
        return {
            "crossref": crossref,
            "openalex": openalex,
            "europe_pmc": europe_pmc
        }


def process_doi_list(doi_list: List[str], check_oa: bool = True, pdf_folder: str = None) -> List[Dict]:
    """Process a list of DOIs: fetch metadata, check OA, parse local PDFs if available"""
    results = []
    
    for doi in doi_list:
        print(f"Processing {doi}...", file=sys.stderr)
        
        # Fetch metadata
        metadata = fetch_by_doi(doi)
        if not metadata:
            continue
        
        # Check OA
        if check_oa:
            oa_info = check_unpaywall(doi)
            metadata["open_access"] = oa_info
        
        # Look for local PDF
        if pdf_folder:
            # Try common naming patterns
            pdf_candidates = [
                os.path.join(pdf_folder, f"{doi.replace('/', '_')}.pdf"),
                os.path.join(pdf_folder, f"{doi}.pdf"),
                os.path.join(pdf_folder, metadata.get("title", "").replace(":", "").replace("/", "_")[:50] + ".pdf")
            ]
            
            for pdf_path in pdf_candidates:
                if os.path.exists(pdf_path):
                    pdf_content = parse_pdf(pdf_path)
                    if pdf_content:
                        metadata["pdf_path"] = pdf_path
                        metadata["pdf_content"] = pdf_content
                    break
        
        results.append(metadata)
    
    return results


def export_bibtex(results: List[Dict]) -> str:
    """Export results as BibTeX format"""
    bibtex = ""
    
    for i, item in enumerate(results):
        doi = item.get("doi", "")
        year = item.get("year", "n.d.")
        authors = item.get("authors", [])
        title = item.get("title", "No title")
        
        # Create citation key
        if authors:
            first_author = authors[0].split()[-1] if authors[0] else "unknown"
            key = f"{first_author}{year}_{i}"
        else:
            key = f"unknown{year}_{i}"
        
        # Format authors for BibTeX
        authors_bibtex = " and ".join([a.replace("  ", " ").strip() for a in authors if a.strip()])
        
        bibtex += f"@article{{{key},\n"
        bibtex += f"  author = {{{authors_bibtex}}},\n"
        bibtex += f"  title = {{{title}}},\n"
        bibtex += f"  year = {{{year}}},\n"
        bibtex += f"  doi = {{{doi}}},\n"
        
        if item.get("publisher"):
            bibtex += f"  publisher = {{{item['publisher']}}},\n"
        
        if item.get("journal"):
            bibtex += f"  journal = {{{item['journal']}}},\n"
        
        if item.get("abstract"):
            abstract = item["abstract"].replace("{", "\\{").replace("}", "\\}")
            bibtex += f"  abstract = {{{abstract}}},\n"
        
        if item.get("open_access") and item["open_access"].get("is_oa"):
            bibtex += f"  url = {{{item['open_access']['oa_url']}}},\n"
        
        bibtex += f"}}\n\n"
    
    return bibtex


def main():
    if len(sys.argv) < 2:
        print("Usage: literature_search_complete.py <query> [output.json]")
        print("       literature_search_complete.py --doi-list <file.txt> [pdf_folder]")
        print("       literature_search_complete.py --doi <DOI>")
        print("       literature_search_complete.py --pdf <file.pdf>")
        print("\nOptions:")
        print("  --oa    Check Unpaywall for open access")
        print("  --bibtex Export as BibTeX")
        sys.exit(1)
    
    check_oa = "--oa" in sys.argv
    export_format = "bibtex" if "--bibtex" in sys.argv else "json"
    
    if sys.argv[1] == "--doi" and len(sys.argv) >= 3:
        doi = sys.argv[2]
        result = fetch_by_doi(doi)
        if result:
            if check_oa:
                result["open_access"] = check_unpaywall(doi)
            if export_format == "bibtex":
                print(export_bibtex([result]))
            else:
                print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"Could not fetch DOI: {doi}", file=sys.stderr)
            sys.exit(1)
    
    elif sys.argv[1] == "--doi-list" and len(sys.argv) >= 3:
        doi_list_file = sys.argv[2]
        pdf_folder = sys.argv[3] if len(sys.argv) > 3 else None
        
        with open(doi_list_file, "r") as f:
            doi_list = [line.strip() for line in f if line.strip()]
        
        results = process_doi_list(doi_list, check_oa=check_oa, pdf_folder=pdf_folder)
        
        if export_format == "bibtex":
            print(export_bibtex(results))
        else:
            output = {
                "query": f"DOI list from {doi_list_file}",
                "count": len(results),
                "results": results,
                "timestamp": datetime.now().isoformat()
            }
            print(json.dumps(output, indent=2, ensure_ascii=False))
    
    elif sys.argv[1] == "--pdf" and len(sys.argv) >= 3:
        pdf_path = sys.argv[2]
        content = parse_pdf(pdf_path)
        if content:
            print(json.dumps(content, indent=2, ensure_ascii=False))
        else:
            print(f"Could not parse PDF: {pdf_path}", file=sys.stderr)
            sys.exit(1)
    
    else:
        # Parse query and output file, skip flags
        query = sys.argv[1]
        output_file = None
        for arg in sys.argv[2:]:
            if not arg.startswith("--"):
                output_file = arg
                break
        
        results = search_all(query, combine=True, check_oa=check_oa)
        output = {
            "query": query,
            "count": len(results),
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
        
        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                if export_format == "bibtex":
                    f.write(export_bibtex(results))
                else:
                    json.dump(output, f, indent=2, ensure_ascii=False)
            print(f"Saved {len(results)} results to {output_file}")
        else:
            if export_format == "bibtex":
                print(export_bibtex(results))
            else:
                print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
