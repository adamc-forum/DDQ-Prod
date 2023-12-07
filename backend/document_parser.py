from azure.ai.formrecognizer import AnalyzeResult, DocumentTable, DocumentParagraph, DocumentStyle
from classes import DocumentChunk, DocumentFlow
from document_parser_utils import (
    is_similar_color,
    is_start_in_range
)
from collections import defaultdict
from classes import (
    CleanedTable,
    CleanedParagraph,
    CleanedFontWeight,
    CleanedFontColor
)
from typing import Callable
import re

class DocumentParser:

    def __init__(self, result, start_page=1, end_page=None):

        # if not isinstance(result, AnalyzeResult):
        #     raise ValueError(
        #         f"Document Parser input must be of type AnalyzeResult. Got type {type(result)}.")

        if result.pages is None or len(result.pages) == 0:
            raise ValueError(
                "Document Parser input does not contain any pages")

        self.result = result
        self.pages = result.pages
        self.start_page = start_page
        self.end_page = end_page if end_page is not None else len(self.result.pages)

        if not (1 <= self.start_page <= self.end_page <= len(self.result.pages)):
            raise ValueError(
                f"Invalid start_page or end_page value. Got {self.start_page} and {self.end_page}")

        self.paragraphs = [p for p in self.result.paragraphs if self.start_page <=
                           p.bounding_regions[0].page_number <= self.end_page]
        self.tables = [t for t in self.result.tables if self.start_page <=
                       t.bounding_regions[0].page_number <= self.end_page]
        self.styles = self.result.styles
        self.font_colors, self.font_weights = defaultdict(list), defaultdict(list)
        self.setup_styles()

    def setup_styles(self):
        for style in self.styles:
            if style.font_weight:
                self.font_weights[style.font_weight].append(style)
            if style.color:
                self.font_colors[style.color].append(style)

    def extract_cleaned_paragraphs(self, paragraphs: list[DocumentParagraph] = None) -> list[CleanedParagraph]:
        paragraphs = paragraphs if paragraphs is not None else self.paragraphs
        cleaned_paragraphs: list[CleanedParagraph] = []
        for paragraph in paragraphs:
            cleaned_paragraphs.append(
                CleanedParagraph(
                    content=paragraph.content,
                    role=paragraph.role,
                    page=paragraph.bounding_regions[0].page_number,
                    span=(paragraph.spans[0].offset, paragraph.spans[0].length)
                )
            )
        return cleaned_paragraphs
    
    def table_cells_to_rows(self, table: DocumentTable):
        all_rows = []
        current_row_number = 0
        current_row = []
        for cell in table.cells:
            if cell.row_index > current_row_number:
                all_rows.append(current_row)
                current_row = []
                current_row_number = cell.row_index
            current_row.append(cell)

        all_rows.append(current_row)
        return all_rows

    def extract_cleaned_tables(self, tables: list[DocumentTable] = None) -> list[CleanedTable]:
        tables = tables if tables is not None else self.tables
        cleaned_tables: list[CleanedTable] = []
        for table_idx, table in enumerate(tables):
            table_header = f"Table {table_idx}"
            table_rows = self.table_cells_to_rows(table)
            column_headers = [f"column{i+1}" for i in range(table.column_count)]
            current_row = []
            all_rows = []
            parsed_successfully = True
            try:
                for row_index, row in enumerate(table_rows):
                    for cell in row:
                        if 'header' in cell.kind.lower():
                            if cell.column_span == table.column_count:
                                table_header = cell.content
                                # print(f"Found Table Header: {table_header}")
                                break
                            if cell.column_span == 1:
                                column_headers = [cell.content for cell in row]
                                # print(f"Found Column Headers: {column_headers}")
                                break
                        if 'content' in cell.kind.lower():
                            current_row = [
                                f"{column_headers[index] if column_headers[index] else f'column{index+1}'} is {row_cell.content}," 
                                for index, row_cell in enumerate(row)
                            ]
                            all_rows.append(
                                f"For row {row_index}, {''.join(current_row)}")
                            break
            except Exception as e:
                parsed_successfully = False
                print(f"Failed to parse table {table_header} on page {table.bounding_regions[0].page_number}")
                
            if parsed_successfully:
                all_rows = f"For \"{table_header}\": {'.'.join(all_rows)}"
                cleaned_tables.append(
                    CleanedTable(
                        content=all_rows,
                        page=table.bounding_regions[0].page_number,
                        span=(table.spans[0].offset, table.spans[0].length)
                    )
                )
        return cleaned_tables

    def extract_cleaned_font_weights(self, font_weights: dict[str, list[DocumentStyle]] = None) -> list[CleanedFontWeight]:
        font_weights = font_weights if font_weights is not None else self.font_weights
        cleaned_font_weights = []
        for font_weight, styles in font_weights.items():
            cleaned_font_weights.append(
                CleanedFontWeight(
                    weight=font_weight,
                    span=[(span.offset, span.length)
                          for style in styles for span in style.spans]
                )
            )
        return cleaned_font_weights

    def extract_cleaned_font_colors(self, font_colors: dict[str, list[DocumentStyle]] = None) -> list[CleanedFontColor]:
        font_colors = font_colors if font_colors is not None else self.font_colors
        cleaned_font_colors = []
        for font_weight, styles in font_colors.items():
            cleaned_font_colors.append(
                CleanedFontColor(
                    color=font_weight,
                    span=[(span.offset, span.length)
                          for style in styles for span in style.spans]
                )
            )
        return cleaned_font_colors

    def get_matching_color_spans(
        self,
        color,
        font_colors: list[CleanedFontColor],
        matching_function: Callable[[str, str], bool] = None
    ):
        if matching_function is None:
            matching_function = lambda x, y: x == y
        matching_spans = []
        for font_color in font_colors:
            if matching_function(color, font_color.color):
                matching_spans.extend(font_color.span)
    
        return matching_spans
    
    def get_matching_weight_spans(self, weight, font_weights: list[CleanedFontWeight]):
        matching_spans = []
        for font_weight in font_weights:
            if weight == font_weight.weight:
                matching_spans.extend(font_weight.span)
        return matching_spans
    
    def get_matching_paragraphs(
        self, 
        span_groups: list[list[tuple[int, int]]], 
        min_words = 0,
        paragraphs: list[CleanedParagraph] = None,
        regex_pattern: str = None,
        avoid_spans: list(tuple[int, int]) = None  
    ):
        matching_paragraphs = []
        for paragraph in paragraphs:
            paragraph_start = paragraph.span[0]
            if any(span[0] <= paragraph_start < span[0] + span[1] for span in avoid_spans):
                continue
            if all(is_start_in_range(paragraph_start, spans) for spans in span_groups):
                if len(paragraph.content.split(" ")) >= min_words:
                    if regex_pattern:
                        if re.search(regex_pattern, paragraph.content):
                            matching_paragraphs.append(paragraph)
                    else:
                        matching_paragraphs.append(paragraph)
        return matching_paragraphs

    