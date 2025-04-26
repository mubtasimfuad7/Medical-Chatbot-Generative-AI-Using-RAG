import os
from pinecone import Pinecone
import config

def test_pinecone_connection():
    try:
        print("Testing Pinecone connection...")
        
        # Initialize Pinecone client
        pc = Pinecone(
            api_key=os.environ.get("PINECONE_API_KEY", config.PINECONE_API_KEY),
            environment=os.environ.get("PINECONE_ENV", config.PINECONE_ENV)
        )
        
        print("Successfully connected to Pinecone!")
        
        # List all indexes
        indexes = pc.list_indexes()
        print("\nAvailable indexes:")
        for index in indexes:
            print(f"- {index.name}")
            
        # Check if required indexes exist
        required_indexes = ["test", "medicalbot"]
        missing_indexes = [idx for idx in required_indexes if idx not in [i.name for i in indexes]]
        
        if missing_indexes:
            print("\nMissing required indexes:")
            for idx in missing_indexes:
                print(f"- {idx}")
        else:
            print("\nAll required indexes are present!")
            
    except Exception as e:
        print(f"Error connecting to Pinecone: {str(e)}")

if __name__ == "__main__":
    test_pinecone_connection() 