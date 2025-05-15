from dotenv import load_dotenv
from starlette.staticfiles import StaticFiles

from bin.routers import donation_router,rider_router,information_router
from bin.routers.auth_router import auth_router
from bin.routers.role_router import role_router

load_dotenv(override=True)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(
    title="CCC-Line",
    contact={
        "name": "chamindika Kodithuwakku",
        "email": "chamindika.k@ambrumsolutions.com",
    },
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all HTTP headers
)

app.mount("/public", StaticFiles(directory="public"), name="public")

app.include_router(donation_router.router)
app.include_router(rider_router.router)
app.include_router(information_router.router)
app.include_router(role_router)
app.include_router(auth_router)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8003, workers=1, reload=False)







