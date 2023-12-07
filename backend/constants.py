import os
import dotenv

dotenv.load_dotenv()

# ------------------------- General Constants --------------------

TARGET_PDF_PATH = "../Data/Forum Responses to Echelon (2023.08.29).pdf"

# ------------------------- DB Constants --------------------

CONNECTION_STRING = os.environ.get("COSMOS_CONNECTION_STRING")
DATABASE_NAME = "db-ddq-us-east-1"
COLLECTION_NAME = "collection-ddq-knowledge-base"

# ------------------------- OpenAI Constants --------------------

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_VERSION = "2023-05-15"
OPENAI_ENDPOINT = os.getenv("OPENAI_API_ENDPOINT")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_API_ENDPOINT = os.environ.get("OPENAI_API_ENDPOINT")
SUBSCRIPTION_ID = os.environ.get("SUBSCRIPTION_ID")
RG_NAME = os.environ.get("RG_NAME")
ACCOUNT_NAME = os.environ.get("ACCOUNT_NAME")

# ------------------------- Document Intelligence Constants --------------------

DI_ENDPOINT = os.environ.get("DI_API_ENDPOINT")
DI_API_KEY = os.environ.get("DI_API_KEY")