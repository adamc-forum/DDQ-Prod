from dotenv import load_dotenv
from embeddings import (
    generate_embeddings
)

import numpy as np
from datetime import datetime

from functions import (
    get_openai_client,
    get_service_management_client,
    get_models,
    get_db_client, 
    get_document_url
)

from document_parser import (
    DocumentParser
)

from document_processor_subclasses import (
    ClientResponseProcessor
)

from embeddings import convert_chunks_to_json

from azure.ai.formrecognizer import DocumentAnalysisClient, AnalysisFeature, AnalyzeResult, DocumentParagraph
from azure.core.credentials import AzureKeyCredential

load_dotenv()

def cosine_similarity(vec1, vec2):
    dot_product = np.dot(vec1, vec2)
    norm_vec1 = np.linalg.norm(vec1)
    norm_vec2 = np.linalg.norm(vec2)
    return dot_product / (norm_vec1 * norm_vec2)


def vector_search(query: str, result_count: int):
    embeddings_model, completions_model = get_models()
    collection = get_db_client().collection
    open_ai_client = get_openai_client()
    query_embedding = generate_embeddings(query, open_ai_client,
                                          embeddings_model)

    pipeline = [{
        '$search': {
            "cosmosSearch": {
                "vector": query_embedding,
                "path": "contentVector",
                "k": result_count
            },
            "returnStoredSource": True
        }
    }, {
        '$project': {
            'similarityScore': {
                '$meta': 'searchScore'
            },
            'document': '$$ROOT'
        }
    }]

    # Apply search pipeline on filtered documents
    results = list(collection.aggregate(pipeline))

    response_list = []
    for result in results:
        response = {}
        response['similarityScore'] = result['similarityScore']
        response['page'] = result['document']['page']
        response['content'] = result['document']['content']
        response['clientName'] = result['document']['clientName']
        response['date'] = result['document']['date']
        response['documentName'] = result['document']['documentName']
        response['id'] = result['document']['id']
        response['url'] = get_document_url(
            client_name=result['document']['clientName'][0],
            document_name=result['document']['documentName'][0],
            date=result['document']['date'][0],
            page_number=result['document']['page'][0]
        )
        response_list.append(response)

    return response_list


def vector_search_by_client(query: str, result_count: int, client_names: list = None):
    embeddings_model, completions_model = get_models()
    collection = get_db_client().collection
    open_ai_client = get_openai_client()
    query_embedding = generate_embeddings(
        query, open_ai_client, embeddings_model)

    # Pre-filter based on ClientName
    filtered_documents = collection.find({'clientName': {'$in': client_names}})

    # Calculate cosine similarity and store results
    results = []
    for document in filtered_documents:
        similarity = cosine_similarity(
            document['contentVector'], query_embedding)
        document_with_score = document.copy()
        document_with_score['similarityScore'] = similarity
        results.append(document_with_score)

    # Sort results based on similarity score in descending order
    results.sort(key=lambda x: x['similarityScore'], reverse=True)

    # Take the top result_count results
    top_results = results[:result_count]

    response_list = []
    for result in top_results:
        response = {}
        response['similarityScore'] = result['similarityScore']
        response['page'] = result['page']
        response['content'] = result['content']
        response['clientName'] = result['clientName']
        response['date'] = result['date']
        response['documentName'] = result['documentName']
        response['id'] = result['id']
        response['url'] = get_document_url(
            client_name=result['clientName'][0],
            document_name=result['documentName'][0],
            date=result['date'][0],
            page_number=result['page'][0]
        )
        response_list.append(response)

    return response_list


def get_distinct_client_names():
    collection = get_db_client().collection
    pipeline = [
        {'$unwind': '$clientName'},
        {'$group': {'_id': '$clientName'}},
        {'$project': {'clientName': '$_id', '_id': 0}}
    ]
    results = collection.aggregate(pipeline)
    distinct_client_names = [result['clientName'] for result in results]
    return distinct_client_names


def get_distinct_client_document_date_combinations():
    collection = get_db_client().collection
    pipeline = [
        {
            '$group': {
                '_id': {
                    'clientName': '$clientName',
                    'documentName': '$documentName',
                    'date': '$date'
                }
            }
        },
        {
            '$project': {
                '_id': 0,
                'clientName': '$_id.clientName',
                'documentName': '$_id.documentName',
                'date': '$_id.date'
            }
        }
    ]
    results = collection.aggregate(pipeline)
    distinct_combinations = [
        {
            'clientName': result['clientName'][0],
            'documentName': result['documentName'][0], 
            'date': result['date'][0],
            'url': get_document_url(result['clientName'][0], result['documentName'][0], result['date'][0])
        } 
        for result in results]
    return distinct_combinations


def generate_completion(query: str, result_count: int, client_names: list = None, word_limit: int = 300):
    client_names = client_names[0].split(',')
    if (len(client_names) == len(get_distinct_client_names())):
        response_list = vector_search(query, result_count)
    else:
        response_list = vector_search_by_client(query, result_count, client_names)

    system_prompt = f'''
    Your are a financial advisor for a real estate investment fund called REIIF.
    Your purpose is to confidently answer due diligence queries about REIIF.
    You must create a comprehensive, relevant answer to the user's query using only the information provided.
    The information provided are excerpts from documents about REIIF.
    You must only utilize relevant details from the provided information to create your answer.
    Your tone and length must be consistent with that of the information provided.
    The word limit is {word_limit}.
    '''

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Due Diligence Query: {query}"},
    ]

    for index, item in enumerate(response_list):
        messages.append({"role": "system", "content": f"REIIF Documents Excerpt {index}: {item['content'][0]}"})

    embeddings_model, completions_model = get_models()

    openai_client = get_openai_client()
    completion_response = openai_client.chat.completions.create(
        model=completions_model,
        messages=messages,
        temperature=0
    )
    return (completion_response.choices[0].message.content, response_list[:result_count])


def get_parsed_pdf(file_content: bytes, endpoint: str, api_key: str) -> DocumentParser:
    document_analysis_client = DocumentAnalysisClient(
        endpoint=endpoint, credential=AzureKeyCredential(api_key)
    )
    poller = document_analysis_client.begin_analyze_document("prebuilt-layout", file_content, features=[AnalysisFeature.STYLE_FONT])
    result: AnalyzeResult = poller.result()

    return DocumentParser(result=result)


async def get_vectorized_chunks(document_parser: DocumentParser, filename: str, document, in_prod=False):
    openai_client = get_openai_client()
    embedding_model, completions_model = get_models()
    client_response_processor = ClientResponseProcessor(document_parser, filename, document)
    document_flow = client_response_processor.process_document()
    vectorized_chunks = await convert_chunks_to_json(
        document_flow.chunks, openai_client, embedding_model, in_prod
    )
    return vectorized_chunks

def add_documents_to_db(vectorized_chunks) -> bool:
    try:
        db_client = get_db_client()
        db_client.add_data_to_collection(vectorized_chunks)
        return True
    except Exception as e:
        return False