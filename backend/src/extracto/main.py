import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from extracto.api.document_api import document_api
from extracto.api.project_api import project_api
from extracto.api.task_api import task_api


base_url = "/extracto"

app = FastAPI(
    openapi_url="/swagger/openapi.json",
    docs_url= base_url + "/swagger",
    title="Document Processing Application",
    description="",
    version="0.0.1"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def start():
    print(f'Starting application...')
    try:
        print(f'Application Stated')
    except Exception as e:
        print(f'Exception in startup of application: {e}')


@app.on_event("shutdown")
def shutdown():
    print(f'on application shutdown')
    return 0


app.include_router(document_api, prefix="/api/v1/document")
app.include_router(project_api, prefix="/api/v1/project")
app.include_router(task_api, prefix="/api/v1/task")


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")