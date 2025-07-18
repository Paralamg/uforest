from fastapi import APIRouter

home_route = APIRouter()


@home_route.get("/", tags=["home"])
async def index() -> str:
    return "Hello World"
