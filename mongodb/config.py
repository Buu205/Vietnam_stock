"""MongoDB configuration with ServerApi support."""

import os
from typing import Optional
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

# Load environment variables from root .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

# MongoDB configuration
MONGODB_URI = os.getenv(
    'MONGODB_URI',
    'mongodb+srv://buuphanquoc_db:Quocbuu123@cluster0.m6tqpie.mongodb.net/?appName=Cluster0'
)
MONGODB_DB_NAME = os.getenv('MONGODB_DB_NAME', 'mydb')

# Global client instance
_client: Optional[MongoClient] = None


def get_mongodb_client() -> MongoClient:
    """
    Get or create MongoDB client with ServerApi.
    
    Returns:
        MongoClient: MongoDB client instance
        
    Note:
        Uses ServerApi version '1' for MongoDB Atlas compatibility
    """
    global _client
    
    if _client is None:
        try:
            # Create ServerApi instance
            server_api = ServerApi('1')
            
            # Create client with ServerApi
            # Note: tlsAllowInvalidCertificates=True for development
            # Remove in production or install proper certificates
            _client = MongoClient(
                MONGODB_URI,
                server_api=server_api,
                serverSelectionTimeoutMS=5000,  # 5 seconds timeout
                tlsAllowInvalidCertificates=True
            )
            
            # Test connection
            _client.admin.command('ping')
            logger.info("Successfully connected to MongoDB Atlas")
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    return _client


def get_database(db_name: Optional[str] = None) -> 'Database':
    """
    Get MongoDB database instance.
    
    Args:
        db_name: Database name. If None, uses MONGODB_DB_NAME from env.
        
    Returns:
        Database: MongoDB database instance
    """
    client = get_mongodb_client()
    db_name = db_name or MONGODB_DB_NAME
    return client[db_name]


def close_connection():
    """Close MongoDB connection."""
    global _client
    if _client is not None:
        _client.close()
        _client = None
        logger.info("MongoDB connection closed")

