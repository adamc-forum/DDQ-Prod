from azure.identity import DefaultAzureCredential
from azure.mgmt.cognitiveservices import CognitiveServicesManagementClient
from openai import AzureOpenAI
import requests

from constants import (
    SUBSCRIPTION_ID,
    OPENAI_API_VERSION,
    OPENAI_API_KEY,
    OPENAI_API_ENDPOINT,
    RG_NAME,
    ACCOUNT_NAME,
    CONNECTION_STRING,
    DATABASE_NAME,
    COLLECTION_NAME
)

from database import (
    DatabaseClient
)


def get_service_management_client():
    return CognitiveServicesManagementClient(
        credential=DefaultAzureCredential(),
        subscription_id=SUBSCRIPTION_ID
    )


def get_openai_client() -> AzureOpenAI:
    return AzureOpenAI(
        api_version=OPENAI_API_VERSION,
        api_key=OPENAI_API_KEY,
        azure_endpoint=OPENAI_API_ENDPOINT
    )


def get_db_client() -> DatabaseClient:
    return DatabaseClient(
        connection_string=CONNECTION_STRING,
        database_name=DATABASE_NAME,
        collection_name=COLLECTION_NAME
    )


def get_models() -> tuple[str, str]:
    service_management_client = get_service_management_client()
    deployments = service_management_client.deployments.list(
        RG_NAME, ACCOUNT_NAME)

    deployment_models = [deployment.name for deployment in deployments]

    embedding_model = "text-embedding-ada-002"
    completion_model = "gpt-35-turbo-16k"

    for deployment_model in deployment_models:
        embedding_model = deployment_model if "embedding" in deployment_model.lower(
        ) else embedding_model
        completion_model = deployment_model if "completion" in deployment_model.lower(
        ) else completion_model

    return (embedding_model, completion_model)


def get_access_token() -> str:
    credential = DefaultAzureCredential()
    token = credential.get_token("https://graph.microsoft.com/.default")
    return token.token

def get_sharepoint_headers() -> dict:
    access_token = get_access_token()
    return {"Authorization": f"Bearer {access_token}"}

def get_sharepoint_site_id(graph_api_endpoint: str):
    headers = get_sharepoint_headers()
    response = requests.get(graph_api_endpoint, headers=headers)
    return response.json().get('id')


def get_sharepoint_drive_id(site_id: str) -> str:
    headers = get_sharepoint_headers()
    drives_api_endpoint = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives"
    response = requests.get(drives_api_endpoint, headers=headers)
    drives = response.json().get('value')
    for drive in drives:
        if drive.get('name') == "Documents":
            drive_id = drive.get('id')
            return drive_id
    return ""

def upload_document_to_sharepoint(file_content: bytes, client_name: str, document_name: str, date: str):
    try:
        headers = get_sharepoint_headers()
        graph_api_endpoint = "https://graph.microsoft.com/v1.0/sites/forumequitypartners.sharepoint.com:/sites/REIIFDDQAssistant"
        site_id = get_sharepoint_site_id(graph_api_endpoint)
        drive_id = get_sharepoint_drive_id(site_id)
        file_path = f"Test/{client_name}_{document_name}_{date}.docx"
        upload_api_endpoint = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives/{drive_id}/root:/{file_path}:/content"
        response = requests.put(upload_api_endpoint, headers=headers, data=file_content)
    except Exception as e:
        print(f"Uploading error: {e}")
    return response.status_code in (200, 201)