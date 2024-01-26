from typing import Optional, Union, List
from fastapi import FastAPI, Body, Security, HTTPException
from fastapi.security.api_key import APIKeyHeader, APIKeyQuery, APIKeyCookie
from pydantic import BaseModel, Field
import uuid
from datetime import datetime
import motor.motor_asyncio
import os


MONGODB_URL = os.environ["MONGODB_URL"]
API_KEYS = os.environ["API_KEYS"].split(",")
app = FastAPI(
    title="MongoDB API",
    summary="By Char1esOrz",
)

client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
db = client.pdd


def verify_api_key(
    api_key_header: str = Security(APIKeyHeader(name="X-API-Key", auto_error=False)),
    api_key_query: str = Security(APIKeyQuery(name="api_key", auto_error=False)),
    api_key_cookie: str = Security(APIKeyCookie(name="api_key", auto_error=False)),
):
    if api_key_header in API_KEYS:
        return api_key_header
    elif api_key_query in API_KEYS:
        return api_key_query
    elif api_key_cookie in API_KEYS:
        return api_key_cookie
    else:
        raise HTTPException(status_code=403, detail="Invalid API key")


class ResponseModel(BaseModel):
    status: bool = True
    message: str = ""
    data: Optional[List[dict]] = Field(default=[])


class FindModel(BaseModel):
    filter: dict
    projection: Optional[dict] = Field(default={"_id": 0})
    is_many: bool = False


class UpdateModel(BaseModel):
    filter: dict
    update: dict
    is_many: bool = False


class DeleteModel(BaseModel):
    filter: dict
    is_many: bool = False


@app.post("/{collection_name}/find", response_model=ResponseModel)
async def collection_find(
    collection_name: str,
    body: FindModel = Body(...),
    _: str = Security(verify_api_key),
) -> ResponseModel:
    try:
        collection = db.get_collection(collection_name)
        if body.is_many:
            data = await collection.find(
                body.filter, projection=body.projection
            ).to_list(None)
        else:
            d = await collection.find_one(body.filter, projection=body.projection)
            data = [d] if d else []
        return ResponseModel(
            status=True,
            data=data,
        )
    except Exception as e:
        return ResponseModel(status=False, message=str(e))


@app.post("/{collection_name}/insert", response_model=ResponseModel)
async def collection_insert(
    collection_name,
    body: Union[dict, List[dict]] = Body(...),
    _: str = Security(verify_api_key),
) -> ResponseModel:
    try:
        collection = db.get_collection(collection_name)
        if isinstance(body, dict):
            result = await collection.insert_one(
                {"uuid": str(uuid.uuid4()).replace("-", "")}
                | body
                | {"create_time": datetime.now(), "update_time": datetime.now()}
            )
        else:
            for i, el in enumerate(body):
                body[i] = (
                    {"uuid": str(uuid.uuid4()).replace("-", "")}
                    | el
                    | {"create_time": datetime.now(), "update_time": datetime.now()}
                )
            result = await collection.insert_many(body)
        if result.acknowledged:
            return ResponseModel(status=True)
        return ResponseModel(status=False, message="insert failed")
    except Exception as e:
        return ResponseModel(status=False, message=str(e))


@app.post("/{collection_name}/update", response_model=ResponseModel)
@app.post("/{collection_name}/find_one_and_update", response_model=ResponseModel)
async def collection_update(
    collection_name,
    body: UpdateModel = Body(...),
    _: str = Security(verify_api_key),
) -> ResponseModel:
    try:
        collection = db.get_collection(collection_name)
        if body.is_many:
            result = await collection.update_many(
                body.filter, {"$set": body.update | {"update_time": datetime.now()}}
            )
            return ResponseModel(status=True)
        else:
            result = await collection.find_one_and_update(
                body.filter,
                {"$set": body.update | {"update_time": datetime.now()}},
                projection={"_id": 0},
            )
            if result:
                return ResponseModel(status=True, data=[result])
            return ResponseModel(status=True, message="")
    except Exception as e:
        return ResponseModel(status=False, message=str(e))


@app.post("/{collection_name}/delete", response_model=ResponseModel)
async def collection_delete(
    collection_name,
    body: DeleteModel = Body(...),
    _: str = Security(verify_api_key),
) -> ResponseModel:
    try:
        collection = db.get_collection(collection_name)
        if body.is_many:
            result = await collection.delete_many(body.filter)
        else:
            result = await collection.delete_one(body.filter)
        if result.acknowledged:
            return ResponseModel(status=True)
        return ResponseModel(status=False, message="delete failed")
    except Exception as e:
        return ResponseModel(status=False, message=str(e))
