import pickle
import json
from datetime import datetime
from typing import Union

from document_processor_subclasses import (
    MasterDDQProcessor,
    OMProcessor,
    ClientResponsesProcessor,
    ClientResponseProcessor
)

from constants import (
    TARGET_PDF_PATH,
    CONNECTION_STRING,
    DATABASE_NAME,
    COLLECTION_NAME,
    OPENAI_API_KEY,
    OPENAI_API_VERSION,
    OPENAI_ENDPOINT,
    DI_ENDPOINT,
    DI_API_KEY
)

import re

from docx import (
    Document
)

from docx.document import Document as DocumentType

from docx.table import (
    Table
)

from docx.text.paragraph import (
    Paragraph
)

from functions import(
    get_openai_client,
    get_db_client,
    get_service_management_client,
    get_models
)

from extractor import (
    analyze_layout
)

from embeddings import (
    generate_embeddings,
    convert_chunks_to_json
)

from classes import (
    DocumentChunk,
    DocumentFlow
)

from document_parser import (
    DocumentParser
)

from document_parser_utils import (
    is_similar_color,
    remove_non_alphanumeric
)

from azure.ai.formrecognizer import AnalyzeResult, DocumentParagraph

db_client = get_db_client()

openai_client = get_openai_client()

embedding_model, completions_model = get_models()

# db_client.setup_collection()

# db_client.create_indices()

# document_analysis_result = analyze_layout(TARGET_PDF_PATH, DI_ENDPOINT, DI_API_KEY)

with open('layout_backup.pkl', 'rb') as file:
    result = pickle.load(file)

document_parser = DocumentParser(result=result)

filename = TARGET_PDF_PATH.split('/')[-1]

document: DocumentType = Document(
    TARGET_PDF_PATH.replace(".pdf", ".docx")
)

client_response_processor = ClientResponseProcessor(document_parser, filename, document)

document_flow = client_response_processor.process_document()

with open(f"{document_flow.client_name}_{document_flow.document_name}_parsing_backup.json", "w") as file:
    file.write(json.dumps(document_flow.to_dict()))

vectorized_chunks = convert_chunks_to_json(document_flow.chunks, openai_client, embedding_model)

# with open(f"{document_flow.client_name}_{document_flow.document_name}_parsing_vectorized_backup.json", "r", encoding="utf-8") as file:
#     data = file.read()

db_client.add_data_to_collection(vectorized_chunks)
