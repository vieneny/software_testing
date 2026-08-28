import uvicorn

if __name__ == "__main__":
    uvicorn.run("ai_middleware.app:app", host="0.0.0.0", port=8000)
