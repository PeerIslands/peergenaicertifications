"""
Initialize Database - Creates the database and a test collection
This ensures the database appears in MongoDB Compass
"""

from pymongo import MongoClient
from config import Config
import sys

def init_database():
    """Initialize the database with a test collection"""
    print("=" * 60)
    print("Initializing Database for MongoDB Compass")
    print("=" * 60)
    print()
    
    try:
        # Validate configuration
        Config.validate()
        
        connection_string = Config.MONGODB_CONNECTION_STRING
        database_name = Config.MONGODB_DATABASE
        
        print(f"Connection String: {connection_string}")
        print(f"Database Name: {database_name}")
        print()
        
        # Connect to MongoDB
        print("Connecting to MongoDB...")
        client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
        
        # Test connection
        client.admin.command('ping')
        print("✓ Connected to MongoDB")
        print()
        
        # Get database (this doesn't create it yet - need to write data)
        db = client[database_name]
        print(f"Accessing database: {database_name}")
        print()
        
        # Create a test collection and insert a document
        # This will create the database if it doesn't exist
        print("Creating test collection and inserting sample document...")
        test_collection = db['_init']
        
        # Insert a document to ensure database is created
        test_doc = {
            'message': 'Database initialized',
            'timestamp': '2024-01-01',
            'status': 'ready'
        }
        result = test_collection.insert_one(test_doc)
        print(f"✓ Inserted test document (ID: {result.inserted_id})")
        print()
        
        # Verify database exists
        databases = client.list_database_names()
        if database_name in databases:
            print(f"✓ Database '{database_name}' now exists in MongoDB")
        else:
            print(f"⚠ Database '{database_name}' not found in list")
        print()
        
        # List collections in the database
        collections = db.list_collection_names()
        print(f"Collections in '{database_name}':")
        if collections:
            for collection in collections:
                count = db[collection].count_documents({})
                print(f"  - {collection}: {count} documents")
        else:
            print("  (No collections found)")
        print()
        
        print("=" * 60)
        print("✓ Database initialized successfully!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Refresh MongoDB Compass (click the refresh button)")
        print(f"2. You should now see '{database_name}' database in the left sidebar")
        print("3. Run 'python create_sample_data.py' to add more collections")
        print()
        
        client.close()
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        print()
        print("Troubleshooting:")
        print("  1. Make sure MongoDB is running")
        print("  2. Check connection string in .env file")
        print("  3. Run: python test_connection.py")
        return False


if __name__ == '__main__':
    success = init_database()
    sys.exit(0 if success else 1)

