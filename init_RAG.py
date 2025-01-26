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

    def process_documents(self, file_path: str):
        """Process PDF documents into vector store"""
        try:
            # Load and split documents
            loader = PyPDFLoader(file_path)
            pages = loader.load_and_split()
            
            # Create text chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            chunks = text_splitter.split_documents(pages)
            
            # Create vector store
            self.vectorstore = Chroma.from_documents(
                documents=chunks,
                embedding=self.embedder
            )
            self.retriever = self.vectorstore.as_retriever(k=3)
            
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
        
        # Get response from Groq
        response = self.llm.invoke(prompt)
        return response.content