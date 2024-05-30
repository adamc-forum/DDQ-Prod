from azure.identity import DefaultAzureCredential, CertificateCredential
from azure.keyvault.secrets import SecretClient
from azure.mgmt.cognitiveservices import CognitiveServicesManagementClient
from openai import AzureOpenAI
from msal import ConfidentialClientApplication, PublicClientApplication
import requests
from requests.models import Response
from urllib.parse import quote
from datetime import datetime

import base64

from constants import (
    SUBSCRIPTION_ID,
    OPENAI_API_VERSION,
    OPENAI_API_KEY,
    OPENAI_API_ENDPOINT,
    RG_NAME,
    ACCOUNT_NAME,
    CONNECTION_STRING,
    DATABASE_NAME,
    COLLECTION_NAME,
    APP_CLIENT_ID,
    APP_TENANT_ID,
    KEY_VAULT_URL,
    GRAPH_API_ENDPOINT,
    SHAREPOINT_BASE_URL
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

def format_date(date_obj: datetime) -> str:
    try:
        day = date_obj.day
        month = date_obj.month
        year = date_obj.year
        return f"{day:02d}-{month:02d}-{year}"
    except Exception as e:
        raise ValueError(f"Error formatting date: {e}")
    
def get_document_url(
    client_name: str,
    document_name: str,
    date: datetime,
    page_number: int = 0
):
    try:
        encoded_client_name = quote(client_name)
        encoded_document_name = quote(document_name)
        formatted_date = format_date(date)
        document_url = f"{SHAREPOINT_BASE_URL}/{encoded_client_name}_{encoded_document_name}_{formatted_date}.pdf#page={page_number}"
        return document_url
    except Exception as e:
        raise Exception(f"Error fetching document url: {e}")

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
        completion_model = deployment_model if "gpt4o" in deployment_model.lower(
        ) else completion_model
    return (embedding_model, completion_model)

def get_access_token() -> str:
    default_credential = DefaultAzureCredential()
    vault_url = KEY_VAULT_URL
    secret_client = SecretClient(vault_url=vault_url, credential=default_credential)

    secret_name = [secret.name for secret in secret_client.list_properties_of_secrets()][0]
    secret = secret_client.get_secret(secret_name)  

    # The value of the secret is the base64-encoded bytes of the .pfx certificate
    certificate_bytes = base64.b64decode(secret.value)

    tenant_id = APP_TENANT_ID
    client_id = APP_CLIENT_ID

    credential = CertificateCredential(
        tenant_id=tenant_id,
        client_id=client_id,
        certificate_data=certificate_bytes,
    )

    token = credential.get_token("https://graph.microsoft.com/.default")

    return token.token  

def get_sharepoint_headers(access_token: str) -> dict:
    access_token = get_access_token()
    return {"Authorization": f"Bearer {access_token}"}


def get_sharepoint_site_id(graph_api_endpoint: str, access_token: str):
    headers = get_sharepoint_headers(access_token)
    response = requests.get(graph_api_endpoint, headers=headers)
    return response.json().get('id')


def get_sharepoint_drive_id(site_id: str, access_token: str) -> str:
    headers = get_sharepoint_headers(access_token)
    drives_api_endpoint = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives"
    response = requests.get(drives_api_endpoint, headers=headers)
    drives = response.json().get('value')
    for drive in drives:
        if drive.get('name') == "Documents":
            drive_id = drive.get('id')
            return drive_id
    return ""

def create_pdf_and_upload_to_sharepoint(file_content: bytes, client_name: str, document_name: str, date: str) -> bytes:
    try:
        access_token = get_access_token()
        headers = get_sharepoint_headers(access_token)
        site_id = get_sharepoint_site_id(GRAPH_API_ENDPOINT, access_token)
        drive_id = get_sharepoint_drive_id(site_id, access_token)
        if drive_id is None or site_id is None:
            raise Exception("Failed to get SharePoint site or drive ID")
        file_path = f"General/{client_name}_{document_name}_{date}"

        # Upload word document to sharepoint
        upload_result: Response = upload_document_to_sharepoint(file_content, headers, site_id, drive_id, file_path, file_extension="docx")
        document_id = upload_result.json()['id']

        # Convert word to pdf
        pdf_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives/{drive_id}/items/{document_id}/content?format=pdf"
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        response = requests.get(pdf_url, headers=headers)
        pdf_content = response.content if response.status_code == 200 else None
        if pdf_content is None:
            raise Exception(f"Unable to convert docx to pdf: {response.status_code} - {response.content}")

        # Upload pdf document to sharepoint
        upload_document_to_sharepoint(pdf_content, headers, site_id, drive_id, file_path, file_extension="pdf")
        return pdf_content
    except Exception as e:
        raise e

def upload_document_to_sharepoint(file_content: bytes, headers, site_id: str, drive_id: str, file_path: str, file_extension: str) -> Response:
    try:
        upload_api_endpoint = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives/{drive_id}/root:/{file_path}.{file_extension}:/content"
        response = requests.put(upload_api_endpoint, headers=headers, data=file_content, timeout=60)
    except Exception as e:
        raise Exception(f"Unable to upload word document to Sharepoint: {e}")
    if response.status_code not in (200, 201):
        raise Exception(f"Unable to upload word document to Sharepoint: {response.status_code} - {response.content}")

    return response

def delete_documents_from_sharepoint(filename: str):
    try:
        access_token = get_access_token()
        headers = get_sharepoint_headers(access_token)
        site_id = get_sharepoint_site_id(GRAPH_API_ENDPOINT, access_token)
        drive_id = get_sharepoint_drive_id(site_id, access_token)
        for file_extension in ["pdf", "docx"]:    
            file_path = f"General/{filename}.{file_extension}"
            delete_api_endpoint = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives/{drive_id}/root:/{file_path}"
            response = requests.delete(delete_api_endpoint, headers=headers)
    except Exception as e:
        raise e
    return response.status_code in (200, 204)  