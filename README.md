# Text-to-SQL RAG API

A lightweight backend application built with FastAPI, LangChain, and Google Gemini 
that converts natural language questions into precise SQL queries using hybrid schema retrieval.

## How It Works

1. **Database Upload**: Users upload an SQLite database file (.db, .sqlite) through the web interface.

2. **In-Memory Deserialization**: The backend reads the file bytes directly into server RAM using SQLite3's deserialize feature,
   then we pass it to the SQLAlchemy for establishing a connection into RAM, avoiding permanent disk storage and file-lock issues.
   
4. **Schema Extraction**: SQLAlchemy inspects the database tables and columns, formatting them into structured text descriptions.
  Then we convert the extracted schema to LangChain.Document format, so that we can store it on a Vector Database.

5. **Hybrid RAG Search**: 
   - **BM25** handles exact keyword matching for table and column names.
   - **HuggingFace (all-MiniLM-L6-v2)** runs local semantic embeddings for conceptual matching.
   - An EnsembleRetriever merges both search results to pull only the relevant tables.
   
6. **SQL Generation**: The filtered schema and user question are passed into Google Gemini-3.5-Flash-Lite
    with zero temperature to output clean, executable SQL.



## Tech Stack

- **Backend**: FastAPI, Uvicorn, SQLAlchemy
- **RAG / AI**: LangChain, HuggingFace Sentence-Transformers, Rank-BM25, Google GenAI
- **Frontend**: HTML, CSS, JavaScript (Fetch API)  used Gemini to do the frontend beautification.


## Test it Live at
https://text-to-sql-rag-api.onrender.com

You can use sample database from database folder in this repository. The Schema of Chinook database is shown below

<img width="1067" height="725" alt="image" src="https://github.com/user-attachments/assets/4f3cbd09-3583-4f9f-9147-39cb1db9720c" />
