import streamlit as st
import pymupdf
import nltk
from nltk.tokenize import sent_tokenize
import chromadb
from sentence_transformers import SentenceTransformer
import ollama

try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")

try:
    nltk.data.find("tokenizers/punkt_tab")
except LookupError:
    nltk.download("punkt_tab")

#---data extraction from pdf---
def readpdf(file_path):
    doc=pymupdf.open(file_path)
    text=""
    for page_number, page in enumerate(doc, start=1):
        page_text=page.get_text()
        if len(page_text)>100:
            text+= f"page {page_number}:\n"
            text += page_text + "\n"
            text+="Method: Text Extraction\n \n"
        else:
            # If the page is likely an image, try OCR
            text += f"page {page_number}:\n"
            try:
                # This line requires Tesseract to be installed on the OS
                ocr_text = page.get_textpage_ocr().extractTEXT()
                text += ocr_text + "\n"
                text += "Method: OCR\n \n"
            except Exception as e:
                # Fallback: If OCR fails (Tesseract missing), just use what we can get
                text += page_text + "\n"
                text += f"Method: Fallback (OCR Failed: {str(e)})\n \n"
    return text

#---text chunking---
def chunk_text(text, chunk_size= 200, overlap= 50):
    sentences=sent_tokenize(text)
    chunks= []
    current_chunk = []
    current_word_count = 0

    for sentence in sentences:
        words=sentence.split()
        if current_word_count + len(words) <= chunk_size:
            current_chunk.extend(words)
            current_word_count += len(words)
        else:
            chunks.append(" ".join(current_chunk))
            if overlap<len(current_chunk):
                current_chunk = current_chunk[-overlap:]
            else:
                current_chunk = words
            current_word_count = len(current_chunk)
    if current_chunk:
        chunks.append(" ".join(current_chunk))
        
    return chunks


#---embedding generation---
@st.cache_resource
def setup_rag_pipeline(text_chunks):
    embed_model = SentenceTransformer('all-MiniLM-L6-v2')
    chroma_client = chromadb.Client()

    try:
        chroma_client.delete_collection("pdf_rag")
    except:
        pass

    collection = chroma_client.create_collection(name="pdf_rag")

    embeddings = embed_model.encode(text_chunks).tolist()
    ids = [f"chunk_{i}" for i in range(len(text_chunks))]
    collection.add(documents=text_chunks, embeddings=embeddings, ids=ids)
    return embed_model, collection

# --- UI generation ---
uploaded_file = st.file_uploader("Upload your PDF document", type="pdf")

if uploaded_file is not None:
    # Save the uploaded file temporarily so pymupdf can read it
    temp_path = "temp_uploaded.pdf"
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
        
    with st.spinner("Extracting and chunking text..."):
        raw_text = readpdf(temp_path)
        chunks = chunk_text(raw_text)
        
    with st.spinner("Creating embeddings and Vector DB..."):
        embed_model, collection = setup_rag_pipeline(chunks)
        
    st.success("Document processed successfully! You can now query the PDF.")
    
    query = st.text_input("Ask a question about your document:")
    
    if query:
        with st.spinner("Searching and generating response..."):
            # 1. Retrieve the top 3 most relevant chunks
            results = collection.query(
                query_embeddings=embed_model.encode([query]).tolist(),
                n_results=3
            )
            
            # Combine the retrieved chunks into a single context string
            retrieved_context = "\n\n".join(results['documents'][0])
            
            # 2. Build the prompt for Ollama
            prompt = f"""
            You are a helpful assistant. Use the following context to answer the user's question. 
            If the answer is not in the context, say you don't know.
            
            Context: {retrieved_context}
            
            Question: {query}
            
            Answer:
            """
            
            # 3. Generate response using Ollama
            response = ollama.chat(model='llama3', messages=[
                {'role': 'user', 'content': prompt}
            ])
            
            st.markdown("### Answer:")
            st.write(response['message']['content'])
            
            with st.expander("View Retrieved Context"):
                st.write(retrieved_context)