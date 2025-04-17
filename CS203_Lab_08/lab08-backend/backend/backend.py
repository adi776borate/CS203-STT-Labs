from fastapi import FastAPI, HTTPException
from elasticsearch import Elasticsearch
import uvicorn
from pydantic import BaseModel

app = FastAPI()

# Connect to Elasticsearch
es = Elasticsearch(["http://elasticsearch:9200"])

# Ensure index exists
if not es.indices.exists(index="documents"):
    es.indices.create(index="documents")

# Define data models
class SearchQuery(BaseModel):
    query: str

class DocumentContent(BaseModel):
    content: str

@app.post("/search")
async def search_document(query: SearchQuery):
    try:
        search_query = {
            "query": {
                "match": {
                    "text": {
                        "query": query.query,
                        "fuzziness": "AUTO" 
                    }
                }
            }
        }

        response = es.search(index="documents", body=search_query, size=1)

        if response["hits"]["total"]["value"] > 0:
            document = response["hits"]["hits"][0]
            return {
                "id": document["_id"],
                "score": document["_score"],
                "content": document["_source"]["text"]
            }
        else:
            return {"message": "No documents found matching the query."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/insert")
async def insert_document(document: DocumentContent):
    try:
        response = es.index(index="documents", document={"text": document.content})
        return {"message": f"Document inserted successfully with ID: {response['_id']}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run the FastAPI app
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9567)
