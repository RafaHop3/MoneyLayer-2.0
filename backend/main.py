from fastapi import FastAPI
import os

app = FastAPI(title="Money Layer API", version="0.1.0")

@app.get("/")
def read_root():
    return {
        "status": "active",
        "service": "Money Layer",
        "social_mission": "Financial access for all",
        "version": "MVP 1.0"
    }

@app.get("/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
