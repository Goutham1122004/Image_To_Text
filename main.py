# main.py

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse
import requests
import os
from motor.motor_asyncio import AsyncIOMotorClient

app = FastAPI()

API_URL = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-large"
HEADERS = {"Authorization": "Bearer api_key"}

# MongoDB Connection
MONGO_CONNECTION_URL = "mongodb://localhost:27017"
client = AsyncIOMotorClient(MONGO_CONNECTION_URL)
db = client["image_caption_db"]
collection = db["captions"]

async def save_caption_to_db(file_name, caption):
    await collection.insert_one({"file_name": file_name, "caption": caption})

@app.post("/generate-caption/")
async def generate_caption(file: UploadFile = File(...)):
    try:
        data = await file.read()
        response = requests.post(API_URL, headers=HEADERS, data=data)
        result = response.json()
        if result:
            caption = result[0]["generated_text"]
            # Save caption to MongoDB
            await save_caption_to_db(file.filename, caption)
            return {"caption": caption}
        else:
            raise HTTPException(status_code=500, detail="Failed to generate caption")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/", response_class=HTMLResponse)
async def homepage():
    with open(os.path.join("template", "index.html"), "r") as f:
        content = f.read()
    return HTMLResponse(content)
