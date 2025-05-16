import logging
from asyncio import sleep

from just_playback import Playback

from file_util import follow
from tts import play_speech


async def node_death_monitor(path: str):
    async for line in follow(path):
        if 'user interrupted with ctrl-c (SIGINT)' in line:
            break

        if 'process has died' not in line:
            continue

        if '__node:=' in line:
            node_name = line[line.find('__node:=') + 8:].split(' ', 1)[0]
        else:
            node_name = line.split(' ', 4)[2][1:-2]
        node_name = node_name.replace('_', ' ')
        try:
            await play_speech(f'{node_name} が異常終了しました')
        except Exception as e:
            logging.error(e)
            playback = Playback(f'node_died.mp3')
            playback.play()
            while playback.active:
                await sleep(0.01)
