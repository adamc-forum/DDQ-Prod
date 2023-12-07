import math
from classes import (
    DocumentFlow, DocumentChunk
)

def hex_to_rgb(hex_color):
    """Converts a hex color string to an RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def color_distance(rgb1, rgb2):
    """Calculates the Euclidean distance between two RGB colors."""
    return math.sqrt(sum((c1 - c2) ** 2 for c1, c2 in zip(rgb1, rgb2)))

def is_similar_color(reference_color, comparison_color, threshold=30):
    """Checks if a comparison color is similar to the reference color within a given threshold."""
    ref_rgb = hex_to_rgb(reference_color)
    comp_rgb = hex_to_rgb(comparison_color)

    return color_distance(ref_rgb, comp_rgb) <= threshold

def is_start_in_range(start, ranges):
    """Checks if the start of a span is within any of the provided ranges."""
    for range_start, length in ranges:
        range_end = range_start + length
        if range_start <= start <= range_end:
            return True
    return False

def add_chunk_and_initialize_new(current_chunk: DocumentChunk, document_flow: DocumentFlow, min_words_threshold=8):
    try:
        current_content = ''.join(current_chunk.content.split(':')[1:]).split(' ')
    except:
        print(F"WARNING: Encountered chunk {current_chunk.content} with only {len(current_content)} chunks")
        current_content = []
    if current_chunk.paragraphs and len(current_content) >= min_words_threshold:  # Check if the current chunk has content before adding
        document_flow.add_chunk(current_chunk)
    return DocumentChunk()