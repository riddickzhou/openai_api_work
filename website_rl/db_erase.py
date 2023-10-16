from pymongo import MongoClient

DB_NAME = "mongodb_rl"
MONGO_URI = 'mongodb://localhost:27017/' + DB_NAME  # MongoDB connection URI

# Connect to the MongoDB server
client = MongoClient(MONGO_URI)

# Access the database you want to delete
db = client[DB_NAME]

# Delete the database
client.drop_database(DB_NAME)

print(f"Database '{DB_NAME}' has been deleted.")