# app.py — Bio Re:code Backend Server (Gemini 2.0 Flash Version)
# This file handles searching for genes and generating AI summaries using Google Gemini 2.0.

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv

# Load environment variables (so we don't expose API keys in code)
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")



app = Flask(__name__)
CORS(app)  # Enables frontend (like Streamlit or HTML) to talk to this backend


# =====================================================
# 🧬 Function 1: Search for a gene in the NCBI database
# =====================================================
def search_gene(gene_name):
    """
    This function searches for a gene and retrieves basic biological information
    from the NCBI Gene database.
    Example: "BRCA1" or "TP53"
    """
    print(f"Searching for gene: {gene_name}")
    
    try:
        # Step 1: Find the gene ID using NCBI's eSearch API
        url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        params = {
            'db': 'gene',
            'term': f'{gene_name}[Gene Name] AND human[Organism]',
            'retmode': 'json'
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        # Check if results exist
        if 'idlist' not in data['esearchresult'] or not data['esearchresult']['idlist']:
            return {"error": "Gene not found"}
        
        gene_id = data['esearchresult']['idlist'][0]
        print(f"Found gene ID: {gene_sid}")
        
        # Step 2: Get detailed info using NCBI's eSummary API
        summary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
        summary_params = {
            'db': 'gene',
            'id': gene_id,
            'retmode': 'json'
        }
        
        summary_response = requests.get(summary_url, params=summary_params, timeout=10)
        summary_data = summary_response.json()
        
        gene_info = summary_data['result'][gene_id]
        
        # Step 3: Return key details for display or AI summary
        return {
            'name': gene_info.get('name', gene_name),  # Gene symbol (e.g., BRCA1)
            'gene_id': gene_id,  # Unique NCBI Gene ID
            'description': gene_info.get('description', 'No description available'),
            'summary': gene_info.get('summary', 'No summary available'),
            'chromosome': gene_info.get('chromosome', 'Unknown'),  # Which chromosome it's located on
            'map_location': gene_info.get('maplocation', 'Unknown'),  # Exact chromosome position
            'aliases': ', '.join(gene_info.get('otheraliases', [])) if gene_info.get('otheraliases') else 'None',
            'mim_number': ', '.join([str(m) for m in gene_info.get('mim', [])]) if gene_info.get('mim') else 'Not available',
            'organism': gene_info.get('organism', {}).get('scientificname', 'Homo sapiens'),
            'gene_type': gene_info.get('geneticsource', 'Unknown')  # e.g., protein-coding, pseudogene, etc.
        }
        
    except Exception as e:
        print(f"Error: {e}")
        return {"error": str(e)}


# =====================================================
# 🤖 Function 2: Generate AI Summary using Google Gemini 2.0 Flash
# =====================================================
def create_ai_summary(gene_info):
    """
    This function takes gene information and asks the Google Gemini 2.0 Flash model
    to create a short, human-readable summary for researchers and clinicians.
    
    Gemini 2.0 Flash is faster and more efficient than 1.5 Pro!
    """
    print("Creating AI summary with Gemini 2.0 Flash...")
    
    try:
        # Google Gemini 2.0 Flash endpoint
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={GEMINI_API_KEY}"
        
        # Prompt template for Gemini
        prompt = f"""You are a bioinformatics expert. Create a brief 3–4 sentence summary for researchers and clinicians.

Gene: {gene_info.get('name', 'Unknown')}
Description: {gene_info.get('description', 'No description')}
Details: {gene_info.get('summary', 'No details')[:500]}

Focus on:
1. What this gene does (functional role)
2. Any disease connections
3. Clinical significance

Keep it concise and professional."""
        
        # Gemini 2.0 request payload
        data = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.3,          # Keep tone factual and consistent
                "maxOutputTokens": 300,      # Limit summary length
                "topP": 0.8,                 # Nucleus sampling for better quality
                "topK": 40                   # Top-k sampling
            }
        }
        
        # Send the request to Gemini 2.0
        response = requests.post(url, json=data, timeout=30)
        result = response.json()
        
        # Extract AI text response
        if 'candidates' in result and len(result['candidates']) > 0:
            ai_text = result['candidates'][0]['content']['parts'][0]['text']
            return ai_text
        else:
            error_msg = result.get('error', {}).get('message', 'Unknown error')
            return f"Could not generate AI summary. Error: {error_msg}"
            
    except Exception as e:
        print(f"AI Error: {e}")
        return f"AI summary unavailable: {str(e)}"


# =====================================================
# 🌐 Flask API Endpoints
# =====================================================
@app.route('/search', methods=['POST'])
def search():
    """
    This endpoint handles POST requests from your frontend or Streamlit interface.
    It expects a JSON object containing { "gene": "<gene_name>" }.
    """
    print("\n=== New Search Request ===")
    
    # Extract gene name from incoming request
    data = request.get_json()
    gene_name = data.get('gene', '').strip().upper()
    
    if not gene_name:
        return jsonify({"error": "Please enter a gene name"}), 400
    
    print(f"Searching for: {gene_name}")
    
    # Step 1: Get gene data from NCBI
    gene_data = search_gene(gene_name)
    if "error" in gene_data:
        return jsonify(gene_data), 404
    
    # Step 2: Generate AI summary with Gemini 2.0
    ai_summary = create_ai_summary(gene_data)
    
    # Step 3: Combine all info into one response
    result = {
        "success": True,
        "gene": gene_data['name'],
        "gene_id": gene_data['gene_id'],
        "description": gene_data['description'],
        "summary": gene_data['summary'],
        "chromosome": gene_data['chromosome'],
        "map_location": gene_data['map_location'],
        "aliases": gene_data['aliases'],
        "mim_number": gene_data['mim_number'],
        "organism": gene_data['organism'],
        "gene_type": gene_data['gene_type'],
        "ai_summary": ai_summary,
        "source": "NCBI Gene Database",
        "ai_model": "Google Gemini 2.0 Flash"
    }
    
    print("Search completed successfully!")
    return jsonify(result)


# Simple test route to check backend connection
@app.route('/test', methods=['GET'])
def test():
    """
    Basic health check route to verify the server is running.
    """
    return jsonify({
        "status": "Server is running!",
        "message": "Bio Re:code API v1.0",
        "ai_model": "Google Gemini 2.0 Flash"
    })


# =====================================================
# 🚀 Run the Flask Server
# =====================================================
if __name__ == '__main__':
    print("=" * 50)
    print("🧬 Bio Re:code Server Starting...")
    print("=" * 50)
    print("🤖 Using: Google Gemini 2.0 Flash (Experimental)")
    print("📡 Server running at: http://localhost:5000")
    print("🧪 Test it at: http://localhost:5000/test")
    print("=" * 50)
    app.run(debug=True, port=5000)