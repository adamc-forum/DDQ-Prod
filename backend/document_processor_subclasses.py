from document_processor import DocumentProcessor
from classes import DocumentFlow, DocumentChunk, CleanedParagraph
from typing import Union
import copy
import re

from docx.document import Document as DocumentType
from docx.table import Table
from docx.text.paragraph import Paragraph

from document_parser_utils import remove_non_alphanumeric


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
            '10. Environmental, Social and Governance ("ESG")',
            "11. Track Record",
            "12. Accounting, Valuation and Reporting",
            "13. Legal and Administration",
            '14. Information Technology ("IT"), Cyber and Physical Security',
            "15. Disaster Recovery and Business Continuity Plans",
            "16. Important Information for DDQ Recipients",
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
            if paragraph.role == "pageFooter" or paragraph.role == "pageNumber":
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
                    current_chunk = self.prepend_headers_to_chunk(
                        current_chunk, current_heading=current_heading
                    )
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
            regex_pattern=r"^([0-9]+|[a-zA-Z])[.)]",
            avoid_spans=table_spans,
        )
        return subheadings


class OMProcessor(DocumentProcessor):
    def __init__(self, document_parser, filename, document: DocumentType):
        super().__init__(document_parser, filename)
        [
            self.level_1_headings,
            self.level_2_headings,
            self.level_3_headings,
        ] = self.get_subheadings(document)

    def get_subheadings(self, document: DocumentType):
        level_1_headers_styles = ["Standard_L1", "Legal1_L1", "Appendix 1_L1"]
        level_2_headers_styles = ["Legal1_L2", "%Heading=Left+Bold", "Standard_L2"]
        level_3_headers_styles = ["Legal1_L3"]

        level_1_headers = []
        level_2_headers = []
        level_3_headers = []

        heading_hierarchy = []

        for paragraph in document.paragraphs():
            text = paragraph.text.strip().lower()
            style_name = paragraph.style.name
            if (
                style_name in level_1_headers_styles
                or style_name in level_2_headers_styles
                or style_name in level_3_headers_styles
            ) and (len(text.split()) < 15):
                cleaned_text = remove_non_alphanumeric(text)

                if style_name in level_1_headers_styles:
                    level_1_headers.append(
                        (cleaned_text, 1, copy.deepcopy(heading_hierarchy))
                    )
                    heading_hierarchy = [cleaned_text]
                elif (
                    style_name in level_2_headers_styles and len(heading_hierarchy) >= 1
                ):
                    level_2_headers.append(
                        (cleaned_text, 2, copy.deepcopy(heading_hierarchy))
                    )
                    heading_hierarchy = [heading_hierarchy[0], cleaned_text]
                elif (
                    style_name in level_3_headers_styles and len(heading_hierarchy) >= 2
                ):
                    level_3_headers.append(
                        (cleaned_text, 3, copy.deepcopy(heading_hierarchy))
                    )
                    heading_hierarchy = [
                        heading_hierarchy[0],
                        heading_hierarchy[1],
                        cleaned_text,
                    ]

        return [level_1_headers, level_2_headers, level_3_headers]

    def find_subheading(self, cleaned_paragraph, current_hierarchy):
        candidate_headings = []
        for heading, level, hierarchy in (
            self.level_1_headings + self.level_2_headings + self.level_3_headings
        ):
            if re.match(f"^{re.escape(heading)}", cleaned_paragraph):
                candidate_headings.append((heading, level, hierarchy))

        # Find the heading whose hierarchy context matches the current hierarchy
        # Purpose of comparing heading hierarchies is to handle duplicate headings
                
        for candidate in candidate_headings:
            candidate_hierarchy = candidate[2]
            if current_hierarchy == candidate_hierarchy or not current_hierarchy:
                return candidate

        return None

    def process_document(self):
        document_flow = DocumentFlow(self.filename)
        current_chunk = DocumentChunk()
        heading_hierarchy = []
        cleaned_heading_hierarchy = []
        for paragraph in self.cleaned_paragraphs:
            if paragraph.role == "pageFooter" or paragraph.role == "pageNumber":
                continue
            cleaned_paragraph = (
                remove_non_alphanumeric(paragraph.content).lower().strip()
            )

            subheading = self.find_subheading(
                cleaned_paragraph, cleaned_heading_hierarchy
            )
            if subheading:
                if current_chunk.content:
                    current_chunk.content = f"Context Heading Tags: {','.join(heading_hierarchy)} | Content: {current_chunk.content}"
                    current_chunk = self.prepend_headers_to_chunk(current_chunk)
                    self.finalize_chunk(current_chunk, document_flow)
                current_chunk = DocumentChunk()

                if subheading[1] == 1:
                    heading_hierarchy = [paragraph.content]
                    cleaned_heading_hierarchy = [cleaned_paragraph]
                elif subheading[1] == 2:
                    if len(cleaned_heading_hierarchy) > 0:
                        heading_hierarchy = [heading_hierarchy[0], paragraph.content]
                        cleaned_heading_hierarchy = [
                            cleaned_heading_hierarchy[0],
                            cleaned_paragraph,
                        ]
                elif subheading[1] == 3:
                    if len(cleaned_heading_hierarchy) > 1:
                        heading_hierarchy = [
                            heading_hierarchy[0],
                            heading_hierarchy[1],
                            paragraph.content,
                        ]
                        cleaned_heading_hierarchy = [
                            cleaned_heading_hierarchy[0],
                            cleaned_heading_hierarchy[1],
                            cleaned_paragraph,
                        ]
            else:
                is_in_table, table = self.is_paragraph_in_table(paragraph.span)
                if is_in_table:
                    if table not in self.processed_tables:
                        current_chunk.add_document_object(table)
                        self.processed_tables.add(table)
                    continue  # Skip to next paragraph after handling the table
                current_chunk.add_document_object(paragraph)

        # Finalize the last chunk
        if current_chunk.content:
            current_chunk.content = f"Context Heading Tags: {','.join(heading_hierarchy)} | Content: {current_chunk.content}"
            self.prepend_headers_to_chunk(current_chunk)
            self.finalize_chunk(current_chunk, document_flow)

        return document_flow


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
            regex_pattern=r"^([0-9]+|[a-zA-Z])[.)]",
            avoid_spans=table_spans,
        )
        return subheadings

    def process_document(self):
        document_flow = DocumentFlow(self.filename)
        current_chunk = DocumentChunk()
        max_chunk_size = 750  # Adjust the chunk size as needed
        found_subheader = False
        last_found_was_header = False

        for paragraph in self.cleaned_paragraphs:
            if paragraph.role == "pageFooter" or paragraph.role == "pageNumber":
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


class ClientResponseProcessor(DocumentProcessor):
    def __init__(self, document_parser, filename, document: DocumentType):
        super().__init__(document_parser, filename)
        [self.level_1_headings, self.level_2_headings] = self.get_subheadings(document)

    def get_subheadings(self, document: DocumentType):
        level_1_headers_styles = ["Heading 1"]
        level_2_headers_styles = ["Heading 2"]

        level_1_headers = []
        level_2_headers = []

        heading_hierarchy = []

        for paragraph in document.paragraphs:
            cleaned_text = remove_non_alphanumeric(paragraph.text.strip().lower())
            style_name = paragraph.style.name
            if not cleaned_text: 
                continue
            if (
                style_name in level_1_headers_styles
                or style_name in level_2_headers_styles
            ):
                if style_name in level_1_headers_styles:
                    level_1_headers.append(
                        (cleaned_text, 1, copy.deepcopy(heading_hierarchy))
                    )
                    heading_hierarchy = [cleaned_text]
                elif (
                    style_name in level_2_headers_styles
                    and len(heading_hierarchy) >= 1
                ):
                    level_2_headers.append(
                        (cleaned_text, 2, copy.deepcopy(heading_hierarchy))
                    )
                    heading_hierarchy = [heading_hierarchy[0], cleaned_text]

        return [level_1_headers, level_2_headers]

    def find_subheading(self, cleaned_paragraph):
        candidate_headings = []
        for heading, level, hierarchy in self.level_1_headings + self.level_2_headings:
            heading_re_pattern = rf"^(?:\d+|[a-zA-Z])?\s*{re.escape(heading)}"
            if re.match(heading_re_pattern, cleaned_paragraph):
                candidate_headings.append((heading, level, hierarchy))

        # Required for dealing with duplicate headings
        # Commented out for client response documents as duplicate headings are very unlikely
        # More appropriate for larger documents like OM
        
        # for candidate in candidate_headings:
        #     candidate_hierarchy = candidate[2]
        #     print(candidate_hierarchy, current_hierarchy)
        #     if current_hierarchy == candidate_hierarchy or not current_hierarchy:
        #         return candidate

        return candidate_headings[0] if candidate_headings else None

    def process_document(self):
        document_flow = DocumentFlow(self.filename)
        current_chunk = DocumentChunk()
        heading_hierarchy = []
        cleaned_heading_hierarchy = []
        found_subheading = False
        for paragraph in self.cleaned_paragraphs:
            if paragraph.role == "pageFooter" or paragraph.role == "pageNumber":
                continue
            cleaned_paragraph = (
                remove_non_alphanumeric(paragraph.content).lower().strip()
            )
            subheading = self.find_subheading(
                cleaned_paragraph
            )

            if subheading:
                found_subheading = True
                if current_chunk.content:
                    current_chunk.content = f"Context Heading Tags: {','.join(heading_hierarchy)} | Content: {current_chunk.content}"
                    current_chunk = self.prepend_headers_to_chunk(current_chunk)
                    self.finalize_chunk(current_chunk, document_flow)
                current_chunk = DocumentChunk()

                # subheading[1] is the heading level
                if subheading[1] == 1:
                    heading_hierarchy = [paragraph.content]
                elif subheading[1] == 2:
                    if len(cleaned_heading_hierarchy) > 0:
                        heading_hierarchy = [heading_hierarchy[0], paragraph.content]
            else:
                if not found_subheading:
                    continue
                is_in_table, table = self.is_paragraph_in_table(paragraph.span)
                if is_in_table:
                    if table not in self.processed_tables:
                        current_chunk.add_document_object(table)
                        self.processed_tables.add(table)
                    continue  # Skip to next paragraph after handling the table
                current_chunk.add_document_object(paragraph)

        # Finalize the last chunk
        if current_chunk.content:
            current_chunk.content = f"Context Heading Tags: {','.join(heading_hierarchy)} | Content: {current_chunk.content}"
            self.prepend_headers_to_chunk(current_chunk)
            self.finalize_chunk(current_chunk, document_flow)

        return document_flow
