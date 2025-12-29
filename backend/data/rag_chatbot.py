import os
import google.generativeai as genai
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv

load_dotenv(dotenv_path='../.env') 

GEMINI_SECRET_KEY = os.environ.get("GEMINI_SECRET_KEY")
genai.configure(api_key="xxxxxxxx")  

def build_retriever():
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    doc_dir = os.path.join(backend_dir, "rag_docs")
    
    if not os.path.exists(doc_dir):
        return None
    
    doc_paths = [os.path.join(doc_dir, f) for f in os.listdir(doc_dir) if f.endswith(".txt")]
    
    if not doc_paths:
        return None
    
    docs = []
    for p in doc_paths:
        try:
            loader = TextLoader(p, encoding='utf-8')
            docs.extend(loader.load())
        except:
            try:
                loader = TextLoader(p, encoding='latin-1')
                docs.extend(loader.load())
            except:
                continue
    
    if not docs:
        return None
    
    splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    splits = splitter.split_documents(docs)
    
    if not splits:
        return None
    
    embed = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectordb = FAISS.from_documents(splits, embed)
    retriever = vectordb.as_retriever(search_kwargs={"k": 3})
    
    return retriever

def query_rag_chatbot(user_query):
    try:
        retriever = build_retriever()
        if retriever is None:
            return "No documents available yet. Please upload insurance PDFs first."
        
        # Get relevant documents
        docs = retriever.get_relevant_documents(user_query)
        
        if not docs:
            return "I couldn't find relevant information to answer your question."
        
        # Combine document content
        context = "\n\n".join([doc.page_content for doc in docs])
        
        # Use Gemini to generate answer
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
        
        prompt = f"""Based on the following insurance documents, answer the user's question. 
If the information is not in the documents, say "I don't have that information in the available documents."

Documents:
{context}

Question: {user_query}

Answer:"""
        
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        return f"Error: {str(e)}"
