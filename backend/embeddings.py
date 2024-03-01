import json
import copy
from datetime import datetime
from classes import (
    DocumentChunk
)

from tenacity import retry, wait_random_exponential, stop_after_attempt
import time
    
@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(5))
def generate_embeddings(text, client, model="text-embedding-ada-002"): # model = "deployment_name"
    '''
    Generate embeddings from string of text.
    This will be used to vectorize data and user input for interactions with Azure OpenAI.
    '''
    time.sleep(0.5) # rest period to avoid rate limiting on AOAI for free tier
    return client.embeddings.create(input = [text], model=model).data[0].embedding

async def convert_chunks_to_json(chunks: list[DocumentChunk], client, embedding_model):
    items = []
    n = 0
    title_embeddings = None
    for chunk in chunks:
        item = {}
        n += 1
        content_embeddings = generate_embeddings(chunk.content, client, embedding_model)
        item['id'] = chunk.id,
        item['clientName'] = chunk.client_name,
        item['documentName'] = chunk.document_name,
        item['date'] = chunk.date,
        item['page'] = chunk.page_number,
        item['content'] = chunk.content,
        item['contentVector'] = content_embeddings
        item['@search.action'] = 'upload'
        print("Creating embeddings for item:", n, "/", len(chunks), end='\r')
        items.append(item)

    items_json = copy.deepcopy(items)

    # Convert the 'date' field in the copied list from datetime to string
    for item in items_json:
        item['date'] = item['date'][0].strftime('%Y-%m-%d %H:%M:%S')
    
    with open(f"{chunks[0].client_name}_{chunks[0].document_name}_parsing_vectorized_backup.json", "w") as f:
        json.dump(items_json, f)
    
    return items
