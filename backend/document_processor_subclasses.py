from document_processor import DocumentProcessor
from document_parser_utils import add_chunk_and_initialize_new
from classes import (
    DocumentFlow, 
    DocumentChunk, 
    CleanedParagraph
)

class MasterDDQProcessor(DocumentProcessor):
    def __init__(self, document_parser, filename):
        super().__init__(document_parser, filename)
        self.section_headers = [
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
        self.subheader_color = "#990135"  # Burgundy color for subheaders
        self.subheadings = self.get_subheadings()

    def process_document(self):
        document_flow = DocumentFlow(self.filename)
        current_chunk = DocumentChunk()
        max_chunk_size = 750  # Adjust the chunk size as needed
        last_found_was_header = False
        found_header_or_subheader = False
        found_subheader = False
        current_heading = ""
        
        for paragraph in self.cleaned_paragraphs:
            if paragraph.role == 'pageFooter' or paragraph.role == 'pageNumber':
                continue
            
            is_header = paragraph.content in self.section_headers
            is_subheader = paragraph in self.subheadings
            
            is_in_table, table = self.is_paragraph_in_table(paragraph.span)
            if is_in_table:
                if table not in self.processed_tables:
                    current_chunk.add_document_object(table)
                    self.processed_tables.add(table)
                continue  # Skip to next paragraph after handling the table
            
            # Determine if a new chunk should start
            start_new_chunk = False
            if is_header or is_subheader:
                found_subheader = found_subheader or is_subheader
                if not last_found_was_header and found_header_or_subheader:
                    start_new_chunk = True
                found_header_or_subheader = True 
            elif not found_subheader and len(current_chunk.content) >= max_chunk_size:
                start_new_chunk = True
            
            # print(f"{start_new_chunk} - {paragraph.content} - {is_header or is_subheader}")
            
            # Start a new chunk if required
            if start_new_chunk:
                if current_chunk.content:  # Check if there's content to be finalized
                    current_chunk = self.prepend_headers_to_chunk(current_chunk, current_heading=current_heading)
                    self.finalize_chunk(current_chunk, document_flow)
                current_chunk = DocumentChunk()
            
            # Directly add paragraph to the chunk
            if not is_header:
                current_chunk.add_document_object(paragraph)
            
            # Update heading or subheading
            if is_header:
                current_heading = paragraph.content
            
            last_found_was_header = is_header or is_subheader

        # Finalize the last chunk
        if current_chunk.content:
            self.prepend_headers_to_chunk(current_chunk, current_heading)
            self.finalize_chunk(current_chunk, document_flow)

        return document_flow

    def get_subheadings(self) -> list[CleanedParagraph]:
        subheader_spans = self.get_color_spans(self.subheader_color)
        table_spans = [table.span for table in self.cleaned_tables]
        subheadings = self.document_parser.get_matching_paragraphs(
            span_groups=[subheader_spans],
            min_words=4,
            paragraphs=self.cleaned_paragraphs,
            regex_pattern=r'^([0-9]+|[a-zA-Z])[.)]',
            avoid_spans=table_spans
        )
        return subheadings

class ClientResponsesProcessor(DocumentProcessor):
    def __init__(self, document_parser, subheader_color, filename):
        super().__init__(document_parser, filename)
        self.subheader_color = subheader_color
        self.subheadings = self.get_subheadings()
        # for subheading in self.subheadings:
        #     print(subheading.content)
    
    def get_subheadings(self) -> list:
        subheader_spans = self.get_color_spans(self.subheader_color)
        table_spans = [table.span for table in self.cleaned_tables]
        subheadings = self.document_parser.get_matching_paragraphs(
            span_groups=[subheader_spans],
            min_words=4,
            paragraphs=self.cleaned_paragraphs,
            regex_pattern=r'^([0-9]+|[a-zA-Z])[.)]',
            avoid_spans=table_spans
        )
        return subheadings

    def process_document(self):
        document_flow = DocumentFlow(self.filename)
        current_chunk = DocumentChunk()
        max_chunk_size = 750  # Adjust the chunk size as needed
        found_subheader = False
        last_found_was_header = False
        
        for paragraph in self.cleaned_paragraphs:
            if "Forum House at Brookfield Place East Podium, 2nd Floor 181 Bay Street Toronto, ON M5J 2T3" in paragraph.content:
                continue
            if paragraph.role == 'pageFooter' or paragraph.role == 'pageNumber':
                continue
            
            is_subheader = paragraph in self.subheadings
            
            is_in_table, table = self.is_paragraph_in_table(paragraph.span)
            if is_in_table:
                if table in self.processed_tables:
                    continue
                current_chunk.add_document_object(table)
                self.processed_tables.add(table)
            
            # Determine if a new chunk should start
            start_new_chunk = False
            if is_subheader:
                if not last_found_was_header and found_subheader:
                    start_new_chunk = True
                found_subheader = True
            elif not found_subheader and len(current_chunk.content) >= max_chunk_size:
                # print("Exceeded max chunk size")
                start_new_chunk = True
                
            # print(f"{start_new_chunk} - {paragraph.content} - {is_subheader}")
            
            # Start a new chunk if required
            if start_new_chunk:
                if current_chunk.content:  # Check if there's content to be finalized
                    self.finalize_chunk(current_chunk, document_flow)
                current_chunk = DocumentChunk()
            
            # Directly add paragraph to the chunk
            if not is_in_table:
                current_chunk.add_document_object(paragraph)
            
            last_found_was_header = is_subheader
            
        # Finalize the last chunk
        if current_chunk.content:
            self.finalize_chunk(current_chunk, document_flow)

        return document_flow
