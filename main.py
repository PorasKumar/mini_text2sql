from pydantic import BaseModel, Field

from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from src.schema_to_document import extract_schema_from_bytes
from src.hybrid_search_logic import embed_store_retrieve
from src.prompts import sql_query_gen_prompt

#loading .env file
load_dotenv()

#load gemini model
llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")

#init FastAPI object in app variable
app = FastAPI(
    title="Text-to-SQL API",
    description="API that converts plain English queries into SQL based on provided schema.",
    version="1.0.0"
)

#pydantic class for SQL query response by LLM
class TextToSQLResponse(BaseModel):
    sql_query:str


##################
# Front End Work #
##################

# 1. Mount the static directory so FastAPI can serve your CSS file
# This expects a folder named "static" in the same directory as main.py containing styles.css
app.mount("/static", StaticFiles(directory="static"), name="static")

#index.html file template loaded in variable below
templates = Jinja2Templates(directory="templates")



#################
#    ENDPOINTS  #
#################

#import the external HTML file via jinja2 templates
@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse(request, "index.html")


#below will be the endpoint for reading db, converting it into langchain Document
#chunking and embedding, then upserting to pinecone, taking user query, and generating the final QUERY

@app.post("/generate-sql", response_model=TextToSQLResponse)
async def generate_sql( db_file:UploadFile=File(...), user_query:str = Form(...)): #inputs from User
    try:
        #read file bytes into RAM
        file_bytes = await db_file.read()

        #extract schema in LangChain Document format, without saving file into disk
        documents = extract_schema_from_bytes(file_bytes)


        if not documents:
            raise HTTPException(status_code=400 ,detail="Database is empty or invalid!")
        

        #retrieve relevant docs by running the hybrid search using EnsembleRetriever (RRF)
        relevant_docs = embed_store_retrieve(documents, user_query)

        #structuring the data for context purpose
        filtered_schema = "\n\n".join([doc.page_content for doc in relevant_docs])
        print(f"Retrieved {len(relevant_docs)} relevant tables out of {len(documents)} total tables.")


        #prompts and llm response generation
        system_prompt = sql_query_gen_prompt

        #user prompt with the relevant context and user query
        user_prompt = f"Relevant Database Schema:\n{filtered_schema}\n\nUser Question: {user_query}"

        #invoke gemini via langchain
        messages = [
            ("system", system_prompt),
            ("human", user_prompt)
        ]
        
        response = llm.invoke(messages)
        sql_query = response.content

        # Handle response.content if it is returned as a list or a string
        if isinstance(response.content, list):
            sql_query = "".join([item.get("text", "") if isinstance(item, dict) else str(item) for item in response.content]).strip()
        else:
            sql_query = str(response.content).strip()

        # Cleanup markdown formatting blocks if Gemini includes them
        if sql_query.startswith("```"):
            sql_query = sql_query.split("```")[1]
            if sql_query.startswith("sql"):
                sql_query = sql_query[3:].strip()
        
        return TextToSQLResponse(sql_query=sql_query)

    except Exception as e:
        print(f"Error while Executing Generate SQL Pipeline!\n\n{e}")
        raise HTTPException(status_code=500, detail=str(e))