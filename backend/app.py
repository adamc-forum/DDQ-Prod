from typing import Union
from fastapi import FastAPI, Query, UploadFile, Form, HTTPException, File
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from docx import Document
from docx.document import Document as DocumentType

from io import BytesIO

from api_methods import (
    generate_completion,
    get_distinct_client_names,
    get_distinct_client_document_date_combinations,
    get_parsed_pdf,
    get_vectorized_chunks, 
    add_documents_to_db
)

from functions import (
    upload_document_to_sharepoint
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
    client_names: list[str] = Query(None, title="Client Names")
):
    try:
        llm_response, vector_search_results = generate_completion(
            query, result_count, client_names)
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


@app.get("/documents")
def get_client_documents():
    try:
        distinct_client_documents = get_distinct_client_document_date_combinations()
        return {"clientDocuments": distinct_client_documents}
    except Exception as e:
        return {"Message": f"Error fetching distinct client documents: {e}"}


@app.get("/documentUrl")
def get_client_documents(
    client_name: str = Query(None, title="Client Name"),
    document_name: str = Query(None, title="Document Name"),
    date: str = Query(None, title="Date"),
    page_number: int = Query(0, title="Page Number")
):
    try:
        document_url = f"{SHAREPOINT_BASE_URL}/{client_name}_{document_name}_{date}.pdf#page={page_number}"
        return {"documentUrl": document_url}
    except Exception as e:
        return {"Message": f"Error fetching document url: {e}"}

# Mount the `static` directory to the path `/`
app.mount("/", StaticFiles(directory="public", html=True), name="public")
