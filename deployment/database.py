import pymongo
from pymongo.errors import DuplicateKeyError


class DatabaseClient:

    def __init__(self, connection_string, database_name, collection_name):
        self.client = pymongo.MongoClient(connection_string)
        self.collection_name = collection_name
        self.db = self.client[database_name]
        self.collection = self.db[collection_name]

    def setup_collection(self, collection_name=""):
        collection_name = collection_name if collection_name else self.collection_name

        if collection_name not in self.db.list_collection_names():
            self.db.create_collection(collection_name)
            print(f"Created collection '{collection_name}'.")
        else:
            print(f"Using existing collection: '{collection_name}'.")

        return self.db[collection_name]

    def create_indices(self,
                       collection=None,
                       vector_index_name="VectorSearchIndex"):
        collection = collection if collection else self.collection
        vector_index_exists = False
        for index in collection.list_indexes():
            if index['name'] == vector_index_name:
                vector_index_exists = True

        document_count = collection.count_documents({})

        # Set numLists based on document count as recommended by Microsoft's best practices
        num_lists = max(1, int(document_count /
                               1000)) if document_count <= 1000000 else int(
                                   document_count**0.5)

        if not vector_index_exists:
            self.db.command({
                'createIndexes':
                collection.name,
                'indexes': [{
                    'name': vector_index_name,
                    'key': {
                        "contentVector": "cosmosSearch"
                    },
                    'cosmosSearchOptions': {
                        'kind': 'vector-ivf',
                        'numLists': num_lists,
                        'similarity': 'COS',
                        'dimensions': 1536,
                    }
                }]
            })
            print(f"Created vector index {vector_index_name}")
        else:
            print(f"Using existing vector index {vector_index_name}")

        # Unique ID index to avoid adding duplicate data
        unique_index = [("id", pymongo.ASCENDING)]
        collection.create_index(unique_index, unique=True)

    def add_data_to_collection(self, data):
        for document in data:
            try:
                self.collection.insert_one(document)
            except DuplicateKeyError:
                print(
                    f"ERROR: Attempting to add duplicate id {document['id']}")
                continue

    def remove_data_from_collection(self,
                                    fieldname: str = None,
                                    substring: str = None,
                                    delete_all: bool = False):
        if delete_all:
            self.collection.delete_many({})
        else:
            if fieldname is None or substring is None:
                raise ValueError(
                    "fieldname and substring must be provided unless delete_all is True"
                )
            self.collection.delete_many({fieldname: {"$regex": substring}})

    def find_documents_by_substring(self, fieldname: str, substring: str):
        regex = {"$regex": substring}
        documents = self.collection.find({fieldname: regex})
        return list(documents)
