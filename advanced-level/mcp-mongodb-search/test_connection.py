"""
Test MongoDB Connection for Local Setup
This script helps verify that MongoDB is accessible locally
"""

import sys
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from config import Config

def test_mongodb_connection():
    """Test connection to MongoDB"""
    print("=" * 60)
    print("Testing MongoDB Connection")
    print("=" * 60)
    print()
    
    connection_string = Config.MONGODB_CONNECTION_STRING
    database_name = Config.MONGODB_DATABASE
    
    print(f"Connection String: {connection_string}")
    print(f"Database Name: {database_name}")
    print()
    
    try:
        # Attempt to connect
        print("Attempting to connect to MongoDB...")
        client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
        
        # Test connection by pinging
        client.admin.command('ping')
        print("✓ Successfully connected to MongoDB!")
        print()
        
        # List databases
        print("Available databases:")
        databases = client.list_database_names()
        for db in databases:
            print(f"  - {db}")
        print()
        
        # Check target database
        db = client[database_name]
        print(f"Target database: {database_name}")
        
        # List collections in target database
        collections = db.list_collection_names()
        if collections:
            print(f"Collections in '{database_name}':")
            for collection in collections:
                count = db[collection].count_documents({})
                print(f"  - {collection} ({count} documents)")
        else:
            print(f"  (No collections found - database is empty)")
        print()
        
        # Test insert/read/delete
        print("Testing basic operations...")
        test_collection = db['_test_connection']
        
        # Insert test document
        test_doc = {'test': True, 'message': 'Connection test'}
        result = test_collection.insert_one(test_doc)
        print(f"✓ Insert test: Document ID {result.inserted_id}")
        
        # Read test document
        found = test_collection.find_one({'_id': result.inserted_id})
        if found:
            print(f"✓ Read test: Found document")
        
        # Delete test document
        test_collection.delete_one({'_id': result.inserted_id})
        print(f"✓ Delete test: Removed test document")
        
        # Clean up test collection
        test_collection.drop()
        print()
        
        print("=" * 60)
        print("✓ All tests passed! MongoDB is ready to use.")
        print("=" * 60)
        
        client.close()
        return True
        
    except ConnectionFailure as e:
        print("✗ Connection failed!")
        print(f"  Error: {e}")
        print()
        print("Troubleshooting:")
        print("  1. Make sure MongoDB is running:")
        print("     - macOS: brew services start mongodb-community")
        print("     - Linux: sudo systemctl start mongod")
        print("     - Windows: net start MongoDB")
        print("  2. Check if MongoDB is on the default port (27017)")
        print("  3. Verify connection string in .env file")
        return False
        
    except ServerSelectionTimeoutError as e:
        print("✗ Server selection timeout!")
        print(f"  Error: {e}")
        print()
        print("MongoDB server is not responding. Please check:")
        print("  1. Is MongoDB running?")
        print("  2. Is the connection string correct?")
        print("  3. Are there any firewall issues?")
        return False
        
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False


if __name__ == '__main__':
    try:
        Config.validate()
    except ValueError as e:
        print(f"Configuration error: {e}")
        print("Please check your .env file or environment variables")
        sys.exit(1)
    
    success = test_mongodb_connection()
    sys.exit(0 if success else 1)

