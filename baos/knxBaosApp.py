# -*- coding: utf-8 -*-

import pyb
import gc

import uasyncio.core as asyncio
import logging
asyncio.log.level = logging.INFO


from knxBaosListener import KnxBaosListener
from knxBaos import KnxBaos


class MyEventLoop(asyncio.EventLoop):
    def time(self):
        return pyb.millis()

    def wait(self, delay):
        asyncio.log.debug("Sleeping for: %s", delay)
        start = pyb.millis()
        while pyb.elapsed_millis(start) < delay:
            gc.collect()
            pyb.delay(10)

asyncio._event_loop_class = MyEventLoop


class KnxBaosApp(KnxBaosListener):
    """
    """
    def __init__(self):
        """
        """
        super(KnxBaosApp, self).__init__()

        self.baos = KnxBaos(self)

        self.init()

    def init(self):
        """ Additional init for real app
        """
        pass

    @asyncio.coroutine
    def loop(self):
        """ Real app. loop (coroutine)
        """
        raise NotImplementedError

    def run(self):
        """ Start event loop and so

        Instanciate all FT12 stuff, handlers... and run needed coroutines
        """
        loop = asyncio.get_event_loop()

        self.baos.reset()
        #baos.getParam(1)
        #baos.getDatapoint(1)

        self.baos.start(loop)

        loop.create_task(self.loop())

        loop.run_forever()
