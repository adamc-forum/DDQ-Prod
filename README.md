# DDQ

## Deploying web app

The web app is deployed via the Fast API library. The frontend static files are hosted at the root path `/` whereas the search api is hosted at the `/search` route. THey were hosted via the same web app / root domain to avoid any CORS issues.

- The backend is effectively the root directory.

- If you make any changes to the frontend folder, build the folder via the `npm run build` command, copy the resulting `build` folder into the backend directory and rename it to `public`.

- To deploy the webapp, navigate to the backend directory

- `cd backend`

- Run the follow azure cli command to upload the files in the current directory (backend) to the web app. Ensure you are using a cmd shell.

- `az webapp up --name DDQ-Web-App --resource-group rg-duedilligence-shared-001 --plan DDQ-Web-App-Service-Plan --runtime "PYTHON|3.9"`

## Helpful Commands

To delete all documents in the database

`db_client.remove_data_from_collection(delete_all=True)`

Python datetime objects are not json serializable but dates must be uploaded in this format to MongoDB to enable native filtering by dates. If you need to rely on any backup json files, ensure you convert the stringified date to a datetime object first before uploading to MongoDB.

## Relevant Concepts

The Retrieval Augment Generation (RAG) architecture can be described as follows

![RAG diagram](https://truera.com/wp-content/uploads/2023/07/TruLens-Pinecone-Figure-1-1024x536.png)

- Vector Conversion: Both the text of source documents and user queries are turned into vectors using an embedding machine learning model.
- Finding Similar Texts: The system searches for source documents that are most similar to the user's query. It compares the vectors using methods like cosine similarity or Euclidean distance.
- Retrieval of Relevant Information: Based on this similarity search, the most relevant texts or document segments are selected.
- Answer Generation: These selected texts, along with the original query, are then given to a completion model.
- Creating the Final Answer: The model uses this information to produce a response that is accurate and relevant to the user's query, drawing directly from the content of the retrieved texts.

There are three types of models in Azure OpenAI

```python
completion = client.completions.create(
    model=gpt-35-turbo-instruct, # Must match custom deployment name chosen for model.
    prompt=<"prompt">
)

chat_completion = client.chat.completions.create(
    model="gpt-35-turbo", # model = "deployment_name".
    messages=<"messages">
)

embedding = client.embeddings.create(
    input = "<input>",
    model= "text-embedding-ada-002" # model = "deployment_name".
)
```

- Embeddings are about understanding and representing the meaning of text in a numerical format
- Completion models are about generating text based on a given prompt
- Chat models are specialized in conversational contexts and interactions

## Getting Started

[Azure OpenAI on your data (preview) | Microsoft Learn](https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/use-your-data?tabs=mongo-db#using-the-web-app) 

[CosmosDB MongoDB vCore Preparation Script | Github](https://github.com/microsoft/sample-app-aoai-chatGPT/blob/feature/2023-9/scripts/cosmos_mongo_vcore_data_preparation.py)

[Getting Started With Embeddings Python | Microsoft Learn](https://learn.microsoft.com/en-us/azure/ai-services/openai/tutorials/embeddings?tabs=python%2Ccommand-line)

[Azure OpenAI Service REST API reference | Microsoft Learn](https://learn.microsoft.com/en-us/azure/ai-services/openai/reference#azure-cosmos-db-for-mongodb-vcore)

## End to End Tutorial

[CosmosDB MongoDB vCore AzureOpenAI Tutorial | Github](https://github.com/microsoft/AzureDataRetrievalAugmentedGenerationSamples/blob/main/Python/CosmosDB-MongoDB-vCore/CosmosDB-MongoDB-vCore_AzureOpenAI_Tutorial.ipynb)

[Azure Search Vector Python Sample](https://github.com/Azure/azure-search-vector-samples/blob/main/demo-python/code/azure-search-vector-python-sample.ipynb)

## Supporting Documentation

[Azure OpenAI v1.0.0 Migration Guide](https://github.com/openai/openai-python/discussions/742)
