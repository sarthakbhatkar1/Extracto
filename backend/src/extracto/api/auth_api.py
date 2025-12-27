from fastapi import APIRouter, Request, Response, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from extracto.schema import schemas
from extracto.services.auth_service import AuthService

auth_api = APIRouter(tags=["Auth APIs"])
auth_service = AuthService()


@auth_api.post("/register")
async def register(payload: schemas.UserCreate, response: Response):
    return await auth_service.register(payload, response)


@auth_api.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    response = AuthService().authenticate_user(form_data.username, form_data.password)
    if not response:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return response


@auth_api.post("/refresh")
async def refresh(request: Request, response: Response):
    return await auth_service.refresh(request, response)


@auth_api.post("/logout")
async def logout(request: Request, response: Response):
    return await auth_service.logout(request, response)
