import fastapi

app = fastapi.FastAPI()

@app.get('/ping')
async def read_main():
    return { "message" : "Hello World of FastAPI HTTPS" }
