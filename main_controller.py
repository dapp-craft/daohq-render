import io
import json
import os
import sys
import asyncio

import aioboto3
import httpx
from fastapi import APIRouter, Request
import playwright

from playwright.async_api import async_playwright, Page

from settings import BACKEND_URL, SYSTEM_TOKEN, FILES_BUCKET_FOLDER, FILES_BUCKET_NAME


router = APIRouter()

aws_session = aioboto3.Session()

lock = asyncio.Lock()


@router.post('/discord/image')
async def discord_screenshot(request: Request, message: dict, update: bool = False):
    async with lock:
        messageId = message['message_id']

        with open(f'static/{messageId}.json', 'w') as file:
            json.dump(message, file, indent=4)

        print(f"Rendering of msg {messageId} update {update} started")
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page(viewport={'width': 450, 'height': 800})
            await page.goto(f'http://127.0.0.1:8010/static/discord/index.html?msg=/static/{messageId}.json')

            await waitPageRenderComplete(page, f'Message {messageId}')

            screenshot_bytes = await page.screenshot()
            screenshot_buffer = io.BytesIO(screenshot_bytes)

            os.remove(f'static/{messageId}.json')
            await browser.close()
        print(f"Rendering of msg {messageId} update {update} finished")

        guild = message['guild']
        channel= message['channel']
        
        save_path = f'{FILES_BUCKET_FOLDER}/{guild}-{channel}/{messageId}'
        
        async with aws_session.client('s3') as s3:
            await s3.put_object(
                Bucket=FILES_BUCKET_NAME,
                Key=save_path,
                Body=screenshot_buffer,
                ContentType='image/png',
            )
        s3_urn = f'https://{FILES_BUCKET_NAME}.s3.amazonaws.com/{save_path}'
        
        if not update:
            async with httpx.AsyncClient() as client:
                await client.post(f'{BACKEND_URL}/discord/images', params={
                    's3_urn': s3_urn, 
                    'guild': guild, 
                    'channel': channel,
                    'jump_url': message['jump_url']
                    },
                    headers={'Authorize': SYSTEM_TOKEN}
                )
        else:
            async with httpx.AsyncClient() as client:
                await client.put(f'{BACKEND_URL}/discord/images', params={
                    'jump_url': message['jump_url']
                    },
                    headers={'Authorize': SYSTEM_TOKEN}
                )

        return s3_urn


@router.post('/metrics/image')
async def metrics_screenshot():


    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(device_scale_factor=1.5)
        await page.goto(f'http://127.0.0.1:8010/static/metrics/metrics.html')

        await waitPageRenderComplete(page, 'Metrics')

        divs = await page.query_selector_all('.metrics-output')

        metrics = {}
        for div in divs:
            div_id = await div.get_attribute('id')
            screenshot_bytes = await div.screenshot()
            screenshot_buffer = io.BytesIO(screenshot_bytes)

            save_path = f'{FILES_BUCKET_FOLDER}/metrics/{div_id}'
            async with aws_session.client('s3') as s3:
                await s3.put_object(
                    Bucket=FILES_BUCKET_NAME,
                    Key=save_path,
                    Body=screenshot_buffer,
                    ContentType='image/png',
                )
            
            s3_urn = f'https://{FILES_BUCKET_NAME}.s3.amazonaws.com/{save_path}'

            metrics[div_id] = s3_urn

        await browser.close()

    async with httpx.AsyncClient() as client:
        await client.post(
            f'{BACKEND_URL}/metrics/images', 
            json=metrics,
            headers={'Authorize': SYSTEM_TOKEN}
        )

    return s3_urn



async def waitPageRenderComplete(page: Page, name: str):
    completeEventName = await page.evaluate("() => window.completeEventName")
    if completeEventName:
        try:
            # await page.wait_for_event(completeEventName, timeout=5000)
            await page.wait_for_function(f"() => window.{completeEventName}", timeout=5000)
        except playwright._impl._errors.TimeoutError:
            print(f'{name} did not respond.', file=sys.stderr)
