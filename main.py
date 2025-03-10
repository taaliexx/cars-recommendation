from fastapi import FastAPI
import logging 
from auth.routes import router as auth_router
from requests.routes import router as requests_router 

logging.basicConfig(level=logging.INFO, 
                    format="%(asctime)s [%(levelname)s] %(message)s")

app = FastAPI(title='Cars Recommendations')

app.include_router(auth_router)
app.include_router(requests_router)