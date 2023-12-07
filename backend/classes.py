from constants import TARGET_PDF_PATH
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
        self.page_number = 0
        self.content = ""
        self.filename = ""
        self.id = ""
        self.date = ""

    def add_document_object(self, document_object: CleanedParagraph | CleanedTable):
        self.paragraphs.append(document_object) if isinstance(document_object, CleanedParagraph) else self.tables.append(document_object)
        self.document_objects.append(document_object)
        self.page_number = document_object.page
        self.content += document_object.content

class DocumentFlow:
    def __init__(self, filename, date = datetime.now().isoformat):
        self.chunks: list[DocumentChunk] = []
        self.filename = filename
        self.date = date

    def add_chunk(self, chunk: DocumentChunk):
        chunk.filename = self.filename
        chunk.date = self.date
        chunk.id = f'{self.filename}_chunk_{len(self.chunks)}'
        self.chunks.append(chunk)
    
    def __str__(self):
        output = []
        for index, chunk in enumerate(self.chunks):
            output.append(f"Chunk: {index}, Page Number: {chunk.page_number}, Date: {chunk.date}\n{chunk.content}\n{'_' * 30}")
        return "\n".join(output)
    
    def to_dict(self) -> list[dict]:
        chunks_dicts_list = []
        for chunk in self.chunks:
            chunks_dicts_list.append({
                'id': chunk.id,
                'filename': chunk.filename,
                'page_number': chunk.page_number,
                'content': chunk.content
            })
        return chunks_dicts_list
        
