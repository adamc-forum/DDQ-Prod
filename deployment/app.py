from typing import Union
from fastapi import FastAPI, Query, UploadFile, Form, HTTPException, File, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.responses import FileResponse
from docx import Document
from docx.document import Document as DocumentType

from io import BytesIO
import os

from api_methods import (
    generate_completion,
    get_distinct_client_names,
    get_distinct_client_document_date_combinations,
    get_parsed_pdf,
    get_vectorized_chunks,
    add_documents_to_db
)

from functions import (
    create_pdf_and_upload_to_sharepoint,
    delete_documents_from_sharepoint,
    get_db_client,
    get_document_url
)

from datetime import datetime

from constants import SHAREPOINT_BASE_URL, DI_ENDPOINT, DI_API_KEY

app = FastAPI()

# Configure CORS for dev environment
# Not required for prod since both frontend and api have same root domain, same-origin request

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Allows all origins
#     allow_credentials=True,
#     allow_methods=["*"],  # Allows all methods
#     allow_headers=["*"],  # Allows all headers
# )

@app.get("/search")
def read_root(
    query: str = Query(None, title="Query"),
    result_count: int = Query(5, title="Result Count"),
    word_limit: int = Query(300, title="Word Limit"),
    client_names: list[str] = Query(None, title="Client Names")
):
    try:
        llm_response, vector_search_results = generate_completion(query, result_count, client_names, word_limit)
        return {
            "response": llm_response,
            "results": vector_search_results
        }
    except Exception as e:
        return {"Message": f"Error fetching response: {e}"}


@app.get("/clients")
def get_client_names():
    try:
        distinct_client_names = get_distinct_client_names()
        return {"clientNames": distinct_client_names}
    except Exception as e:
        return {"Message": f"Error fetching distinct client names: {e}"}


@app.get("/document-list")
def get_client_documents():
    try:
        distinct_client_documents = get_distinct_client_document_date_combinations()
        return {"clientDocuments": distinct_client_documents}
    except Exception as e:
        return {"Message": f"Error fetching distinct client documents: {e}"}

@app.post("/document-create")
async def upload_document(
    client_name: str = Form(...),
    document_name: str = Form(...),
    date: str = Form(...),
    docx_document: UploadFile = File(...),
):
    if not docx_document.filename.endswith(".docx"):
        raise HTTPException(status_code=400, detail="Invalid file type, expecting .docx")

    try:
        # Read the DOCX file content
        word_file_content = await docx_document.read()

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading document: {e}")

    try:
        formatted_date = datetime.strptime(date, "%Y-%m-%d").strftime("%d-%m-%Y")
        pdf_file_content = create_pdf_and_upload_to_sharepoint(word_file_content, client_name, document_name, formatted_date)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading document to SharePoint: {e}")

    try:
        word_file_stream = BytesIO(word_file_content)
        document: DocumentType = Document(word_file_stream)
        document_parser = get_parsed_pdf(pdf_file_content, DI_ENDPOINT, DI_API_KEY)
        filename = f"{client_name}_{document_name}_{formatted_date}.pdf"
        vectorized_chunks = await get_vectorized_chunks(document_parser, filename, document, in_prod=True)
        add_documents_to_db(vectorized_chunks)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing and chunking document: {e}")
    
    return JSONResponse(content={"message": "File uploaded successfully"}, status_code=200)

@app.delete("/document-delete")
async def delete_document(
    document_id: str = Query(..., title="Document ID"),
):
    db_client = get_db_client();
    existing_document = db_client.find_documents_by_substring(fieldname="id", substring=document_id)
    if not existing_document:
        raise HTTPException(status_code=410, detail=f"Document {document_id} does not exist or has already been deleted")
    
    try:
        db_client.remove_data_from_collection(fieldname="id", substring=document_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")
    
    try:
        id_deleted_successfully = delete_documents_from_sharepoint(document_id)
        if not id_deleted_successfully:
            raise HTTPException(status_code=404, detail=f"Unable to delete document from Sharepoint: {e}")
            
    except:
        raise HTTPException(status_code=404, detail=f"Unable to delete document from Sharepoint: {e}")

    return JSONResponse(content={"message": f"Document {document_id} deleted successfully"}, status_code=200)

@app.delete("/chunk-delete")
async def delete_document(
    chunk_id: str = Query(..., title="Chunk ID"),
):
    db_client = get_db_client();
    existing_document = db_client.find_documents_by_substring(fieldname="id", substring=chunk_id)
    if not existing_document:
        raise HTTPException(status_code=410, detail=f"Chunk {chunk_id} does not exist or has already been deleted")
    
    try:
        db_client.remove_data_from_collection(fieldname="id", substring=chunk_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")

    return JSONResponse(content={"message": f"Chunk {chunk_id} deleted successfully"}, status_code=200)
        

@app.get("/ping")
def ping():
    return {"Message": "Healthy"}

app.mount("/", StaticFiles(directory="public", html=True), name="public")

@app.get("/{full_path:path}", include_in_schema=False)
async def catch_all():
    return FileResponse("public/index.html")
