from langchain_core.documents import Document
from sqlalchemy import create_engine, inspect
from fastapi import HTTPException
import sqlite3 #we'll read db as sqlite3 first, then pass it to SQLAlchemy, because I was getting an Error while using tempfile library for reading db directly into RAM

def extract_schema_from_bytes(file_bytes:bytes) ->list[Document]:
    """Writes uploaded file bytes into a temporary in-memory/OS-cache file,
    inspects it via SQLAlchemy, and extracts LangChain documents."""
    try:
            #create a sqlite3 db connection with uploaded db
            def sqlite_creator():
                 conn = sqlite3.connect(":memory:")
                 #load the raw_bytes into memory
                 conn.deserialize(file_bytes)

                 return conn

            #pass the user db loaded into sqlite3 conn to SQLAlchemy engine below
            engine = create_engine("sqlite://", creator=sqlite_creator)
            inspector = inspect(engine) #to inspect the schema

            #list for storing langchain docs
            documents = []


            #now we extract the the data from schema and store them as langchain Document format
            for table_name in inspector.get_table_names():
                columns = inspector.get_columns(table_name)
                col_descriptions = [f"- {col['name']} ({col['type']})" for col in columns]

                #a payload for page_content
                table_text = (
                    f"Table Name: {table_name}\n"
                    f"Columns:\n" + "\n".join(col_descriptions)
                )

                documents.append(
                    Document(page_content=table_text, 
                            metadata={"table_name": table_name})
                )


            return documents

    except Exception as e:
        print(f"Error in extracting schema from Database\n\n{e}")
        raise HTTPException(status_code=500, detail=str(e))