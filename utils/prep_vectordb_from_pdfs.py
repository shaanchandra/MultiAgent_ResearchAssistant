import os, time
import fitz  # PyMuPDF for PDF text extraction
import chromadb
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
import requests
from tqdm import tqdm


class PrepareVectorDBFromPDFs:
    """
    This class processes PDFs, extracts text, generates embeddings, and stores them in ChromaDB.
    
    Attributes:
        file_directory: Path to the PDF file or directory containing PDFs.
    """
    def __init__(self, file_directory, db_dir, HF_API_KEY, collection_name):
        self.file_directory = file_directory
        self.db_dir = db_dir
        self.HF_API_KEY = HF_API_KEY
        self.collection_name = collection_name
        self.chroma_client = chromadb.PersistentClient(path=self.db_dir)

        # Initialize the chunking mechanism
        self.text_chunker = RecursiveCharacterTextSplitter(
            chunk_size=500,  # Adjust chunk size as needed
            chunk_overlap=100,  # Overlap between chunks
            length_function=len,
            separators=["\n\n", "\n", " ", ""]  # Split on paragraphs, sentences, and words
        )
    

    def _extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extracts text from a given PDF file.        
        Args:
            pdf_path (str): Path to the PDF file.        
        Returns:
            str: Extracted text from the PDF.
        """
        text = ""
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text("text") + "\n"
        return text.strip()

    

    def _prepare_data_for_injection(self):
        """
        Processes PDF files: extracts text, generates embeddings, and prepares data for ChromaDB.
        
        Returns:
            tuple: Lists of documents, metadata, IDs, and embeddings.
        """
        docs = []
        ids = []
        
        if os.path.isdir(self.file_directory):
            pdf_files = [os.path.join(self.file_directory, f) for f in os.listdir(self.file_directory) if f.endswith(".pdf")]
        else:
            pdf_files = [self.file_directory] if self.file_directory.endswith(".pdf") else []
        
        if not pdf_files:
            raise ValueError("No PDF files found in the specified directory.")
        else:
            print(">> Number of PDF files found:", len(pdf_files))
        
        print("\n>> Extracting text from PDF files and generating embeddings...")        
        for index, pdf_file in enumerate(pdf_files):
            file_name = os.path.basename(pdf_file)
            extracted_text = self._extract_text_from_pdf(pdf_file)

            # Split the extracted text into chunks
            chunks = self.text_chunker.split_text(extracted_text)

            
            # Process each chunk
            for chunk_id, chunk in tqdm(enumerate(chunks), total=len(chunks), desc=f"Processing Chunks for {file_name}"):
                metadata= {
                    "source": file_name,
                    "chunk_id": chunk_id,
                    "total_chunks": len(chunks)
                }
                doc = Document(page_content=chunk, metadata=metadata, id=f"id{index}_chunk{chunk_id}")
                docs.append(doc)
                ids.append(f"id{index}_chunk{chunk_id}")
            
            # # Get embeddings using HF API
            # response = requests.post(
            #     "https://api-inference.huggingface.co/pipeline/feature-extraction/meta-llama/Meta-Llama-3-70B-Instruct",
            #     headers={"Authorization": f"Bearer {self.HF_API_KEY}"},
            #     json={"inputs": extracted_text}
            # )
            
            # if response.status_code == 200:
            #     embedding = response.json()
            #     embeddings.append(embedding)
            #     docs.append(extracted_text)
            #     metadatas.append({"source": file_name})
            #     ids.append(f"id{index}")
            # else:
            #     print(f"Error generating embedding for {file_name}: {response.text}")
        return docs, ids

    

    # def _inject_data_into_chromadb(self):
    #     """
    #     Injects processed data into ChromaDB.
    #     """
    #     print(">> Injecting data into ChromaDB...")
    #     collection = self.chroma_client.create_collection(name=self.collection_name)
    #     collection.add(
    #         documents=self.docs,
    #         metadatas=self.metadatas,
    #         embeddings=self.embeddings,
    #         ids=self.ids
    #     )
    #     print(">> Data is successfuly stored in ChromaDB.")


    def _inject_data_into_chromadb(self):
        """
        Injects processed data into ChromaDB.
        """
        print(">> Injecting data into ChromaDB...")
        t = time.time()
        # Create the embedding model
        model_name = "sentence-transformers/all-mpnet-base-v2"
        model_kwargs = {'device': 'mps'}
        encode_kwargs = {'normalize_embeddings': False}
        model = HuggingFaceEmbeddings(
            multi_process=False, # to run on multiple GPUs
            model_name=model_name,
            model_kwargs=model_kwargs,
            encode_kwargs=encode_kwargs
        )
        vectordb = Chroma.from_documents(documents=self.docs, embedding=model, ids=self.ids, persist_directory=self.db_dir, client=self.chroma_client, collection_name=self.collection_name)
        retriever = vectordb.as_retriever(search_kwargs={"k": 1})
        print(f"\n>> Data is successfuly stored in ChromaDB. Took  {time.time()-t:.2f} seconds.\n")




    def _validate_db(self):
        """
        Validates the database to ensure successful data injection.
        """
        print("\n>> Validating ChromaDB...")
        vectordb = self.chroma_client.get_collection(name=self.collection_name)        
        print(">> Number of vectors in vectordb:", vectordb.count())
        
    

    def run_pipeline(self):
        """
        Executes the pipeline: loads PDFs, extracts text, prepares embeddings, injects into ChromaDB, and validates.
        """

        print("-"*50 + "\nCreating VectorDB from PDF files\n" + "-"*50)
        self.docs, self.ids = self._prepare_data_for_injection()
        self._inject_data_into_chromadb()
        self._validate_db()
