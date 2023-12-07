from dotenv import load_dotenv
from embeddings import (
    generate_embeddings
)

from functions import (
    get_openai_client,
    get_service_management_client,
    get_models,
    get_db_client
)

# Load environment variables
load_dotenv()

# Simple function to assist with vector search
def vector_search(query: str):
    embeddings_model, completions_model = get_models()
    collection = get_db_client().collection
    open_ai_client = get_openai_client()
    query_embedding = generate_embeddings(query, open_ai_client, embeddings_model)
    pipeline = [
        {
            '$search': {
                "cosmosSearch": {
                    "vector": query_embedding,
                    "path": "contentVector",
                    "k": 5
                },
                "returnStoredSource": True }},
        {'$project': { 'similarityScore': { '$meta': 'searchScore' }, 'document' : '$$ROOT' } }
    ]
    results = collection.aggregate(pipeline)
    return results

def generate_completion(query: str):
    results = vector_search(query)
    response_list = []
    for result in results:
        response = {}
        response['similarityScore'] = result['similarityScore']
        response['page'] = result['document']['page']
        response['content'] = result['document']['content']
        response['filename'] = result['document']['filename']
        response_list.append(response)
    
    system_prompt = '''
    Your are a financial advisor for a real estate invesment fund called REIIF.
    Your purpose is to confidently answer due dilligence inquiries about REIIF.
    You must create a comprehensive and relevant answer to the user's query using only the information provided.
    The information to be provided are sections of internal finance documents about REIIF.
    You must utilize relevant details from the provided information to create your answer.
    Your tone and length must be consistent with that of the information about to be provided.
    '''
    
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": query},
    ]
    
    for item in response_list:
        messages.append({"role": "system", "content": item['content'][0]})
    
    embeddings_model, completions_model = get_models() 
    
    openai_client = get_openai_client()
    completion_response = openai_client.chat.completions.create(
        model=completions_model,
        messages=messages,
        temperature=0
    )
    print(completion_response.choices[0])
    return (completion_response.choices[0].message.content, response_list)
    
