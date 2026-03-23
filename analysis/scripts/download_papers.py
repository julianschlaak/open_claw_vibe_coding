#!/usr/bin/env python3
"""
Download OA papers from Unpaywall URLs
Usage: python download_papers.py <output_folder>
"""

import requests
import sys
import os
from pathlib import Path

HEADERS = {
    "User-Agent": "OpenClaw-Literature-Download/1.0 (academic research bot)"
}

# Top 5 relevant papers with PDF URLs
papers = [
    {
        "title": "Asad_2026_Multivariate_Calibration_CAMELS",
        "url": "https://egusphere.copernicus.org/preprints/egusphere-egu26-3497/egusphere-egu26-3497.pdf",
        "doi": "10.5194/egusphere-egu26-3497"
    },
    {
        "title": "Iffland_2026_mHM_Groundwater",
        "url": "https://egusphere.copernicus.org/preprints/egusphere-egu26-5174/egusphere-egu26-5174.pdf",
        "doi": "10.5194/egusphere-egu26-5174"
    },
    {
        "title": "Mizukami_2019_Calibration_Metrics",
        "url": "https://hess.copernicus.org/articles/23/2601/2019/hess-23-2601-2019.pdf",
        "doi": "10.5194/hess-23-2601-2019"
    },
    {
        "title": "Demirel_2018_Spatial_Pattern",
        "url": "https://www.hydrol-earth-syst-sci.net/22/1299/2018/hess-22-1299-2018.pdf",
        "doi": "10.5194/hess-22-1299-2018"
    },
    {
        "title": "Dembélé_2020_Multi_Signal",
        "url": "https://onlinelibrary.wiley.com/doi/pdfdirect/10.1029/2019WR026085",
        "doi": "10.1029/2019WR026085"
    },
    {
        "title": "Fatima_2024_mHM_CosmicRay",
        "url": "https://essopenarchive.org/doi/pdf/10.22541/essoar.172910250.00782438/v1",
        "doi": "10.22541/essoar.172910250.00782438"
    }
]

def download_paper(output_folder: str, paper: dict) -> bool:
    """Download single paper"""
    filepath = os.path.join(output_folder, f"{paper['title']}.pdf")
    
    if os.path.exists(filepath):
        print(f"✓ {paper['title']}.pdf (already exists)")
        return True
    
    try:
        resp = requests.get(paper['url'], headers=HEADERS, timeout=30)
        resp.raise_for_status()
        
        with open(filepath, 'wb') as f:
            f.write(resp.content)
        
        size_mb = os.path.getsize(filepath) / (1024 * 1024)
        print(f"✓ {paper['title']}.pdf ({size_mb:.2f} MB)")
        return True
    
    except Exception as e:
        print(f"✗ {paper['title']}: {e}", file=sys.stderr)
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python download_papers.py <output_folder>")
        sys.exit(1)
    
    output_folder = sys.argv[1]
    Path(output_folder).mkdir(parents=True, exist_ok=True)
    
    print(f"Downloading {len(papers)} papers to {output_folder}...\n")
    
    success = 0
    for paper in papers:
        if download_paper(output_folder, paper):
            success += 1
    
    print(f"\nDone: {success}/{len(papers)} papers downloaded")

if __name__ == "__main__":
    main()
