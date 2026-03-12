from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document
import os
import json

def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    chunks = text_splitter.split_text(text)
    return chunks

def get_vector_store(text_chunks, api_key):
    os.environ["GOOGLE_API_KEY"] = api_key
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001", google_api_key=api_key)
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    os.makedirs("faiss_index_dir", exist_ok=True)
    vector_store.save_local("faiss_index_dir")

def user_input(user_question, api_key):
    os.environ["GOOGLE_API_KEY"] = api_key
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001", google_api_key=api_key)
    try:
        new_db = FAISS.load_local("faiss_index_dir", embeddings, allow_dangerous_deserialization=True)
        docs = new_db.similarity_search(user_question)
        context = "\n".join([doc.page_content for doc in docs])
        
        prompt_template = """
        Answer the question as detailed as possible from the provided context, make sure to provide all the details. If the answer is not in
        provided context just say, "answer is not available in the context", don't provide the wrong answer.\n\n
        Context:\n {context}?\n
        Question: \n{question}\n

        Answer:
        """
        prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
        model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.3)
        formatted_prompt = prompt.format(context=context, question=user_question)
        response = model.invoke(formatted_prompt)
        return response.content
    except Exception as e:
        return f"Error retrieving from document: {str(e)}. Please assure documents have been uploaded and processed."

def generate_quiz(api_key, num_questions=5, difficulty="Medium"):
    os.environ["GOOGLE_API_KEY"] = api_key
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001", google_api_key=api_key)
    try:
        new_db = FAISS.load_local("faiss_index_dir", embeddings, allow_dangerous_deserialization=True)
        docs = new_db.similarity_search("core concepts main ideas overview summary", k=10)
        context_text = "\n".join([doc.page_content for doc in docs])
        
        prompt_template = f"""
        Based on the following context, generate a {num_questions}-question multiple choice quiz.
        The difficulty level should be {difficulty}.

        Context: {{context}}

        Format your response EXCLUSIVELY as a valid JSON array of objects, with no markdown formatting prefix outside of the pure JSON structure.
        The JSON structure MUST conform exactly to this example, and be parseable by Python's json.loads:
        [
            {{{{
                "question": "What is...?",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "answer": "Option A",
                "explanation": "Because..."
            }}}}
        ]
        """
        
        prompt = PromptTemplate(template=prompt_template, input_variables=["context"])
        formatted_prompt = prompt.format(context=context_text)
        
        model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7)
        response = model.invoke(formatted_prompt)
        
        import re
        
        json_str = response.content.strip()
        
        # Use regex to find the JSON array anywhere in the text
        match = re.search(r'\[\s*{.*?}\s*\]', json_str, re.DOTALL)
        if match:
            json_str = match.group(0)
            
        return json.loads(json_str)
        
    except json.JSONDecodeError as e:
        return {"error": f"Failed to parse LLM output into JSON. Please try again. Raw output: {json_str}"}
    except Exception as e:
        return {"error": str(e)}
