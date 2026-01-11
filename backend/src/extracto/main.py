import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from extracto.api.document_api import document_api
from extracto.api.project_api import project_api
from extracto.api.task_api import task_api
from extracto.api.user_api import user_api
from extracto.api.auth_api import auth_api

from extracto.logger.log_utils import Logger

logger = Logger()

base_url = "/extracto"

app = FastAPI(
    openapi_url="/swagger/openapi.json",
    docs_url=base_url + "/swagger",
    title="Document Processing Application",
    description="LLM powered document intelligence platform",
    version="0.0.1"
)

allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Content-Type", "Authorization"],
    max_age=3600
)


@app.on_event("startup")
def start():
    """
    Application startup event.
    """
    try:
        logger.info(f'Starting application...')
        logger.info(f'Application Stated')
    except Exception as e:
        logger.error(f'Exception in startup of application: {e}')


@app.on_event("shutdown")
def shutdown():
    """
    Application shutdown event.
    """
    logger.info(f'on application shutdown')
    return 0


app.include_router(auth_api, prefix="/api/v1/auth")
app.include_router(user_api, prefix="/api/v1/user")
app.include_router(document_api, prefix="/api/v1/document")
app.include_router(project_api, prefix="/api/v1/project")
app.include_router(task_api, prefix="/api/v1/task")


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")