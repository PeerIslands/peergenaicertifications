"""
Quick script to check records in MongoDB
Use this to verify if records were inserted successfully
"""

from pymongo import MongoClient
from config import Config

def check_records(collection_name: str = 'user'):
    """Check records in a collection"""
    try:
        # Connect to MongoDB
        client = MongoClient(Config.MONGODB_CONNECTION_STRING, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        
        # Get database and collection
        db = client[Config.MONGODB_DATABASE]
        collection = db[collection_name]
        
        # Count documents
        count = collection.count_documents({})
        print(f"=" * 60)
        print(f"Collection: {collection_name}")
        print(f"Database: {Config.MONGODB_DATABASE}")
        print(f"Total documents: {count}")
        print(f"=" * 60)
        print()
        
        if count > 0:
            print("Documents:")
            print("-" * 60)
            for doc in collection.find().limit(10):
                print(f"  {doc}")
            print()
        else:
            print("No documents found in this collection.")
            print()
        
        # List all collections in database
        print("All collections in database:")
        print("-" * 60)
        collections = db.list_collection_names()
        for coll in collections:
            coll_count = db[coll].count_documents({})
            print(f"  - {coll}: {coll_count} documents")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False


if __name__ == '__main__':
    import sys
    
    # Get collection name from command line or use default
    collection = sys.argv[1] if len(sys.argv) > 1 else 'user'
    
    print("Checking MongoDB records...")
    print()
    check_records(collection)

