import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "dicery_backend:app", host="0.0.0.0", port=8000, log_level="trace", reload=True,
    )
