from fastapi import APIRouter, File, HTTPException
from pydantic import BaseModel
from fastapi.responses import FileResponse
from datetime import datetime
import os
from dotenv import load_dotenv
from UseCases.WebScrapping.WebScrapperService import WebScrapperService

router = APIRouter()
load_dotenv()


class UpdateRequest(BaseModel):
    email: str
    password: str


class SalesRequest(BaseModel):
    from_date: datetime
    to_date: datetime


@router.get("/update")
async def update(request: UpdateRequest):
    scrapper = WebScrapperService()
    scrapper.login(address=os.environ['URL'],
                   email=request.email, password=request.password)
    return {"response": "success"}


@router.get("/sales")
async def get_sales(time_period: SalesRequest):
    scrapper = WebScrapperService()
    sales = scrapper.get_from_to(time_period.from_date, time_period.to_date)
    return sales


@router.get("/sales/today")
async def get_sales_today():
    scrapper = WebScrapperService()
    sales = scrapper.get_today()
    return sales


@router.get("/sales/last_month")
async def get_last_month():
    scrapper = WebScrapperService()
    sales = scrapper.get_last_month()
    return sales


@router.get("/download/{file_name}")
async def download_file(file_name: str):
    if os.path.isfile(f"./Storage/{file_name}"):
        return FileResponse(f"./Storage/{file_name}")

    else:
        return HTTPException(status_code=404, detail="File not found")
