from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import warnings
import uvicorn

from api import chatbot, document, history, products

warnings.filterwarnings("ignore", message="Api key is used with an insecure connection.")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chatbot.router, prefix="/api")
app.include_router(document.router, prefix="/api")
app.include_router(history.router, prefix="/api")
app.include_router(products.router, prefix="/api")


@app.get("/")
async def hello():
    return {"message": "MekongAI API Services || Hello!"}


# ================================================ MAIN API ===================================================
###############################################################################################################
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=1953, timeout_keep_alive=50000)
