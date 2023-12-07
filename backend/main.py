import pickle
import json
from datetime import datetime

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
    add_chunk_and_initialize_new
)

from azure.ai.formrecognizer import AnalyzeResult, DocumentParagraph

db_client = get_db_client()

openai_client = get_openai_client()

embedding_model, completions_model = get_models()

db_client.setup_collection()

db_client.create_indices()

# document_analysis_result = analyze_layout(TARGET_PDF_PATH, DI_ENDPOINT, DI_API_KEY)

# print(document_analysis_result)

with open('layout_backup.pkl', 'rb') as file:
    result = pickle.load(file)
    
# print(cleaned_paragraphs)
# print(cleaned_tables)
# print(cleaned_font_colors)
# print(cleaned_font_weights)

def parse_master_ddq():
    document_parser = DocumentParser(result=result, start_page=3)

    cleaned_paragraphs = document_parser.extract_cleaned_paragraphs()

    cleaned_tables = document_parser.extract_cleaned_tables()

    cleaned_font_colors = document_parser.extract_cleaned_font_colors()

    cleaned_font_weights = document_parser.extract_cleaned_font_weights()
    
    section_headers = [
        "Definitions and Short Forms Used in DDQ",
        "1. Snapshot - The Firm and the Fund",
        "2. General Information - The Firm",
        "3. General Information - The Fund",
        "4. Investment Strategy",
        "5. Investment Process",
        "6. The Team",
        "7. Alignment of Interests",
        "8. Fund Terms",
        "9. Firm Governance, Risk and Compliance",
        "10. Environmental, Social and Governance (\"ESG\")",
        "11. Track Record",
        "12. Accounting, Valuation and Reporting",
        "13. Legal and Administration",
        "14. Information Technology (\"IT\"), Cyber and Physical Security",
        "15. Disaster Recovery and Business Continuity Plans",
        "16. Important Information for DDQ Recipients"
    ]
    
    # Extract bold spans
    bold_spans = []
    for font_weight in cleaned_font_weights:
        if font_weight.weight == 'bold':
            bold_spans.extend(font_weight.span)

    # Reference burgundy color
    subheader_burgundy = "#990135"
        
    # Extract similar burgundy color spans
    burgundy_spans = []
    for font_color in cleaned_font_colors:
        if is_similar_color(subheader_burgundy, font_color.color):
            burgundy_spans.extend(font_color.span)
            
    table_spans_and_tables = [(table.span, table) for table in cleaned_tables]
    
    subheadings = document_parser.get_matching_paragraphs(
        span_groups=[burgundy_spans], 
        min_words=3, 
        paragraphs=cleaned_paragraphs,
        regex_pattern=r'^([0-9]+|[a-zA-Z])[.)]',
    )

    date = "2023.06.30"
    iso_date = datetime.strptime(date, "%Y.%m.%d").isoformat()
    section_header = ""
    first_section_header = first_subsection_header = True
    consecutive_subheading = False
    filename = TARGET_PDF_PATH.strip().replace(' ', '').lower().split('/')[-1].split('.pdf')[0]

    document_flow = DocumentFlow(filename=filename)
    current_chunk = DocumentChunk()

    for paragraph in cleaned_paragraphs:
        if paragraph.role == 'pageFooter' or paragraph.role == 'pageNumber':
            continue
        paragraph_span = paragraph.span
        is_in_table = False
        for span, table in table_spans_and_tables:
            if span[0] <= paragraph_span[0] < span[0] + span[1]:
                is_in_table = True
                if table not in current_chunk.tables:
                    current_chunk.add_document_object(table)
                break
            
        if is_in_table:
            continue  # Skip the paragraph if it's part of a table
        
        if paragraph.content in section_headers and not is_in_table:
            if not first_section_header:
                current_chunk = add_chunk_and_initialize_new(current_chunk, document_flow)
            else:
                first_section_header = False
            section_header = paragraph.content
            paragraph.content = f"Section {section_header}: "
            first_subsection_header = True
            consecutive_subheading = False
        
        elif paragraph in subheadings and not is_in_table:
            if not first_subsection_header and not consecutive_subheading:
                current_chunk = add_chunk_and_initialize_new(current_chunk, document_flow)
            else:
                first_subsection_header = False
            paragraph.content = f"Section {section_header}: Subsection {paragraph.content}: "
            consecutive_subheading = True
        else:
            consecutive_subheading = False
        
        if len(current_chunk.content.strip().replace(' ','')) >= 1000 and first_subsection_header:
            current_chunk = add_chunk_and_initialize_new(current_chunk, document_flow)
            paragraph.content = f"Section {section_header}: {paragraph.content} "
        
        if not is_in_table:
            current_chunk.add_document_object(paragraph)
                
    current_chunk = add_chunk_and_initialize_new(current_chunk, document_flow)

    return document_flow

def echelon_responses():
    document_parser = DocumentParser(result=result, start_page=2)

    cleaned_paragraphs = document_parser.extract_cleaned_paragraphs()

    cleaned_tables = document_parser.extract_cleaned_tables()

    cleaned_font_colors = document_parser.extract_cleaned_font_colors()

    cleaned_font_weights = document_parser.extract_cleaned_font_weights()
    
        # Reference burgundy color
    subheader_black = "#010101"
        
    # Extract similar burgundy color spans
    black_spans = []
    for font_color in cleaned_font_colors:
        if is_similar_color(subheader_black, font_color.color):
            black_spans.extend(font_color.span)
            
    # Extract bold spans
    bold_spans = []
    for font_weight in cleaned_font_weights:
        if font_weight.weight == 'bold':
            bold_spans.extend(font_weight.span)
    
    table_spans = [table.span for table in cleaned_tables]
    
    subheadings = document_parser.get_matching_paragraphs(
        span_groups=[black_spans], 
        paragraphs=cleaned_paragraphs,
        min_words=4,
        regex_pattern=r'^([0-9]+|[a-zA-Z])[.)]',
        avoid_spans=table_spans
    )
    
    first_header = True
    consecutive_subheading = False
    filename = TARGET_PDF_PATH.strip().replace(' ', '').lower().split('/')[-1].split('.pdf')[0]
    date = filename.split('(')[-1].split(')')[0]
    iso_date = datetime.strptime(date, "%Y.%m.%d").isoformat()
    table_spans_and_tables = [(table.span, table) for table in cleaned_tables]

    document_flow = DocumentFlow(filename=filename, date=iso_date)
    current_chunk = DocumentChunk()

    for paragraph in cleaned_paragraphs:
        if paragraph.role == 'pageFooter' or paragraph.role == 'pageNumber':
            continue
        paragraph_span = paragraph.span
        is_in_table = False
        for span, table in table_spans_and_tables:
            if span[0] <= paragraph_span[0] < span[0] + span[1]:
                is_in_table = True
                if table not in current_chunk.tables:
                    current_chunk.add_document_object(table)
                break
            
        if is_in_table:
            continue  # Skip the paragraph if it's part of a table
        
        if paragraph in subheadings and not is_in_table:
            if not first_header and not consecutive_subheading:
                current_chunk = add_chunk_and_initialize_new(current_chunk, document_flow)
            else:
                first_header = False
            paragraph.content = f"Section {paragraph.content}: "
            consecutive_subheading = True
        else:
            consecutive_subheading = False
        
        if len(current_chunk.content.strip().replace(' ','')) >= 1000 and first_header:
            current_chunk = add_chunk_and_initialize_new(current_chunk, document_flow)
        
        if not is_in_table:
            current_chunk.add_document_object(paragraph)
                
    current_chunk = add_chunk_and_initialize_new(current_chunk, document_flow)

    return document_flow

echelon_chunks = echelon_responses()

with open("document_parsing_backup.json", "w") as file:
    file.write(json.dumps(echelon_chunks.to_dict()))

with open("document_parsing_backup.json", "r", encoding="utf-8") as file:
    data = file.read()    

data = json.loads(data)

vectorized_chunks = convert_chunks_to_json(echelon_chunks.chunks, openai_client, embedding_model)

with open("document_parsing_vectorized_backup.json", "r", encoding="utf-8") as file:
    data = file.read()    

db_client.add_data_to_collection(json.loads(data))