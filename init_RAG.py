import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq


class RagSystem:
    def __init__(self):
        self.vectorstore = None
        self.retriever = None
        self.embedder = HuggingFaceEmbeddings()
        self.llm = ChatGroq(
            temperature=0,
            model_name="llama-3.2-1b-preview",
            groq_api_key=os.getenv("GROQ_API_KEY")
        )
        self.persist_dir = "chroma_db"

    def process_documents(self):
        """Process all PDFs in documents folder"""
        try:
            # Load all PDF files
            pdf_files = [f for f in os.listdir("documents") if f.endswith(".pdf")]
            
            # Load and split all documents
            pages = []
            for pdf_file in pdf_files:
                loader = PyPDFLoader(os.path.join("documents", pdf_file))
                pages.extend(loader.load_and_split())
            
            # Create text chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            chunks = text_splitter.split_documents(pages)
            
            # Create/update vector store with persistence
            self.vectorstore = Chroma.from_documents(
                documents=chunks,
                embedding=self.embedder,
                persist_directory=self.persist_dir
            )
            self.retriever = self.vectorstore.as_retriever(k=3) # Retrieve top 3 documents you can change this parameter to retrieve more or less context
            
        except Exception as e:
            raise RuntimeError(f"Document processing failed: {str(e)}")


    def generate_response(self, query: str) -> str:
        """Generate response using RAG pipeline with Groq"""
        if not self.retriever:
            raise ValueError("Documents not processed yet")
            
        # Retrieve relevant context
        context_docs = self.retriever.invoke(query)
        context = "\n".join([doc.page_content for doc in context_docs])
        
        # Create structured prompt
        prompt = f"""
        You are a helpful assistant. Answer the question using only the context below.
        If you don't know the answer, say 'I don't know' based on the context.

        Context:
        {context}

        Question: {query}

        Answer:
        """
        
        response = self.llm.invoke(prompt)
        return response.content