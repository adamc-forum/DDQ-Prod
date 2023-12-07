from typing import Union
from fastapi import FastAPI, Query
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import json

from completions import generate_completion

app = FastAPI()

@app.get("/search")
def read_root(query: str = Query(None, title="Query")):
    try:
        llm_response, vector_search_results = generate_completion(query)
        return {
            "response": llm_response,
            "results": vector_search_results
        }
    except Exception as e:
        print(e)
        return {"Message": f"Error fetching response: {e}"}

# Mount the `static` directory to the path `/`
app.mount("/", StaticFiles(directory="public", html=True), name="public")

