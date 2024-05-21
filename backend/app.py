from typing import Union
from fastapi import FastAPI, Query, UploadFile, Form, HTTPException, File, Request
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


@app.get("/document-list")
def get_client_documents():
    try:
        distinct_client_documents = get_distinct_client_document_date_combinations(
        )
        return {"clientDocuments": distinct_client_documents}
    except Exception as e:
        return {"Message": f"Error fetching distinct client documents: {e}"}


@app.get("/document-url")
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


@app.post("/document-upload")
async def upload_document(
    client_name: str = Form(...),
    document_name: str = Form(...),
    date: str = Form(...),
    docx_document: UploadFile = File(...),
    pdf_document: UploadFile = File(...)
):
    if not docx_document.filename.endswith(".docx"):
        raise HTTPException(
            status_code=400, detail="Invalid file type, expecting .docx")
    if not pdf_document.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=400, detail="Invalid file type, expecting .pdf")

    try:
        word_file_content = await docx_document.read()
        pdf_file_content = await pdf_document.read()

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error reading document: {e}")

    try:
        word_file_stream = BytesIO(word_file_content)
        document: DocumentType = Document(word_file_stream)
        # document_parser = get_parsed_pdf(
        #     pdf_file_content, DI_ENDPOINT, DI_API_KEY)
        formatted_date = datetime.strptime(
            date, "%Y-%m-%d").strftime("%d-%m-%Y")
        filename = f"{client_name}_{document_name}_{formatted_date}.pdf"
        # vectorized_chunks = await get_vectorized_chunks(document_parser, filename, document)
        # add_documents_to_db(vectorized_chunks)

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing and chunking document: {e}")

    try:
        successful_upload = upload_document_to_sharepoint(
            pdf_file_content, client_name, document_name, date, in_prod=True
        )
        if not successful_upload:
            raise HTTPException(
                status_code=500, detail="Failed to upload file to SharePoint")

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error uploading document to SharePoint: {e}")

    return JSONResponse(content={"message": "File uploaded successfully"}, status_code=200)


@app.get("/ping")
def ping():
    return {"Message": "Healthy"}


# Mount the `static` directory to the path `/`
app.mount("/", StaticFiles(directory="public", html=True), name="public")


@app.get("/{full_path:path}", include_in_schema=False)
async def catch_all(full_path: str, request: Request):
    return JSONResponse(content={
        "Message":
        f"This endpoint does not exist: {full_path} - {request}"
    },
        status_code=200)
