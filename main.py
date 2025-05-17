import logging
from asyncio import Task, run, create_task

from log_watcher.autoware_launch import wait_for_autoware_launch_log
from node_death_monitor.node_death_monitor import node_death_monitor


async def main():
    current_tasks: list[Task] = []
    async for path in wait_for_autoware_launch_log():
        for task in current_tasks:
            task.cancel()

        current_tasks.append(create_task(node_death_monitor(path)))


if __name__ == '__main__':
    def is_debugger_attached():
        import sys
        return sys.gettrace() is not None


    if is_debugger_attached():
        logging.basicConfig(level=logging.DEBUG)
        logging.getLogger().setLevel(logging.DEBUG)
        run(main(), debug=True)
    else:
        run(main())
