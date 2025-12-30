"""
Create Sample Data for Testing
This script populates MongoDB with sample data for testing the MCP search solution
"""

from pymongo import MongoClient
from config import Config
import sys

def create_sample_data():
    """Create sample collections with test data"""
    print("=" * 60)
    print("Creating Sample Data")
    print("=" * 60)
    print()
    
    try:
        # Validate configuration
        Config.validate()
        
        # Connect to MongoDB
        print(f"Connecting to MongoDB: {Config.MONGODB_CONNECTION_STRING}")
        client = MongoClient(Config.MONGODB_CONNECTION_STRING, serverSelectionTimeoutMS=5000)
        
        # Test connection
        client.admin.command('ping')
        print("✓ Connected to MongoDB")
        print()
        
        # Get database
        db = client[Config.MONGODB_DATABASE]
        print(f"Using database: {Config.MONGODB_DATABASE}")
        print()
        
        # Create users collection
        print("Creating 'users' collection...")
        users = db['users']
        
        # Clear existing data (optional)
        users.delete_many({})
        
        # Insert sample users
        users_data = [
            {'name': 'Alice', 'age': 28, 'status': 'active', 'email': 'alice@example.com', 'city': 'New York'},
            {'name': 'Bob', 'age': 32, 'status': 'active', 'email': 'bob@example.com', 'city': 'San Francisco'},
            {'name': 'Charlie', 'age': 24, 'status': 'inactive', 'email': 'charlie@example.com', 'city': 'Chicago'},
            {'name': 'Diana', 'age': 35, 'status': 'active', 'email': 'diana@example.com', 'city': 'Boston'},
            {'name': 'Eve', 'age': 29, 'status': 'active', 'email': 'eve@example.com', 'city': 'Seattle'},
            {'name': 'Frank', 'age': 45, 'status': 'inactive', 'email': 'frank@example.com', 'city': 'Los Angeles'},
        ]
        result = users.insert_many(users_data)
        print(f"✓ Inserted {len(result.inserted_ids)} users")
        print()
        
        # Create products collection
        print("Creating 'products' collection...")
        products = db['products']
        
        # Clear existing data (optional)
        products.delete_many({})
        
        # Insert sample products
        products_data = [
            {'name': 'Laptop', 'price': 999.99, 'category': 'electronics', 'stock': 10, 'brand': 'TechCorp'},
            {'name': 'Phone', 'price': 699.99, 'category': 'electronics', 'stock': 25, 'brand': 'TechCorp'},
            {'name': 'Tablet', 'price': 399.99, 'category': 'electronics', 'stock': 15, 'brand': 'TechCorp'},
            {'name': 'Headphones', 'price': 149.99, 'category': 'accessories', 'stock': 50, 'brand': 'AudioPro'},
            {'name': 'Keyboard', 'price': 79.99, 'category': 'accessories', 'stock': 30, 'brand': 'KeyMaster'},
            {'name': 'Mouse', 'price': 49.99, 'category': 'accessories', 'stock': 40, 'brand': 'KeyMaster'},
            {'name': 'Monitor', 'price': 299.99, 'category': 'electronics', 'stock': 20, 'brand': 'DisplayTech'},
        ]
        result = products.insert_many(products_data)
        print(f"✓ Inserted {len(result.inserted_ids)} products")
        print()
        
        # Create orders collection
        print("Creating 'orders' collection...")
        orders = db['orders']
        
        # Clear existing data (optional)
        orders.delete_many({})
        
        # Insert sample orders
        orders_data = [
            {'order_id': 'ORD001', 'user': 'Alice', 'product': 'Laptop', 'quantity': 1, 'total': 999.99, 'status': 'completed'},
            {'order_id': 'ORD002', 'user': 'Bob', 'product': 'Phone', 'quantity': 2, 'total': 1399.98, 'status': 'pending'},
            {'order_id': 'ORD003', 'user': 'Diana', 'product': 'Tablet', 'quantity': 1, 'total': 399.99, 'status': 'completed'},
            {'order_id': 'ORD004', 'user': 'Eve', 'product': 'Headphones', 'quantity': 3, 'total': 449.97, 'status': 'shipped'},
            {'order_id': 'ORD005', 'user': 'Alice', 'product': 'Keyboard', 'quantity': 1, 'total': 79.99, 'status': 'completed'},
        ]
        result = orders.insert_many(orders_data)
        print(f"✓ Inserted {len(result.inserted_ids)} orders")
        print()
        
        # Summary
        print("=" * 60)
        print("Sample Data Created Successfully!")
        print("=" * 60)
        print()
        print("Collections created:")
        print(f"  - users: {users.count_documents({})} documents")
        print(f"  - products: {products.count_documents({})} documents")
        print(f"  - orders: {orders.count_documents({})} documents")
        print()
        print("You can now test queries like:")
        print("  - find all users where age is greater than 25")
        print("  - get products from products collection where price is less than 500")
        print("  - show first 5 documents from orders collection")
        print()
        
        client.close()
        return True
        
    except Exception as e:
        print(f"✗ Error creating sample data: {e}")
        print()
        print("Troubleshooting:")
        print("  1. Make sure MongoDB is running")
        print("  2. Check connection string in .env file")
        print("  3. Run: python test_connection.py")
        return False


if __name__ == '__main__':
    success = create_sample_data()
    sys.exit(0 if success else 1)

