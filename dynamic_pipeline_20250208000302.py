import os
import time
import json
import subprocess
import shutil
from pymongo import MongoClient

# Directories for incoming, output, and processed files.
INPUT_DIR = "input"
OUTPUT_DIR = "output"
PROCESSED_DIR = "processed"

def process_file(file_path):
    base_filename = os.path.basename(file_path)
    output_file = os.path.join(OUTPUT_DIR, base_filename)
    
    print(f"Processing file: {file_path}")
    # Call the Scala transformation program.
    # This assumes that DataTransformer.scala has been compiled to DataTransformer.jar.
    try:
        subprocess.run(
            ["scala", "-cp", "DataTransformer.jar", "DataTransformer", file_path, output_file],
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Error during Scala transformation: {e}")
        return False

    # Load the transformed JSON data and insert into MongoDB.
    try:
        with open(output_file, "r") as f:
            data = json.load(f)
        # Connect to MongoDB using the service hostname 'mongodb' (set in docker-compose)
        client = MongoClient("mongodb://mongodb:27017/")
        db = client["ecommerce"]
        collection = db["orders"]
        result = collection.insert_many(data)
        print("Inserted document IDs:", result.inserted_ids)
    except Exception as e:
        print(f"Error inserting into MongoDB: {e}")
        return False

    return True

def dynamic_pipeline():
    # Ensure required directories exist.
    os.makedirs(INPUT_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    
    print(f"Starting dynamic pipeline. Watching for files in '{INPUT_DIR}' directory...")
    
    while True:
        # List JSON files in the input directory.
        files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".json")]
        for filename in files:
            file_path = os.path.join(INPUT_DIR, filename)
            print(f"Found new file: {file_path}")
            if process_file(file_path):
                # Move the processed file to the processed folder.
                shutil.move(file_path, os.path.join(PROCESSED_DIR, filename))
                print(f"Moved {filename} to '{PROCESSED_DIR}' directory.")
        # Poll every 5 seconds.
        time.sleep(5)

if __name__ == "__main__":
    dynamic_pipeline()
