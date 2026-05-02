from src.config import (CHROMA_DB_PATH, 
                        CHROMA_TENANT_ID, 
                        CHROMA_CLOUD_HOST, 
                        CHROMA_API_KEY,
                        CHROMA_COLLECTION_NAME)
import chromadb
from chromadb.api import ClientAPI
from chromadb.api.models.Collection import Collection


_client: ClientAPI | None = None
_collection: Collection | None = None

def get_chroma_client() -> ClientAPI:
	global _client
	if _client is None:
		_client = chromadb.CloudClient(
			cloud_port=443,
			cloud_host=CHROMA_CLOUD_HOST,
            api_key=CHROMA_API_KEY,
            tenant=CHROMA_TENANT_ID,
            database=CHROMA_DB_PATH
        )
	return _client

def get_chroma_collection(client: ClientAPI = None) -> Collection:
	global _collection
	if _collection is None:
		if client is None:
			client = get_chroma_client()
		_collection = client.get_or_create_collection(
		    name=CHROMA_COLLECTION_NAME,
		)
	return _collection