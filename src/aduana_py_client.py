"""A client for the Aduana Paraguay API."""

import json
from typing import Any, Final, Generator

import httpx


class AduanaPYClient:
    """
    A client for the AduanaPY API.
    """

    PER_PAGE: Final[int] = 1000
    PAYLOAD_TEMPLATE_PATH: Final[str] = "src/aduana_py_payload.json"

    def __init__(self, base_url: str):
        """
        Initializes the AduanaPYClient.
        """
        self.base_url = base_url

    def _get_headers(self) -> dict[str, str]:
        """
        Returns the headers to be sent with the request.

        Returns:
            dict[str, str]: The headers to be sent with the request.
        """
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3",
            # 'Accept-Encoding': 'gzip, deflate, br',
            "Content-Type": "application/json",
            "Origin": "https://datosabiertos.aduana.gov.py",
            "Connection": "keep-alive",
            "Referer": "https://datosabiertos.aduana.gov.py/ddaa/app/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
        }

    def _get_payload_template(self) -> dict[str, Any]:
        """
        Returns the payload template.

        Returns:
            dict[str, Any]: The payload template.
        """
        with open(self.PAYLOAD_TEMPLATE_PATH, "r") as file:
            template_str = file.read()

        return json.loads(template_str)

    def _get_payload(self, page: int, anio: str, posicion: str) -> dict[str, Any]:
        """
        Returns a payload to be sent to the API.

        Args:
            page (int): The page number.
            anio (str): The year to fetch data from.
            posicion (str): The position to fetch data from.

        Returns:
            dict[str, Any]: The payload to be sent to the API.
        """
        payload = self._get_payload_template()

        payload["page"] = page
        payload["perPage"] = self.PER_PAGE
        payload["filters"][0]["value"] = anio
        payload["filters"][1]["value"] = posicion

        return payload

    def _get_paginated_payload(self, anio: str, posicion: str) -> Generator:
        """
        Generator that yields payloads for each page.

        Args:
            anio (str): The year to fetch data from.
            posicion (str): The position to fetch data from.

        Yields:
            dict[str, Any]: The payload to be sent to the API.
        """
        page = 1

        while True:
            yield self._get_payload(page, anio, posicion)
            page += 1

    def fetch_paginated(self, anio: str, posicion: str) -> list[dict]:
        """
        Fetches all data for the given year and position.

        Args:
            anio (str): The year to fetch data from.
            posicion (str): The position to fetch data from.

        Returns:
            list[dict]: A list of dictionaries containing the fetched data.
        """
        print(f"Fetching posicion {posicion} for year {anio}...")

        result = []
        fetched = 0

        while True:
            payload_generator = self._get_paginated_payload(anio, posicion)
            payload = next(payload_generator)

            res = httpx.post(
                self.base_url, headers=self._get_headers(), json=payload, timeout=90
            )

            res_json = res.json()

            if not res_json["success"]:
                raise Exception(res_json["message"])

            res_payload = res_json["payload"]
            data = res_payload["gridData"]

            result.extend(data)
            fetched += len(data)

            if fetched >= res_payload["totalCount"]:
                break

        return result
