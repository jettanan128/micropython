# -*- coding: utf-8 -*-

import pyb
import gc

import uasyncio.core as asyncio
import logging
asyncio.log.level = logging.INFO


from knxBaosListener import KnxBaosListener
from knxBaos import KnxBaos


class KnxBaosEventLoop(asyncio.EventLoop):
    def time(self):
        return pyb.millis()

    def wait(self, delay):
        asyncio.log.debug("Sleeping for: %s", delay)
        start = pyb.millis()
        while pyb.elapsed_millis(start) < delay:
            gc.collect()
            pyb.delay(10)

asyncio._event_loop_class = KnxBaosEventLoop


class KnxBaosApp(KnxBaosListener):
    """
    """
    def __init__(self):
        """
        """
        super(KnxBaosApp, self).__init__()

        self.baos = KnxBaos(self)

        self.init()

        # @todo: for a framework, get all datapoints features (dpt...)
        # @todo: implement dpt convertor

    def init(self):
        """ Additional init for real app
        """
        self._logger.debug("init()")

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
        self.baos.start(loop)

        loop.create_task(self.loop())
        loop.run_forever()

    def dataToValue(self, data):
        sign = (data & 0x8000) >> 15
        exp = (data & 0x7800) >> 11
        mant = data & 0x07ff
        if sign != 0:
            mant = -(~(mant - 1) & 0x07ff)
        value = (1 << exp) * 0.01 * mant
        #Logger().debug("DPT2ByteFloat.dataToValue(): sign=%d, exp=%d, mant=%r" % (sign, exp, mant))
        #Logger().debug("DPT2ByteFloat.dataToValue(): value=%.2f" % value)
        return value

    def valueToData(self, value):
        sign = 0
        exp = 0
        if value < 0:
            sign = 1
        mant = int(value * 100)
        while not -2048 <= mant <= 2047:
            mant = mant >> 1
            exp += 1
        #Logger().debug("DPT2ByteFloat.valueToData(): sign=%d, exp=%d, mant=%r" % (sign, exp, mant))
        data = (sign << 15) | (exp << 11) | (int(mant) & 0x07ff)
        #Logger().debug("DPT2ByteFloat.valueToData(): data=%s" % hex(data))
        return data
