import math
import re

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

def remove_non_alphanumeric(s: str):
    return re.sub(r'[^a-zA-Z0-9]', '', s)