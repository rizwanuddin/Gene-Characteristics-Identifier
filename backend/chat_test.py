import streamlit as st
import requests

st.set_page_config(page_title="🧬 Bio Re:code Chatbot", page_icon="🧠")
st.title("🧬 Bio Re:code - AI Gene Info Tester")

st.markdown("Type a gene name (e.g., **BRCA1**, **TP53**) to test your Flask API running locally.")

gene_name = st.text_input("Enter gene name:")

if st.button("Search"):
    if not gene_name.strip():
        st.warning("Please enter a gene name!")
    else:
        try:
            with st.spinner("Searching gene info..."):
                # Send POST request to your Flask backend
                response = requests.post(
                    "http://localhost:5000/search",
                    json={"gene": gene_name.strip()}
                )

                if response.status_code == 200:
                    result = response.json()
                    st.success("✅ Gene information retrieved successfully!")
                    st.subheader(f"🧠 AI Summary ({result['ai_model']})")
                    st.write(result["ai_summary"])
                    
                    st.subheader("📋 Gene Details")
                    st.json({
                        "Gene": result["gene"],
                        "Description": result["description"],
                        "Summary": result["summary"],
                        "Chromosome": result["chromosome"],
                        "Source": result["source"]
                    })
                else:
                    st.error(f"Error {response.status_code}: {response.text}")

        except Exception as e:
            st.error(f"Connection error: {e}")
