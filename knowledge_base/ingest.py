import pip_system_certs.wrapt_requests
import os
import warnings
import time
warnings.filterwarnings("ignore")

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_cohere import CohereEmbeddings

load_dotenv()

DOCS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "docs"))
FAISS_DB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "faiss_db"))

def build_production_database():
    print("Scanning for official PCI DSS PDFs...")
    all_chunks = []

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )

    if not os.path.exists(DOCS_DIR):
        os.makedirs(DOCS_DIR)
        print(f"Created docs folder at {DOCS_DIR}. Please put your PDFs inside it and run again.")
        return

    for filename in os.listdir(DOCS_DIR):
        if filename.endswith(".pdf"):
            print(f"Processing: {filename}...")
            file_path = os.path.join(DOCS_DIR, filename)

            pci_version = "v4.0" if "4.0" in filename else "v3.2.1"

            loader = PyPDFLoader(file_path)
            pages = loader.load()
            chunks = text_splitter.split_documents(pages)

            for chunk in chunks:
                chunk.metadata["pci_version"] = pci_version

            all_chunks.extend(chunks)

    if not all_chunks:
        print(f"Error: No PDFs found in {DOCS_DIR}!")
        return

    print(f"Sliced documents into {len(all_chunks)} searchable chunks.")
    print("Initializing Cohere Enterprise API...")

    embeddings = CohereEmbeddings(
        cohere_api_key=os.getenv("COHERE_API_KEY"),
        model="embed-english-v3.0"
    )

    print("Converting chunks to math vectors... (Applying anti-rate-limit pacing)")
    
    vectorstore = None
    batch_size = 300 

    for i in range(0, len(all_chunks), batch_size):
        batch = all_chunks[i:i + batch_size]
        print(f"Uploading batch {i} to {i + len(batch)} of {len(all_chunks)}...")
        
        if vectorstore is None:
            vectorstore = FAISS.from_documents(batch, embeddings)
        else:
            vectorstore.add_documents(batch)
            
        if i + batch_size < len(all_chunks):
            print("Sleeping for 60 seconds to reset Cohere's free tier token limit...")
            time.sleep(60)

    vectorstore.save_local(FAISS_DB_DIR)
    print(f"✅ Production FAISS Database built and saved to: {FAISS_DB_DIR}")

if __name__ == "__main__":
    if not os.getenv("COHERE_API_KEY"):
        print("Error: COHERE_API_KEY not found in .env file!")
    else:
        build_production_database()
    