from multiprocessing.pool import ThreadPool

from src.aduana_py_client import AduanaPYClient
from src.config import Config


def main():
    aduana_client = AduanaPYClient(base_url=Config.ADUANA_PY_BASE_URL)

    pool = ThreadPool(processes=5)
    results = []

    for i in range(1, 6):
        async_result = pool.apply_async(
            aduana_client.fetch_paginated, ("2023", f"310{i}.00.00")
        )

        results.append(async_result)

    flat_results = []
    for result in results:
        flat_results.extend(result.get())


if __name__ == "__main__":
    main()
