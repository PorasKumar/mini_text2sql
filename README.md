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


## HOW TO RUN THIS APPLICATION LOCALLY

Prerequisites:
- Python 3.10 or higher installed.
- A Google Gemini API Key.

Step 1: Clone the Repository
Open your terminal/command prompt and run:
git clone https://github.com/PorasKumar/mini_text2sql.git
cd mini_text2sql

Step 2: Create and Activate a Virtual Environment
- On Windows:
  python -m venv venv
  venv\Scripts\activate

- On macOS/Linux:
  python3 -m venv venv
  source venv/bin/activate

Step 3: Install Required Dependencies
Run the following command to install all necessary packages:
pip install -r requirements.txt

Step 4: Set Up Your API Key
1. Create a file named .env in the root project folder.
2. Add your Google Gemini API key inside the .env file like this:
   GOOGLE_API_KEY="your_actual_gemini_api_key_here"

Step 5: Start the Application
Run the FastAPI development server:
uvicorn main:app --reload

You can use sample database from database folder in this repository. The Schema of Chinook database is shown below

<img width="1048" height="710" alt="image" src="https://github.com/user-attachments/assets/4d6da113-82d0-42fc-bcd1-be44c907971f" />

