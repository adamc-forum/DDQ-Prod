from database import DatabaseClient

from functions import (
    get_db_client
)

# Responsible for cleaning the database, either removing all or some documents

db_client = get_db_client()

# db_client.remove_data_from_collection(delete_all=True)

# db_client.remove_data_from_collection(fieldname='id', substring='Echelon_Responses_29-08-2023')