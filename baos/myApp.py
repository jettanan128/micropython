# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, "baos")
import pyb
import struct
import logging

import uasyncio.core as asyncio
import mpr121

from knxBaos import KnxBaos
from knxBaosApp import KnxBaosApp

# Data point assignment
DP_FIRST = 1
DP_SW_LED_1 = 1  # input switch for LED 1 (commande chauffage sdb)
DP_SW_LED_2 = 2  # input switch for LED 2 (commande chauffage sejour)
DP_SW_LED_3 = 3  # input switch for LED 3 (commande chauffage degagement)
DP_SW_LED_4 = 4  # input switch for LED 4
DP_DIM_LED_4 = 5  # input dimming for LED 4
DP_TEMP = 6  # input for temperature (living)
DP_BUT_1 = 7  # output for button 1
DP_BUT_2 = 8  # output for button 2
DP_BUT_3 = 9  # output for button 3
DP_BUT_4 = 10  # output for button 4
DP_LAST = 10

# Parameter byte assignment
PB_DIM_STEP = 1  # configuration for dimming (step)
PB_DIM_SPEED = 2  # configuration for dimming (speed)

# Values for the KNX telegram controlling LED switching on/off
SWITCH_OFF = 0  # LED off
SWITCH_ON  = 1  # LED on

# Values for the KNX telegram controlling LED dimming
DIM_STEP_UP = 0  # dimmer one step up
DIM_STEP_DOWN = 1  # dimmer one step down

# Values for the KNX telegram controlling the shutter
SHUTTER_STEP_UP = 0  # Shutter one step up
SHUTTER_STEP_DOWN = 1  # Shutter one step down
SHUTTER_MOVE_UP  = 0  # Shutter move up
SHUTTER_MOVE_DOWN = 1  # Shutter move down

AUTO_SCREEN_OFF_DELAY = 10000  # ms


class MyApp(KnxBaosApp):
    """
    """
    def init(self):
        """
        """
        self._myLogger = logging.getLogger("MyApp")

        self._led = (pyb.LED(1), pyb.LED(2), pyb.LED(3), pyb.LED(4))

        self._lcd = pyb.LCD('X')
        self._lcd.contrast(25)

        self._parameters = 10 * [None]

    @asyncio.coroutine
    def loop(self):
        """
        """
        yield from self.baos.getServerItemReq(KnxBaos.ID_FIRMWARE_VER, 1)  # dummy request (first never answer)
        yield from asyncio.sleep(100)
        yield from self.baos.getParameterByteReq(1, 10)  # refresh parameters bytes
        yield from asyncio.sleep(100)
        yield from self.baos.getDatapointValueReq(DP_FIRST, DP_LAST-DP_FIRST+1)

        touch = mpr121.MPR121(pyb.I2C(1, pyb.I2C.MASTER))

        backlight = False
        backlightOnTime = 0

        switch = pyb.Switch()
        previousSwitch = False

        while True:

            # Manage screen backlight
            if switch():
                if not previousSwitch:
                    if backlight:
                        self._lcd.light(False)
                        backlight = False
                    else:
                        self._lcd.light(True)
                        backlight = True
                        backlightOnTime = pyb.millis()
                    previousSwitch = True
            else:
                previousSwitch = False

            # Auto switch off screen after 10s
            if backlight and pyb.elapsed_millis(backlightOnTime) >= AUTO_SCREEN_OFF_DELAY:
                self._lcd.light(False)
                backlight = False

            # Manage touch buttons
            if touch.touch_status():
                pass  # TODO

            # Let some time to the KnxBaosApp to run
            yield from asyncio.sleep(10)

    def handleGetServerItemRes(self, itemId, itemData):
        if itemId == KnxBaos.ID_HARDWARE_TYPE:
            self._myLogger.info("Hardware type = {}".format(repr("".join(chr(i) for i in itemData))))
        elif itemId == KnxBaos.ID_HARDWARE_VER:
            self._myLogger.info("Hardware version = {}.{}".format(itemData[0] >> 4, itemData[0] & 0x0f))
        elif itemId == KnxBaos.ID_FIRMWARE_VER:
            self._myLogger.info("Firmware version = {}.{}".format(itemData[0] >> 4, itemData[0] & 0x0f))
        elif itemId == KnxBaos.ID_MANUFACT_SYS:
            self._myLogger.info("Manufacturer code DEV = {}".format(repr("".join(chr(i) for i in itemData))))
        elif itemId == KnxBaos.ID_MANUFACT_APP:
            self._myLogger.info("Manufacturer code APP = {}".format(repr("".join(chr(i) for i in itemData))))
        elif itemId == KnxBaos.ID_APP_ID:
            self._myLogger.info("Application ID = {}".format(repr("".join(chr(i) for i in itemData))))
        elif itemId == KnxBaos.ID_APP_VER:
            self._myLogger.info("Application version = {}".format(hex(itemData[0])))
        elif itemId == KnxBaos.ID_SERIAL_NUM:
            self._myLogger.info("Serial number = {}".format(repr("".join(chr(i) for i in itemData))))
        elif itemId == KnxBaos.ID_TIME_RESET:
            self._myLogger.info("Time since reset = {} ms".format(struct.unpack(">L", "".join(chr(i) for i in itemData))[0]))
        elif itemId == KnxBaos.ID_BUS_STATE:
            self._myLogger.info("Bus connection state = {}".format({0: "disconnected", 1: "connected"}[itemData[0]]))
        elif itemId == KnxBaos.ID_MAX_BUFFER:
            self._myLogger.info("Maximal buffer size = {}".format(struct.unpack(">H", "".join(chr(i) for i in itemData))[0]))
        elif itemId == KnxBaos.ID_STRG_LEN:
            self._myLogger.info("Length of description string = {}".format(struct.unpack(">H", "".join(chr(i) for i in itemData))[0]))
        elif itemId == KnxBaos.ID_BAUDRATE:
            self._myLogger.info("Baudrate = {}".format({0: "unknown", 1: "19200", 2: "115200"}[itemData[0]]))
        elif itemId == KnxBaos.ID_BUFFER_SIZE:
            self._myLogger.info("Current buffer size = {} bytes".format(struct.unpack(">H", "".join(chr(i) for i in itemData))[0]))
        elif itemId == KnxBaos.ID_PROG_MODE:
            self._myLogger.info("Programming mode = {}".format({0: "off", 1: "on"}[itemData[0]]))
        else:
            super(MyApp, self).handleGetServerItemRes(itemId, itemData)

    def handleGetDatapointValueRes(self, dpId, dpState, dpData):
        self._myLogger.debug("handleGetDatapointValueRes(): dpId={}, dpState={}, dpData={}".format(dpId, dpState, repr(dpData)))
        self.handleDatapointValueInd(dpId, dpState, dpData)

    def handleDatapointValueInd(self, dpId, dpState, dpData):
        self._myLogger.debug("handleDatapointValueInd(): dpId={}, dpState={}, dpData={}".format(dpId, dpState, repr(dpData)))

        if dpId in (DP_SW_LED_1, DP_SW_LED_2, DP_SW_LED_3, DP_SW_LED_4):
            if dpData[0] == SWITCH_ON:
                self._led[dpId-1].on()
                self._myLogger.info("Led {} has been switched on".format(dpId))
            elif dpData[0] == SWITCH_OFF:
                self._led[dpId-1].off()
                self._myLogger.info("Led {} has been switched off".format(dpId))

        elif dpId == DP_DIM_LED_4:
            self._led[3].intensity(dpData[0])  # TODO: decode dpData with dimming value, or use absolute?
            self._myLogger.info("Led 4 new intensity is {}".format(dpData[0]))

        elif dpId == DP_TEMP:
            temp = self.dataToValue(dpData[0] * 256 + dpData[1])
            self._lcd.write("Temp: {} C\n\n\n\n".format(temp))
            self._myLogger.info("Temp is {}".format(temp))

        #@todo: check dpData length for each command

    def handleGetParameterByteRes(self, byteNum, byteData):
        self._myLogger.debug("handleGetParameterByteRes(): byteNum={}, byteData={}".format(byteNum, byteData))
        self._parameters[byteNum] = byteData


myApp = MyApp()
myApp.run()
