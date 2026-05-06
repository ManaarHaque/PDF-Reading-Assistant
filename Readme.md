# Local PDF RAG App 📄🤖

A fully local, privacy-focused Retrieval-Augmented Generation (RAG) application that allows users to chat with their PDF documents. Built with Streamlit, ChromaDB, and Ollama.

## 🌟 Features
* **Completely Local:** No API keys required. Your documents never leave your machine.
* **Smart Chunking:** Processes text and OCR data while respecting sentence boundaries.
* **Vector Search:** Uses `all-MiniLM-L6-v2` embeddings and ChromaDB for fast, semantic retrieval.
* **Interactive UI:** Built with Streamlit for a seamless, chat-like experience.

## 🛠️ Tech Stack
* **Frontend:** Streamlit
* **LLM:** Llama 3 (via Ollama)
* **Embeddings:** Sentence-Transformers
* **Vector Database:** ChromaDB
* **PDF Processing:** PyMuPDF

## 🚀 How to Run Locally

### Prerequisites
1. Python 3.9+
2. Ollama installed and running on your machine
3. Llama 3 model downloaded through Ollama
4. Tesseract OCR installed if you want scanned PDF support

Pull the Llama 3 model:
```bash
ollama pull llama3
```

Check that the model is available:
```bash
ollama list
```

## 🔍 OCR Setup

This app supports OCR for scanned or image-based PDFs using **Tesseract OCR**.

> **Important:** Tesseract is a separate system dependency and is **not installed via `requirements.txt`**.

If Tesseract is not installed, the app will still work for normal text-based PDFs, but OCR on scanned PDFs will fail.

### Windows Setup

Install Tesseract OCR for Windows. A common installation path is:

```text
C:\Program Files\Tesseract-OCR
```

Make sure this folder exists:

```text
C:\Program Files\Tesseract-OCR\tessdata
```

Inside the `tessdata` folder, there should be files such as:

```text
eng.traineddata
osd.traineddata
```

Set the `TESSDATA_PREFIX` environment variable in PowerShell:

```powershell
setx TESSDATA_PREFIX "C:\Program Files\Tesseract-OCR\tessdata"
```

You may also need to add Tesseract to your PATH:

```powershell
setx PATH "$env:PATH;C:\Program Files\Tesseract-OCR"
```

After setting these variables, close and reopen your terminal or IDE.

Test the installation:

```bash
tesseract --version
```

If the command prints a version number, Tesseract is installed correctly.

### Optional Python Environment Fix

If OCR still fails, you can set the Tesseract path directly inside `app.py`:

```python
import os
os.environ["TESSDATA_PREFIX"] = r"C:\Program Files\Tesseract-OCR\tessdata"
```

Place this near the top of the file before OCR is used.

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/ManaarHaque/PDF-Reading-Assistant.git
   cd PDF-Reading-Assistant
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   ```

   On Windows:

   ```bash
   venv\Scripts\activate
   ```

   On macOS/Linux:

   ```bash
   source venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

### Run the App

```bash
streamlit run app.py
```

The app will open in your browser at:

```text
http://localhost:8501
```

## 📄 Usage

1. Upload a PDF document.
2. Wait for the app to extract, chunk, embed, and store the document.
3. Ask a question about the PDF.
4. The app retrieves the most relevant chunks and sends them to the local Llama 3 model.
5. View the generated answer and optionally inspect the retrieved context.

## 📦 Requirements

```txt
streamlit==1.31.1
PyMuPDF==1.24.14
nltk
chromadb==0.4.24
sentence-transformers==2.7.0
ollama==0.6.2
huggingface-hub==0.25.2
```