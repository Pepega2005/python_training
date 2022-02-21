import uvicorn
from fastapi import FastAPI

app = FastAPI()

@app.get('/')
def index():
    return('Any text')

uvicorn.run(app)