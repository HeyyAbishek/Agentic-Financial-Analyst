from fastapi import FastAPI
import uvicorn
import os
from dotenv import load_dotenv
from api.routes import router as api_router

# Load environment variables
load_dotenv()

app = FastAPI(title="AI Worker Service")

# Include routers
app.include_router(api_router)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
