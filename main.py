from fastapi import FastAPI, Query
from langchain.vectorstores import Chroma
from langchain.prompts import PromptTemplate
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain_openai import OpenAI
from langchain.chains import RetrievalQA
from langchain_openai import OpenAIEmbeddings
import os
import warnings

# Suppress warnings
warnings.filterwarnings("ignore")

# Set OpenAI API Key (make sure to keep this secure in production)
os.environ["OPENAI_API_KEY"] = ""

# Initialize embeddings and vector store
embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
collection_name = "TaxAI"
vectordb = Chroma(persist_directory="TaxAI2", collection_name=collection_name, embedding_function=embeddings)

# Define the prompt template
prompt_template = """
    I'm ready to assist you with your question! I'll carefully review the provided information and do my best to provide a comprehensive and accurate answer.
    **Here's the context I'll be using:**
    You Must- Don't reply from your knowledge base
    {context}
    question: {question}
    Answer: """

prompt = PromptTemplate(input_variables=["context", "question"], template=prompt_template)

# Function to generate answers
def generate_answers():
    llm1 = OpenAI(temperature=0.1, max_tokens=200)
    retriever = vectordb.as_retriever(search_type="similarity", search_kwargs={"k": 8})
    question_answers = RetrievalQA.from_chain_type(llm=llm1, chain_type="stuff", retriever=retriever, return_source_documents=True, chain_type_kwargs={'prompt': prompt})
    return question_answers

# Function to process the answer
def process_answer(instruction: str):
    qa = generate_answers()
    generated_text = qa(instruction)
    return generated_text

# FastAPI app
app = FastAPI()

@app.get("/ask")
async def ask_question(query: str = Query(..., description="Your question about tax regulations")):
    # Process the answer
    answer = process_answer(query)
    
    # Prepare the response
    response = {
        "answer": answer['result'],
        "source_titles": []
    }
    
    mdata = set()
    for source in answer['source_documents']:
        metadata = source.metadata  # Access the metadata directly
        if metadata:
            mdata.add(metadata["title"].split("|")[0])
    
    response["source_titles"] = list(mdata)
    
    return response

# Run with: uvicorn main:app --reload
