from fastapi import FastAPI, HTTPException
from fastapi import status


def ResponseModel(data, message):
    return {
        "status": True,
        "data": data,
        "code": status.HTTP_200_OK,
        "message": message,
    }


def ErrorResponseModel(error="Server error", code=status.HTTP_500_INTERNAL_SERVER_ERROR):
    raise HTTPException(status_code=code, detail=error)


def FalseResponseModel(data, message):
    return {
        "status": False,
        "data": data,
        "code": status.HTTP_200_OK,
        "message": message,
    }
