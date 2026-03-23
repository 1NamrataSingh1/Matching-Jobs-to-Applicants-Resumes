# from typing import Optional
from typing import Union
import json

from fastapi import FastAPI, Form, File, UploadFile
# from fastapi.staticfiles import StaticFiles

from pydantic import BaseModel
from skills_query import QueryMysql
from cv_analyzer import cv_get_results, get_st_job_titles, suggest


class Item(BaseModel):
    txt: str


class Suggest(BaseModel):
    resume: str
    jobs: str


class Evaluate(BaseModel):
    resume: str
    jobs: list


q = QueryMysql()
app = FastAPI()


# @app.post("/get-skills/")
# async def request(txt: str = Form(...)):
#     # print(txt)
#     a = q.new_query(txt)
#     # print(a)
#     return a  # {"txt": txt}


@app.post("/send-cv/")
async def create_item(item: Evaluate):
    string_encode = str(item.resume).encode("ascii", "ignore")
    resume = string_encode.decode()
    resume = resume.replace("\"", "")
    jobs = item.jobs
    a = cv_get_results(resume, jobs=jobs)
    return a  # json.dumps(a)


@app.post("/suggest/")
async def create_item(item: Suggest):
    string_encode = str(item.resume).encode("ascii", "ignore")
    resume = string_encode.decode()
    resume = resume.replace("\"", "")
    jobs = item.jobs
    result = suggest(resume, jobs)
    return result


@app.post("/get-all-skills/")
async def request(txt: str = Form(...)):
    a = q.get_all_skills(txt)
    return a


# @app.post("/files/")
# async def create_file(file: Union[bytes, None] = File(default=None)):
#     if not file:
#         return {"message": "No file sent"}
#     else:
#         return {"file_size": len(file)}


# @app.post("/uploadfile/")
# async def create_upload_file(file: Union[UploadFile, None] = None):
#     if not file:
#         return {"message": "No upload file sent"}
#     else:
#         return {"filename": file.filename}


# serve static pages
# app.mount("/", StaticFiles(directory="./static/"), name="static")
