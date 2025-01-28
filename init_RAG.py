import os
import logging
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RagSystem:
    def __init__(self, chunk_size=1000, chunk_overlap=200):
        self.vectorstore = None
        self.retriever = None
        self.embedder = HuggingFaceEmbeddings()
        self.llm = ChatGroq(
            temperature=0,
            model_name="deepseek-r1-distill-llama-70b",
            groq_api_key=os.getenv("GROQ_API_KEY")
        )
        self.persist_dir = "chroma_db"
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def load_vectorstore(self):
        """Load persisted vector store if it exists"""
        if os.path.exists(self.persist_dir):
            self.vectorstore = Chroma(
                persist_directory=self.persist_dir,
                embedding_function=self.embedder
            )
            self.retriever = self.vectorstore.as_retriever(k=3)
            return True
        return False

    def process_documents(self):
        """Process all PDFs in documents folder"""
        try:
            # Validate documents folder
            if not os.path.exists("documents"):
                raise FileNotFoundError("Documents folder not found")
            pdf_files = [f for f in os.listdir("documents") if f.endswith(".pdf")]
            if not pdf_files:
                raise ValueError("No PDF files found in the documents folder")
            
            # Load and split all documents
            pages = []
            for pdf_file in pdf_files:
                loader = PyPDFLoader(os.path.join("documents", pdf_file))
                pages.extend(loader.load_and_split())
            
            # Create text chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap
            )
            chunks = text_splitter.split_documents(pages)
            
            # Create/update vector store with persistence
            self.vectorstore = Chroma.from_documents(
                documents=chunks,
                embedding=self.embedder,
                persist_directory=self.persist_dir
            )
            self.retriever = self.vectorstore.as_retriever(k=3)
            logger.info("Documents processed and vector store updated")
            return True
        except Exception as e:
            logger.error(f"Document processing failed: {str(e)}")
            raise RuntimeError(f"Document processing failed: {str(e)}")


    def generate_response(self, query: str) -> str:
        """Generate response using RAG pipeline with Groq"""
        if not self.retriever:
            raise ValueError("Documents not processed yet")
            
        # Retrieve relevant context
        context_docs = self.retriever.invoke(query)
        context = "\n".join([doc.page_content for doc in context_docs])
        
        prompt = f"""
        You are a helpful assistant. Answer the question using only the context below.
        If the context is irrelevant or empty, say 'I don't know'.

        Context:
        {context if context else "No relevant context found."}

        Question: {query}

        Answer:
        """
        
        response = self.llm.invoke(prompt)
        return response.content