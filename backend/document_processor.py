from classes import (
    DocumentChunk,
    DocumentFlow
)

from typing import Tuple

from document_parser import DocumentParser

from document_parser_utils import is_similar_color

class DocumentProcessor:
    def __init__(self, document_parser, filename):
        self.filename = filename
        self.document_parser: DocumentParser = document_parser
        self.cleaned_paragraphs = self.document_parser.extract_cleaned_paragraphs()
        self.cleaned_tables = self.document_parser.extract_cleaned_tables()
        self.cleaned_font_weights = self.document_parser.extract_cleaned_font_weights()
        self.cleaned_font_colors = self.document_parser.extract_cleaned_font_colors()
        self.table_and_table_spans = [(table.span, table) for table in self.cleaned_tables]
        self.processed_tables = set()  # Track processed tables

    def process_document(self):
        # Default processing logic
        document_flow = DocumentFlow()
        current_chunk = DocumentChunk()
        max_chunk_size = 750  # Characters threshold for a chunk

        for paragraph in self.cleaned_paragraphs:
            if paragraph.role in ['pageFooter', 'pageNumber']:
                continue

            is_in_table, table = self.is_paragraph_in_table(paragraph.span)
            if is_in_table:
                if table not in self.processed_tables:
                    current_chunk = self.add_content_to_chunk(table, current_chunk, document_flow, max_chunk_size)
                    self.processed_tables.add(table)
                continue
            current_chunk = self.add_content_to_chunk(paragraph, current_chunk, document_flow, max_chunk_size)

        self.finalize_chunk(current_chunk, document_flow)
        return document_flow

    def is_paragraph_in_table(self, paragraph_span):
        for span, table in self.table_and_table_spans:
            if span[0] <= paragraph_span[0] < span[0] + span[1]:
                return True, table
        return False, None

    def handle_table(self, paragraph_span, current_chunk, document_flow):
        for span, table in self.table_and_table_spans:
            if span[0] <= paragraph_span[0] < span[0] + span[1]:
                if table not in current_chunk.tables:
                    self.finalize_chunk(current_chunk, document_flow)
                    current_chunk = DocumentChunk()
                    current_chunk.add_document_object(table)
        return current_chunk

    def add_content_to_chunk(self, content, current_chunk: DocumentChunk, document_flow: DocumentFlow, max_chunk_size):
        if len(current_chunk.content) + len(content.content) > max_chunk_size:
            self.finalize_chunk(current_chunk, document_flow)
            current_chunk = DocumentChunk()
        current_chunk.add_document_object(content)
        return current_chunk

    def prepend_headers_to_chunk(self, current_chunk: DocumentChunk, current_heading: str = "", current_subheading: str = "") -> DocumentChunk:
        heading = f"Section {current_heading}: " if current_heading else ""
        subheading = f"Subsection {current_subheading}: " if current_subheading else ""
        current_chunk.content = heading + subheading + current_chunk.content
        return current_chunk

    def finalize_chunk(self, chunk, document_flow, min_words_threshold=12):
        if len(chunk.content.split()) >= min_words_threshold:  # Add the chunk if it contains any content
            document_flow.add_chunk(chunk)

    def get_bold_spans(self):
        bold_spans = []
        for font_weight in self.cleaned_font_weights:
            if font_weight.weight == 'bold':
                bold_spans.extend(font_weight.span)
        return bold_spans

    def get_color_spans(self, color):
        color_spans = []
        for font_color in self.cleaned_font_colors:
            if is_similar_color(color, font_color.color):
                color_spans.extend(font_color.span)
        return color_spans