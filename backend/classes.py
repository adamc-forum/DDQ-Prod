from constants import TARGET_PDF_PATH
from typing import Union
from datetime import datetime

class CleanedTable:
    def __init__(self, content, page, span):
        self.content = content
        self.page = page
        self.span = span

    def __repr__(self):
        return f"CleanedTable(content={self.content}, page={self.page}, span={self.span})"
    
class CleanedParagraph:
    def __init__(self, content, role, page, span):
        self.content = content
        self.role = role
        self.page = page
        self.span = span

    def __repr__(self):
        return f"CleanedParagraph(content={self.content}, page={self.page}, role={self.role}, span={self.span})"

class CleanedFontWeight:
    def __init__(self, weight: str, span: list[tuple[int, int]]):
        self.weight = weight
        self.span = span

    def __repr__(self):
        return f"CleanedFontWeight(weight={self.weight}, span={self.span})"

class CleanedFontColor:
    def __init__(self, color: str, span: list[tuple[int, int]]):
        self.color = color
        self.span = span

    def __repr__(self):
        return f"CleanedFontColor(color={self.color}, span={self.span})"

class DocumentChunk:
    def __init__(self):
        self.document_objects = []
        self.paragraphs = []
        self.tables = []
        self.page_number = None
        self.content = ""
        self.id: datetime = None
        self.date = None
        self.client_name = ""
        self.document_name = ""

    def add_document_object(self, document_object: Union[CleanedParagraph, CleanedTable]):
        self.paragraphs.append(document_object) if isinstance(document_object, CleanedParagraph) else self.tables.append(document_object)
        self.document_objects.append(document_object)
        self.page_number = document_object.page
        self.content += document_object.content

class DocumentFlow:
    def __init__(self, filename):
        self.chunks: list[DocumentChunk] = []
        self.filename = filename
        self.client_name, self.document_name, self.date = self.parse_filename()
        # print(f"Classes.py - file metadata: {self.client_name, self.document_name, self.date}")
    
    def parse_filename(self):
        # Expected filename format is Forum Internal_Master DDQ_30-06-2023
        # <client_name>_<document_name>_<date>
        parts = self.filename.split('_')
        if len(parts) != 3:
            raise ValueError(f"Filename '{self.filename}' does not follow the expected format")

        client_name = parts[0].strip()
        document_name = parts[1].strip()
        date_str = parts[2].strip()
        
        try:
            date = datetime.strptime(date_str, "%d-%m-%Y")
        except ValueError:
            raise ValueError(f"Invalid date format in filename: {date_str}")

        return client_name, document_name, date

    def add_chunk(self, chunk: DocumentChunk):
        chunk.date = self.date
        chunk.client_name = self.client_name
        chunk.document_name = self.document_name
        chunk.id = f'{self.filename}_chunk_{len(self.chunks)}'
        self.chunks.append(chunk)
    
    def __str__(self):
        output = []
        for index, chunk in enumerate(self.chunks):
            output.append(f"Chunk: {index}, Client Name: {chunk.client_name}, Document Name: {chunk.document_name}, Page Number: {chunk.page_number}, Date: {chunk.date}\n{chunk.content}\n{'_' * 30}")
        return "\n".join(output)
    
    def to_dict(self) -> list[dict]:
        chunks_dicts_list = []
        for chunk in self.chunks:
            chunks_dicts_list.append({
                'id': chunk.id,
                'client_name': chunk.client_name,
                'document_name': chunk.document_name,
                'date': chunk.date.strftime('%Y-%m-%d %H:%M:%S'),
                'page_number': chunk.page_number,
                'content': chunk.content
            })
        return chunks_dicts_list
        
