import usayncio.core as asyncio

from knxBaosListener import KnxBaosListener


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

        self.init()

    def init(self):
        """ Additional init for real app
        """
        pass

    @asyncio.coroutine
    def loop(self):
        """ Real app. loop (coroutine)
        """

    def run(self):
        """ Start event loop and so

        Instanciate all FT12 stuff, handlers... and run needed coroutines
        """
        loop = asyncio.get_event_loop()

        baos = KnxBaos(self)
        baos.reset()
        #baos.getParam(1)
        #baos.getDatapoint(1)

        baos.start()

        loop.create_task(self.loop())

        loop.run_forever()



def main():


if __name__ == "__main__":
    main()
