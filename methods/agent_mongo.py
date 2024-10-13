import pymongo
from pymongo import MongoClient
from llama_index.embeddings.openai import OpenAIEmbedding
import openai
from datetime import datetime
import numpy as np

class MongoDBHandler:
    def __init__(self, mongo_uri, openai_api_key, db_name="FiguresCortexDB"):
        """Initialize MongoDB connection and OpenAI embedding generator."""
        self.client = self.get_mongo_client(mongo_uri)
        self.db = self.client[db_name]
        self.embedding_generator = OpenAIEmbedding(model="text-embedding-ada-002", api_key=openai_api_key)
        
        # Collections
        self.collections = {
            "user_experience": self.db["user_experience"],
            "mentor_insights": self.db["mentor_insights"],
            "coach_knowledge": self.db["coach_knowledge"],
            "user_identity": self.db["user_identity"],
            "user_profile": self.db["user_profile"],
            "user_experience_rag": self.db["user_experience_rag"],
        }

    def get_mongo_client(self, mongo_uri):
        """Establish connection to the MongoDB."""
        try:
            client = pymongo.MongoClient(mongo_uri)
            print("Connection to MongoDB successful")
            return client
        except pymongo.errors.ConnectionFailure as e:
            print(f"Connection failed: {e}")
            return None

    def generate_embeddings(self, input_text):
        """Generate embeddings using OpenAI."""
        return self.embedding_generator.get_text_embedding(input_text)

    def save_text(self, user, linkedin_url, profile_pictrue, profile_summary, topic, key_words, main_topic, event_url, collection_type):
        """Store text in MongoDB with its type and user info."""
        embedding_profile = self.generate_embeddings(profile_summary)
        document = {
            "user": user,
            "linkedin_url": linkedin_url,
            "profile_pictrue": profile_pictrue,
            "profile_summary": embedding_profile,
            "profile": profile_summary,
            "topic": topic,
            "key_words": key_words,
            "main_topic": main_topic,
            "event_url": event_url,
            "date": datetime.utcnow()
        }
        self.collections[collection_type].insert_one(document)
        return document
    
    def save_text_experience(self, user, content, collection_type):
        """Store text in MongoDB with its type and user info."""
        embedding_profile = self.generate_embeddings(content)
        document = {
            "user": user,
            "content": content,
            "embedding": embedding_profile,
            "date": datetime.utcnow()
        }
        self.collections[collection_type].insert_one(document)
        return document

    def retrieve_relevant_data(self, query, user, collection_type, top_k=3, similarity_threshold=0.4):
        """Retrieve the most relevant documents for a specific user from MongoDB using vector search."""
        query_embedding = self.generate_embeddings(query)

        if user=="":
            results = self.collections[collection_type].aggregate([
                    {
                        "$vectorSearch": {
                            "index": "vector_index",
                            "path": "profile_summary",
                            "queryVector": query_embedding,
                            "numCandidates": top_k,
                            "limit": top_k,
                            "similarityThreshold": similarity_threshold
                        }
                    },
                    {
                        "$project": {
                            "content": 1,
                            "date": 1,
                            "user": 1,
                            "linkedin_url": 1,
                            "profile": 1,
                            "profile_pictrue": 1,
                            "topic": 1,
                            "key_words": 1,
                            "main_topic": 1,
                            "event_url": 1,
                            "_id": 0
                        }
                    }
                ])
        else:
            results = self.collections[collection_type].aggregate([
                {
                    "$vectorSearch": {
                        "index": "vector_index",
                        "path": "embedding",
                        "queryVector": query_embedding,
                        "numCandidates": top_k,
                        "limit": top_k,
                        "similarityThreshold": similarity_threshold
                    }
                },
                {
                    "$project": {
                        "content": 1,
                        "date": 1,
                        "user": 1,
                        "_id": 0
                    }
                }
            ])
        
        results_list = list(results)
        if not results_list:
            return " "
        
        return results_list
