import json

import httpx
from quart import current_app

from ..dependencies.config import API_URL


async def api_get_ip() -> str:
    client: httpx.AsyncClient = current_app.extensions['httpx_client']
    response: httpx.Response = await client.get(
        url= f'http://{API_URL}/config/ip',
        headers= {
            'accept': 'application/json'
        }
    )
    return json.dumps(response.json())

async def api_get_origins() -> list[str]:
    client: httpx.AsyncClient = current_app.extensions['httpx_client']
    response: httpx.Response = await client.get(
            url= f'http://{API_URL}/origin/?limit=100&offset=0',
            headers= {
                'accept': 'application/json'
            }
        )
    origins: list[str] = [origin['name'] for origin in response.json()]
    return origins

async def api_get_models() -> list[str]:
    client: httpx.AsyncClient = current_app.extensions['httpx_client']
    response: httpx.Response = await client.get(
            url= f'http://{API_URL}/model/?limit=100&offset=0',
            headers= {
                'accept': 'application/json'
            }
        )
    models: list[str] = [model['name'] for model in response.json()]
    return models

async def api_get_inspection_results() -> list[str]:
    client: httpx.AsyncClient = current_app.extensions['httpx_client']
    response: httpx.Response = await client.get(
        url= f'http://{API_URL}/inspection-result/?limit=100&offset=0',
        headers= {
            'accept': 'application/json'
        }
    )
    results: list[str] = [result['name'] for result in response.json()]
    return results

async def api_get_image_extensions() -> list[str]:
    client: httpx.AsyncClient = current_app.extensions['httpx_client']
    response: httpx.Response = await client.get(
        url= f'http://{API_URL}/image/extensions',
        headers= {
            'accept': 'application/json'
        }
    )
    results: list[str] = [result for result in response.json()]
    return results
