# app/services/http_request_logger.py
from typing import Optional

import httpx
from sqlalchemy.orm import Session

from bin.models.pg_models import ApiLog


class HttpRequestLogger:

    def __init__(self, base_url: str,  db: Optional[Session] = None):
        self.base_url = base_url
        self.headers = {}
        self.payload = {}
        self.api = ""
        self.db = db

    def set_api(self, api: str):
        self.api = api
        return self

    def add_header(self, key: str, value: str):
        self.headers[key] = value
        return self

    def set_payload(self, payload: dict):
        self.payload = payload
        return self

    async def _log(self, method: str, response=None, error=None):
        log = ApiLog(
            request_url=f"{self.base_url}{self.api}",
            request_method=method.upper(),
            request_headers=self.headers,
            request_payload=self.payload,
            response_status=response.status_code if response else None,
            response_headers=dict(response.headers) if response else None,
            response_body=response.json() if response else None,
            error=str(error) if error else None
        )
        self.db.add(log)
        self.db.commit()

    async def post(self):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url=f"{self.base_url}{self.api}",
                    headers=self.headers,
                    json=self.payload
                )
                print(response.json())
            await self._log("POST", response=response)
            return response
        except Exception as e:
            await self._log("POST", error=e)
            raise e

    async def get(self):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url=f"{self.base_url}{self.api}",
                    headers=self.headers,
                    params=self.payload
                )
            await self._log("GET", response=response)
            return response
        except Exception as e:
            await self._log("GET", error=e)
            raise e
