from typing import Union
from fastapi import FastAPI, Query
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from completions import generate_completion

app = FastAPI()

# Configure CORS for dev environment
# Not required for prod since both frontend and api have same root domain, same-origin request

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Allows all origins
#     allow_credentials=True,
#     allow_methods=["*"],  # Allows all methods
#     allow_headers=["*"],  # Allows all headers
# )

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
