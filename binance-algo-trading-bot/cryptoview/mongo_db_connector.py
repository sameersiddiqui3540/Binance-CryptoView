from pymongo import MongoClient

def connect_to_mongodb(uri, db_name, collection_name):
    """
    Connect to a MongoDB instance and return the specified database and collection.

    Parameters:
        uri (str): MongoDB connection URI.
        db_name (str): Name of the database to connect to.
        collection_name (str): Name of the collection to connect to.

    Returns:
        collection (pymongo.collection.Collection): The specified MongoDB collection, or None if an error occurs.
    """
    try:
        # Create a MongoClient instance
        client = MongoClient(uri)

        # Access the database
        db = client[db_name]

        # Access the collection
        collection = db[collection_name]

        print(f"Connected to MongoDB collection: {db_name}.{collection_name}")
        return collection

    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return None

def get_api_credentials(uri, db_name, collection_name):
    """
    Connect to MongoDB and retrieve API_KEY and API_SECRET from the specified collection.

    Parameters:
        uri (str): MongoDB connection URI.
        db_name (str): Database name.
        collection_name (str): Collection name.

    Returns:
        List[dict]: A list of dictionaries containing API_KEY and API_SECRET.
    """
    try:
        # Connect to MongoDB
        client = MongoClient(uri)

        # Access the database and collection
        db = client[db_name]
        collection = db[collection_name]

        # Retrieve documents with API_KEY and API_SECRET
        documents = collection.find({}, {"API_KEY": 1, "API_SECRET": 1, "_id": 0})
        credentials = list(documents)

        return credentials

    except Exception as e:
        print(f"Error: {e}")
        return None



if __name__ == "__main__":
    # MongoDB connection details

    mongo_uri = "mongodb://localhost:27017"
    database_name = "db_name"
    collection_name = "collection_name"

    # Connect to MongoDB
    collection = connect_to_mongodb(mongo_uri, database_name, collection_name)

    # Check if the connection is successful
    if collection is not None:
        # Convert documents to a list of dictionaries
        documents = list(collection.find())

        # Check the number of documents
        print(f"documents: {documents}, Number of documents in the collection: {len(documents)}, type: {type(documents)}")

        # Iterate through the list of dictionaries
        for idx, doc in enumerate(documents, start=1):
            print(f"Document {idx}: {doc}")
            if 'API_KEY' in doc and 'API_SECRET' in doc:
                print(f"API_KEY: {doc['API_KEY']}, API_SECRET: {doc['API_SECRET']}")
            else:
                print(f"Document {idx} does not have 'API_KEY' or 'API_SECRET' keys.")
    else:
        print("Failed to connect to the specified MongoDB collection.")
