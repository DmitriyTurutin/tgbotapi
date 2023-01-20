from fastapi import APIRouter, File, HTTPException
from pydantic import BaseModel
from fastapi.responses import FileResponse
from datetime import datetime, timedelta
import pickle
import os
from dotenv import load_dotenv

from UseCases.WebScrapping.WebScrapperService import WebScrapperService

router = APIRouter()

load_dotenv()


class UpdateRequest(BaseModel):
    url: str
    email: str
    password: str


class SalesRequest(BaseModel):
    from_date: datetime
    to_date: datetime


@router.get("/update")
async def update(request: UpdateRequest):
    scrapper = WebScrapperService()
    scrapper.login(address=request.url,
                   email=request.email, password=request.password)
    return {"response": "success"}


@router.get("/scan")
async def scan(request: UpdateRequest):
    scrapper = WebScrapperService()
    scrapper.scan(url=request.url,
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


@router.get("/predict")
async def predict(unique_visitors: int):
    loaded_model = pickle.load(open('./Storage/linear_regression_model.pkl', 'rb'))

    today = datetime.now()
    one_day = timedelta(1)

    tomorrow = today + one_day

    month = tomorrow.month
    week_day = tomorrow.weekday()
    next_day_features = [[week_day, month, unique_visitors]]
    result = loaded_model.predict(next_day_features)

    result = result[0]

    return {"prediction": result}

# @router.get("/predict")
# async def predict(unique_visitors: int,week_day: int, month: int):
#     with open('./Storage/model.pkl', 'rb') as f:
#         model = pickle.load(f)

#     type(model)
#     prediction = model.predict([week_day, month, unique_visitors])
#     return {"prediction": prediction}
