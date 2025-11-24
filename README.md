# Gene Characteristics Identifier

A web-based gene search application with a retro CRT terminal interface. Search for human genes and retrieve comprehensive biological data from the NCBI database along with clinical summaries.

**Live Application:** https://gene-characteristics-identifier.onrender.com/

## Features

- Search human genes by official gene symbol (e.g., BRCA1, TP53, EGFR)
- Retrieve comprehensive gene data from NCBI Gene Database
- Generate clinical summaries for researchers and healthcare professionals
- Retro CRT monitor aesthetic with animated DNA background
- Real-time search with loading animations
- Detailed gene information including chromosomal location, aliases, and MIM numbers

## Technology Stack

**Backend:**
- Python 3
- Flask 3.1.2
- Flask-CORS for cross-origin requests
- Requests library for API calls
- Gunicorn WSGI server

**Frontend:**
- HTML5
- CSS3 with custom animations
- Vanilla JavaScript
- Canvas API for DNA helix visualization

**External APIs:**
- NCBI E-utilities (eSearch and eSummary)
- OpenRouter (for clinical text generation)
