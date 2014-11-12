# -*- coding: utf-8 -*-

""" Sensirion SHT1x & SHT7x family temperature and humidity sensors
"""

import pyb
import gc

import logging
import uasyncio.core as asyncio

import mpr121

from sht15 import SHT15, InvalidMeasure


class MyEventLoop(asyncio.EventLoop):
    def time(self):
        return pyb.millis()

    def wait(self, delay):
        log = logging.getLogger("asyncio")
        log.debug("Sleeping for: %s", delay)
        start = pyb.millis()
        while pyb.elapsed_millis(start) < delay:
            gc.collect()
            pyb.delay(10)

asyncio._event_loop_class = MyEventLoop


@asyncio.coroutine
def backlight(lcd, autoOff=10000):
    """ LCD backlight management
    """
    logger = logging.getLogger("backlight")

    switch = pyb.Switch()
    touch = mpr121.MPR121(pyb.I2C(1, pyb.I2C.MASTER))

    backlight = False
    backlightOnTime = 0
    previousSwitch = False

    while True:
        #logger.debug("backlight")
        if touch.touch_status() or switch():
            if not previousSwitch:
                if backlight:
                    logger.info("backlight off")
                    lcd.light(False)
                    backlight = False
                else:
                    logger.info("backlight on")
                    lcd.light(True)
                    backlight = True
                    backlightOnTime = pyb.millis()
                previousSwitch = True
        else:
            previousSwitch = False

        # Auto switch off screen after 10s
        # @todo: register a callback with EventLoop.call_later()?
        if backlight and pyb.elapsed_millis(backlightOnTime) >= autoOff:
            logger.info("backlight auto off")
            lcd.light(False)
            backlight = False

        yield from asyncio.sleep(10)


@asyncio.coroutine
def display(sht15, lcd, refresh=1000):
    """ Print data
    """
    logger = logging.getLogger("display")
    rtc = pyb.RTC()
    rtc.datetime((2014, 1, 1, 1, 0, 0, 0, 0))

    while True:
        try:
            h, m, s = rtc.datetime()[4:7]
            measure = h, m, s, gc.mem_free(), sht15.temperature, sht15.humidity, sht15.dewPoint
            logger.info("%02d:%02d:%02d %d:temperature=%.1f C, humidity=%.1f%%, dew point=%.1f C", *measure)
            lcd.write("%02d:%02d:%02d %d\ntemp=%.1f C\nhumidity=%.1f%%\ndew point=%.1f C\n" % measure)
        except InvalidMeasure:
            logger.warning("measure not yet available")

        yield from asyncio.sleep(refresh)


@asyncio.coroutine
def info(refresh=10000):
    """ Print pyb info
    """
    while True:
        pyb.info()

        yield from asyncio.sleep(refresh)


def main():
    logging.basicConfig(logging.DEBUG)

    logger = logging.getLogger("asyncio")
    logger.level = logging.INFO

    lcd = pyb.LCD('X')
    lcd.contrast(25)

    sht15 = SHT15('Y11', 'Y12')

    loop = asyncio.get_event_loop()

    loop.create_task(sht15.loop(refresh=5000))
    loop.create_task(display(sht15, lcd, refresh=1000))
    loop.create_task(backlight(lcd, autoOff=10000))
    #loop.create_task(info(refresh=10000))

    loop.run_forever()


if __name__ == "__main__":
    main()
