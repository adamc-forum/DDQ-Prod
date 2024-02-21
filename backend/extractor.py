from azure.ai.formrecognizer import DocumentAnalysisClient, AnalysisFeature, AnalyzeResult, DocumentParagraph
from azure.core.credentials import AzureKeyCredential
from collections import defaultdict
import pickle
import os

def analyze_layout(file_path, endpoint, api_key) -> AnalyzeResult:

    if os.path.exists('layout_backup.pkl'):
        print("Error: Unable to analyze document, 'layout_backup.pkl' file already exists.")
        return

    document_analysis_client = DocumentAnalysisClient(
        endpoint=endpoint, credential=AzureKeyCredential(api_key)
    )

    with open(file_path, "rb") as f:
        poller = document_analysis_client.begin_analyze_document(
                "prebuilt-layout", f.read(), features=[AnalysisFeature.STYLE_FONT])
        result: AnalyzeResult = poller.result()
    
    # For testing purposes, store layout object locally as a file
    # Layout object can be loaded back into code instead of making repeated api requests
    with open('layout_backup.pkl', 'wb') as file:
        pickle.dump(result, file)
    
    # Prints out relevant sections of document intelligence page analysis reuslt, for debugging
    
    # extract_pages(result)
    # extract_paragraphs(result)
    # extract_tables(result)
    # extract_styles(result)
    # extract_key_value_pairs(result)
    
    return result

def format_bounding_region(bounding_regions):
    if not bounding_regions:
        return "N/A"
    return ", ".join(
        f"Page #{region.page_number}: {format_polygon(region.polygon)}"
        for region in bounding_regions
    )

def format_polygon(polygon):
    if not polygon:
        return "N/A"
    return ", ".join(["[{}, {}]".format(p.x, p.y) for p in polygon])

def get_styled_text(styles, content):
    # Iterate over the styles and merge the spans from each style.
    spans = [span for style in styles for span in style.spans]
    spans.sort(key=lambda span: span.offset)
    return ','.join([content[span.offset : span.offset + span.length] for span in spans])

def extract_pages(result: AnalyzeResult):
    for page in result['pages']:
        print("----Analyzing layout from page #{}----".format(page.page_number))
        print(
            "Page has width: {} and height: {}, measured with unit: {}".format(
                page.width, page.height, page.unit
            )
        )

        for line_idx, line in enumerate(page.lines):
            words = line.get_words()
            print(
                "...Line # {} has word count {} and text '{}' within bounding box '{}'".format(
                    line_idx,
                    len(words),
                    line.content,
                    format_polygon(line.polygon),
                )
            )

            for word in words:
                print(
                    "......Word '{}' has a confidence of {}".format(
                        word.content, word.confidence
                    )
                )

        for selection_mark in page.selection_marks:
            print(
                "...Selection mark is '{}' within bounding box '{}' and has a confidence of {}".format(
                    selection_mark.state,
                    format_polygon(selection_mark.polygon),
                    selection_mark.confidence,
                )
            )
    print("----------------------------------------")

def extract_paragraphs(result: AnalyzeResult):         
    for paragraph in result['paragraphs']:
        print(
            "...Paragraph is {}".format(
                paragraph
            )
        )
    print("----------------------------------------")
        
def extract_tables(result: AnalyzeResult):         
    for table_idx, table in enumerate(result['tables']):
        print(
            "Table # {} has {} rows and {} columns".format(
                table_idx, table.row_count, table.column_count
            )
        )
        for region in table.bounding_regions:
            print(
                "Table # {} location on page: {} is {}".format(
                    table_idx,
                    region.page_number,
                    format_polygon(region.polygon),
                )
            )
        for cell in table.cells:
            print(
                "...Cell[{}][{}] has content '{}'".format(
                    cell.row_index,
                    cell.column_index,
                    cell.content,
                )
            )
            
            print(
                "...Cell[{}][{}] is of kind '{}' and spans rows '{}'".format(
                    cell.row_index,
                    cell.column_index,
                    cell.kind,
                    cell.column_span,
                )
            )
            
            for region in cell.bounding_regions:
                print(
                    "...content on page {} is within bounding box '{}'".format(
                        region.page_number,
                        format_polygon(region.polygon),
                    )
                )
    
    print("----------------------------------------")

def extract_styles(result: AnalyzeResult): 
    # DocumentStyle has the following font related attributes:
    similar_font_families = defaultdict(list)  # e.g., 'Arial, sans-serif
    font_styles = defaultdict(list)             # e.g, 'italic'
    font_weights = defaultdict(list)            # e.g., 'bold'
    font_colors = defaultdict(list)             # in '#rrggbb' hexadecimal format
    font_background_colors = defaultdict(list)  # in '#rrggbb' hexadecimal format

    if any([style.is_handwritten for style in result['styles']]):
        print("Document contains handwritten content")
    else:
        print("Document does not contain handwritten content")

    print("\n----Fonts styles detected in the document----")

    # Iterate over the styles and group them by their font attributes.
    for style in result['styles']:
        if style.similar_font_family:
            similar_font_families[style.similar_font_family].append(style)
        if style.font_style:
            font_styles[style.font_style].append(style)
        if style.font_weight:
            font_weights[style.font_weight].append(style)
        if style.color:
            font_colors[style.color].append(style)
        if style.background_color:
            font_background_colors[style.background_color].append(style)

    print(f"Detected {len(similar_font_families)} font families:")
    for font_family, styles in similar_font_families.items():
        print(f"- Font family: '{font_family}'")
        print(f"  Text: '{get_styled_text(styles, result['content'])}'")

    print(f"\nDetected {len(font_styles)} font styles:")
    for font_style, styles in font_styles.items():
        print(f"- Font style: '{font_style}'")
        print(f"  Text: '{get_styled_text(styles, result['content'])}'")

    print(f"\nDetected {len(font_weights)} font weights:")
    for font_weight, styles in font_weights.items():
        print(f"- Font weight: '{font_weight}'")
        print(f"  Text: '{get_styled_text(styles, result['content'])}'")

    print(f"\nDetected {len(font_colors)} font colors:")
    for font_color, styles in font_colors.items():
        print(f"- Font color: '{font_color}'")
        print(f"  Text: '{get_styled_text(styles, result['content'])}'")

    print(f"\nDetected {len(font_background_colors)} font background colors:")
    for font_background_color, styles in font_background_colors.items():
        print(f"- Font background color: '{font_background_color}'")
        print(f"  Text: '{get_styled_text(styles, result['content'])}'")

    print("----------------------------------------")

def extract_key_value_pairs(result: AnalyzeResult):     
    for idx, kvp in enumerate(result['key_value_pairs']):    
        print(f"Key-Value Pair {idx + 1}:")
        print(f"\tKey: {kvp.key.content}")
        print(f"\tValue: {kvp.value.content if kvp.value else None}")
    print("----------------------------------------")
