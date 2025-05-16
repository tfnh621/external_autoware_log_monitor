from asyncio import sleep
from asyncio.subprocess import DEVNULL, create_subprocess_exec
from base64 import b64decode
from urllib.parse import quote

from aiofiles.tempfile import NamedTemporaryFile
from aiohttp import ClientSession
from just_playback import Playback


async def text_to_speech(text: str) -> bytes:
    endpoint = 'https://www.google.com/async/translate_tts'
    parameters = {'ttsp': f'tl:ja,txt:{quote(text)},spd:1', 'async': '_fmt:jspb'}

    async with ClientSession() as session:
        async with session.get(endpoint, params=parameters) as response:
            response_text = await response.text()

    return b64decode(response_text.split('"')[3])


async def play_speech(text: str) -> None:
    async with (NamedTemporaryFile() as f1, NamedTemporaryFile(suffix='.mp3') as f2):
        raw_audio_data = await text_to_speech(text)
        if raw_audio_data == b'':
            return

        await f1.write(raw_audio_data)
        await (await create_subprocess_exec('ffmpeg', '-i', f1.name, '-af', 'atempo=1.5', f2.name, '-y', stderr=DEVNULL)).communicate()

        playback = Playback(f2.name)
        playback.play()
        while playback.active:
            await sleep(0.01)
