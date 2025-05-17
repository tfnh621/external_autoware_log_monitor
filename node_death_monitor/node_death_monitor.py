import logging
from asyncio import sleep
from fnmatch import fnmatch
from pathlib import Path

from aiofiles import open
from just_playback import Playback

from file_util import follow
from tts import play_speech


async def node_death_monitor(path: str):
    async with open(Path(__file__).resolve().parent / 'ignore_node_list.txt') as f:
        ignore_nodes = [line.strip() for line in await f.readlines()]

    async for line in follow(path):
        if 'user interrupted with ctrl-c (SIGINT)' in line:
            break

        if 'process has died' not in line:
            continue

        if '__node:=' in line:
            node_name = line[line.find('__node:=') + 8:].split(' ', 1)[0]
        else:
            node_name = line.split(' ', 4)[2][1:-2]

        if any([fnmatch(node_name, pattern) for pattern in ignore_nodes]):
            continue

        node_name = node_name.replace('_', ' ')
        try:
            await play_speech(f'{node_name} が異常終了しました')
        except Exception as e:
            logging.error(e)
            playback = Playback(str(Path(__file__).resolve().parent / 'node_died.mp3'))
            playback.play()
            while playback.active:
                await sleep(0.01)
