# -*- coding: utf-8 -*-

import pyb

import uasyncio.core as asyncio

from knxBaosApp import KnxBaosApp

# Data point assignment
DP_SWITCH_OR_STEP_O = 1  # output for binary Switch
DP_SWITCH_DIM_OR_MOVE_O = 2  # output for relative dimming or shutter move (see parameter byte #1)
DP_LED0_SWITCH_I = 3  # input switch for LED (see also parameter byte #2)
DP_LED0_DIM_RELATIVE_I = 4  # input dimmer for LED
DP_LED0_DIM_ABSOLUTE_I = 5  # input absolute dimmer value for LED

# Parameter byte assignment
PB_SWITCH_TYPE = 1  # configuration for DP#1 and #2
PB_LIGHT_TYPE = 2  # configuration for DP#3, #4 and #5

# Parameter byte #1 configuration.
# Usage of data points #1 and #2 (sensors)
ST_DISABLED = 0  # Datapoints are disabled
ST_SWITCH = 1  # used as binary switch
ST_DIMMER = 2  # used as dimmer
ST_SHUTTER = 3  # used as shutter control

# Parameter byte #2 configuration.
# Usage of data points #3, #4 and #5 (actuators)
LT_DISABLED = 0  # Datapoints are disabled
LT_SWITCH = 1  # LED switch
LT_DIMMER = 2  # LED dimmer

# Values for the KNX telegram controlling LED switching on/off
SWITCH_OFF = 0  # LED off
SWITCH_ON  = 1  # LED on

# Values for the KNX telegram controlling the shutter
SHUTTER_STEP_UP = 0  # shutter one step up
SHUTTER_STEP_DOWN = 1  # shutter one step down
SHUTTER_MOVE_UP = 0  # shutter move up
SHUTTER_MOVE_DOWN = 1  # shutter move down


class MyApp(KnxBaosApp):
    """
    """
    def init(self):
        """
        """
        self._button = pyb.IO

    def loop(self):
        """
        """
        while True:
            # do somthing usefull, like check buttons, dim light...

            # Let some time to the KnxBaosApp to run
            asyncio.sleep(100)

    def handleGetDatapointValueRes(self, dpId, dpState, dpData):
        self.handleDatapointValueInd(self, dpId, dpState, dpData)

    def handleDatapointValueInd(self, dpId, dpState, dpData):
        if dpId == DP_LED0_SWITCH_I:
            if dpData == SWITCH_ON:
                self._dimSwitch(True)
            elif dpData == SWITCH_OFF:
                self._dimSwitch(False)

        elif dpId == DP_LED0_DIM_RELATIVE_I:
            self._dimRelative(dpData)

        elif dpId == DP_LED0_DIM_ABSOLUTE_I:
            self._dimAbsolute(dpData*255/100)

        #@todo: check dpData length for each command

    def handleGetParameterByteRes(self, byteNum, byteData):
        if byteNum == PB_SWITCH_TYPE:
            self._switchType = byteData

        elif byteNum == PB_LIGHT_TYPE:
            self._lightType = byteData


myApp = MyApp()
myApp.run()
