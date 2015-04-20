# -*- coding: utf-8 -*-

""" PS2 gamepad python support for Micropython (pyboard)

 - PyS2x http://www.github.com/fma38/micropython/PyS2X is Copyright:
  - (C) 2015 Frederic Mantegazza
  - (C) 2011-1013 Bill Porter

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
or see:

    http://www.gnu.org/licenses/gpl.html

See https:# github.com/madsci1016/Arduino-PyS2x for original Arduino code
"""

import pyb

import logging

CTRL_BYTE_DELAY = 0  # does not seem necessary, at least on a real Sony DualShock 2
MAX_DELAY = 1500

# Button constants
BUTTON_SELECT      = 0x0001
BUTTON_L3          = 0x0002
BUTTON_R3          = 0x0004
BUTTON_START       = 0x0008
BUTTON_PAD_UP      = 0x0010
BUTTON_PAD_RIGHT   = 0x0020
BUTTON_PAD_DOWN    = 0x0040
BUTTON_PAD_LEFT    = 0x0080
BUTTON_L2          = 0x0100
BUTTON_R2          = 0x0200
BUTTON_L1          = 0x0400
BUTTON_R1          = 0x0800
BUTTON_GREEN       = 0x1000
BUTTON_TRIANGLE    = 0x1000
BUTTON_RED         = 0x2000
BUTTON_CIRCLE      = 0x2000
BUTTON_BLUE        = 0x4000
BUTTON_CROSS       = 0x4000
BUTTON_PINK        = 0x8000
BUTTON_SQUARE      = 0x8000

# Sticks values
PAD_RX = 5
PAD_RY = 6
PAD_LX = 7
PAD_LY = 8

# Analog buttons
ANALOG_PAD_RIGHT   =  9
ANALOG_PAD_LEFT    = 10
ANALOG_PAD_UP      = 11
ANALOG_PAD_DOWN    = 12
ANALOG_GREEN       = 13
ANALOG_TRIANGLE    = 13
ANALOG_RED         = 14
ANALOG_CIRCLE      = 14
ANALOG_BLUE        = 15
ANALOG_CROSS       = 15
ANALOG_PINK        = 16
ANALOG_SQUARE      = 16
ANALOG_L1          = 17
ANALOG_R1          = 18
ANALOG_L2          = 19
ANALOG_R2          = 20

# Guitar Hero buttons constants
UP_STRUM        = 0x0010
DOWN_STRUM      = 0x0040
STAR_POWER      = 0x0100
GREEN_FRET      = 0x0200
YELLOW_FRET     = 0x1000
RED_FRET        = 0x2000
BLUE_FRET       = 0x4000
ORANGE_FRET     = 0x8000
WHAMMY_BAR      = 8

# Controllers
GUITAR_HERO = 0x01
DUALSHOCK = 0x03
WIRELESS_DUALSHOCK = 0x0c
CONTROLLER_NAME = {
    GUITAR_HERO: "GuitarHero",
    DUALSHOCK: "DualShock",
    WIRELESS_DUALSHOCK: "Wireless DualShock"
}

ENTER_CONFIG = bytearray((0x01, 0x43, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00))
SET_MODE = bytearray((0x01, 0x44, 0x00, 0x01, 0x03, 0x00, 0x00, 0x00, 0x00))
SET_BYTES_LARGE = bytearray((0x01, 0x4f, 0x00, 0xff, 0xff, 0x03, 0x00, 0x00, 0x00))
EXIT_CONFIG = bytearray((0x01, 0x43, 0x00, 0x00, 0x5a, 0x5a, 0x5a, 0x5a, 0x5a))
ENABLE_RUMBLE = bytearray((0x01, 0x4d, 0x00, 0x00, 0x01))
TYPE_READ = bytearray((0x01, 0x45, 0x00, 0x5a, 0x5a, 0x5a, 0x5a, 0x5a, 0x5a))

CS_PIN = "Y5"
SPI_PORT = 2
SPI_BAUDRATE = 500000

MOTOR_2_MIN = 0x40  # nothing below 0x40 will make it spin?
MOTOR_2_MAX = 0xff

LOGGING_LEVEL = logging.INFO


class PyS2xError(Exception):
    """
    """


class PyS2x(object):
    """
    """
    def __init__(self):
        """
        """
        super(PyS2x, self).__init__()

        self._logger = logging.getLogger("PyS2x")
        self._logger.level = LOGGING_LEVEL

        self._pressure = False
        self._rumble = False
        self._controllerType = None

        self._buttons = 0xffff
        self._buttonsPrev = self._buttons

        self._lastRefreshTimeStamp = 0
        self._refreshDelay = 1
        self._rawData = 21 * [0]

        # SPI stuff
        self._cs = pyb.Pin(CS_PIN, pyb.Pin.OUT_PP)
        self._cs.high()
        self._spi = pyb.SPI(SPI_PORT, pyb.SPI.MASTER, firstbit=pyb.SPI.LSB, baudrate=SPI_BAUDRATE, polarity=1, phase=1, crc=None)

    @property
    def pressure(self):
        return self._pressure

    @property
    def rumble(self):
        return self._rumble

    @property
    def controllerType(self):
        return self._controllerType

    @property
    def buttonDataByte(self):
        return ~self._buttons

    def newButtonState(self, button=None):
        """
        """
        if button is None:
            return (self._buttonsPrev ^ self._buttons) > 0
        else:
            return ((self._buttonsPrev ^ self._buttons) & button) > 0

    def buttonPressed(self, button):
        """
        """
        return self.newButtonState(button) & self.button(button)

    def buttonReleased(self, button):
        """
        """
        return self.newButtonState(button) & ((~self._buttonsPrev & button) > 0)

    def button(self, button):
        """
        """
        return (~self._buttons & button) > 0

    def analog(self, button):
        """
        """
        return self._rawData[button]

    def _sendCmd(self, cmd):
        """
        """
        self._cs.low()  # low enable joystick
        pyb.udelay(CTRL_BYTE_DELAY)

        ans = []
        for byte in cmd:
            ans_ = self._spi.send_recv(byte)
            pyb.udelay(CTRL_BYTE_DELAY)
            ans.append(int.from_bytes(ans_))

        self._cs.high()  # high disable joystick
        pyb.delay(self._refreshDelay)

        return ans

    def _configure(self, getControllerType=False):
        """
        """
        self._logger.debug("_configure(): send ENTER_CONFIG")
        self._sendCmd(ENTER_CONFIG)

        if getControllerType:
            self._logger.debug("_configure(): send TYPE_READ")
            ans = self._sendCmd(TYPE_READ)
            self._controllerType = ans[3]
            self._logger.debug("configure()): _controllerType=%d" % self._controllerType)

        self._logger.debug("_configure(): send SET_MODE")
        self._sendCmd(SET_MODE)

        if self._rumble:
            self._logger.debug("_configure(): send ENABLE_RUMBLE")
            self._sendCmd(ENABLE_RUMBLE)

        if self._pressure:
            self._logger.debug("_configure(): send SET_BYTES_LARGE")
            self._sendCmd(SET_BYTES_LARGE)

        self._logger.debug("_configure(): send EXIT_CONFIG")
        self._sendCmd(EXIT_CONFIG)

    def configure(self, pressure=True, rumble=True):
        """ Configure gamepad
        """

        # Dummy read
        self.refresh()
        #self.refresh()
        # Note: one call seems to be enough, at least on a real Sony DualShock 2
        # TODO : try to call _configure() instead

        # If still anything but 0x41, 0x73 or 0x79, then it's not talking
        if self._rawData[1] not in (0x41, 0x73, 0x79):
            self._logger.critical("Controller mode not matched or no controller found")
            self._logger.critical("Expected 0x41, 0x73 or 0x79, got 0x%02x" % self._rawData[1])
            self._logger.critical("Check wiring...")

            raise PyS2xError

        self._pressure = pressure
        self._rumble = rumble

        for retry in range(10):
            self._configure(getControllerType=True)
            self.refresh()

            if pressure :
                if self._rawData[1] == 0x79:
                    break

                elif self._rawData[1] == 0x73:
                    self._logger.warning("Controller refusing to enter 'pressure' mode; may not support it")
                    break

            if self._rawData[1] == 0x73:
                break

            if self._rawData[1] & 0xf0 != 0x70:
                if self._refreshDelay < 10:
                    self._refreshDelay += 1  # see if this helps out...
                    self._logger.warning("configure()): increased _refreshDelay to %d" % self._refreshDelay)

        else:
            self._logger.critical("Controller not accepting commands")
            self._logger.critical("Mode still set at %s" % hex(self._rawData[1]))
            raise PyS2xError

    def refresh(self, smallMotorEnable=False, largeMotorSpeed=0x00):
        """ Refresh gamepad inputs
        """

        # Check last refresh time stamp
        delay = pyb.millis() - self._lastRefreshTimeStamp

        # Waited to long?
        if delay > MAX_DELAY:
            self._configure()

        # Waited too short?
        elif delay < self._refreshDelay:
            pyb.delay(self._refreshDelay - delay)

        if largeMotorSpeed != 0:
            largeMotorSpeed = int(MOTOR_2_MIN + largeMotorSpeed / 0xff * (MOTOR_2_MAX - MOTOR_2_MIN))

        READ_1 = bytearray((0x01, 0x42, 0x00, smallMotorEnable, largeMotorSpeed, 0x00, 0x00, 0x00, 0x00))
        READ_2 = bytearray((0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00))

        # Try a few times to get valid data...
        for retry in range(5):
            if retry:
                self._logger.warning("refresh(): retry=%d" % retry)

            self._cs.low()  # low enable joystick
            pyb.udelay(CTRL_BYTE_DELAY)

            # Send the command to send button and joystick data
            #self._logger.debug("refresh(): send button/joystick data...")
            for i, byte in enumerate(READ_1):
                ans = self._spi.send_recv(byte)
                self._rawData[i] = int.from_bytes(ans)

            # If controller is in full data return mode, get the rest of data
            if self._rawData[1] == 0x79:
                #self._logger.debug("refresh()): controller is in full data return mode. Read rest of data...")
                for i, byte in enumerate(READ_2):
                    ans = self._spi.send_recv(byte)
                    self._rawData[i+9] = int.from_bytes(ans)

            self._cs.high()  # high disable joystick
            pyb.udelay(CTRL_BYTE_DELAY)

            # Check to see if we received valid data or not
            # We should be in analog mode for our data to be valid
            if self._rawData[1] & 0xf0 == 0x70:
                break

            # If we got to here, we are not in analog mode
            # Try to recover: get back into analog mode
            self._configure()
            pyb.delay(self._refreshDelay)

        # If we get here and still not in analog mode (0x7_), try increasing _refreshDelay...
        #if self._rawData[1] & 0xf0 != 0x70:
        else:
            if self._refreshDelay < 10:
                self._refreshDelay += 1  # see if this helps out...
                self._logger.warning("refresh()): increased _refreshDelay to %d" % self._refreshDelay)

        # Store the previous buttons states
        self._buttonsPrev = self._buttons

        # Store as one value for multiple functions
        self._buttons = (self._rawData[4] << 8) + self._rawData[3]

        self._lastRefreshTimeStamp = pyb.millis()

        #return (self._rawData[1] & 0xf0) == 0x70


def main():
    logger = logging.getLogger("main()")
    logger.level = LOGGING_LEVEL

    smallMotorEnable = False
    largeMotorSpeed = 0

    pys2x = PyS2x()

    # Add delay to give wireless ps2 module some time to startup, before configuring it
    pyb.delay(250)

    pys2x.configure(pressure=True, rumble=True)
    logger.info("Found Controller, configured successful (pressure=%s, rumble=%s)" % (pys2x.pressure, pys2x.rumble))
    logger.info("Try out all the buttons, X will vibrate the controller, faster as you press harder.")
    logger.info("Holding L1 or R1 will print out the analog stick values.")

    try:
        logger.info("%s controller found" % CONTROLLER_NAME[pys2x.controllerType])
    except KeyError:
        logger.critical("Unknown Controller type found (0x%02x)" % pys2x.controllerType)
        raise SystemExit

    while True:

        # You must Refresh Gamepad to get new values and set vibration values
        # >>> pys2x.refresh(small motor on/off, larger motor strenght from 0-255)
        # If you don't enable the rumble, use pys2x.refresh() with no values
        # You should call this at least once per second

        if pys2x.controllerType == GUITAR_HERO:

            # Refresh controller
            pys2x.refresh()

            if pys2x.buttonPressed(GREEN_FRET):
                logger.info("Green Fret Pressed")
            if pys2x.buttonPressed(RED_FRET):
                logger.info("Red Fret Pressed")
            if pys2x.buttonPressed(YELLOW_FRET):
                logger.info("Yellow Fret Pressed")
            if pys2x.buttonPressed(BLUE_FRET):
                logger.info("Blue Fret Pressed")
            if pys2x.buttonPressed(ORANGE_FRET):
                logger.info("Orange Fret Pressed")

            if pys2x.buttonPressed(STAR_POWER):
                logger.info("Star Power Command")

            if pys2x.button(UP_STRUM):
                logger.info("Up Strum")
            if pys2x.button(DOWN_STRUM):
                logger.info("DOWN Strum")

            if pys2x.button(BUTTON_START):
                logger.info("Start is being held")
            if pys2x.button(BUTTON_SELECT):
                logger.info("Select is being held")

            if pys2x.button(ORANGE_FRET):
                logger.info("Wammy Bar Position: 0x%02x" % pys2x.analog(WHAMMY_BAR))

        else:

            # Refresh controller and set large motor to spin at 'largeMotorSpeed' speed
            pys2x.refresh(smallMotorEnable, largeMotorSpeed)
            logger.debug((len(pys2x._rawData) * "0x%02x ") % tuple(pys2x._rawData))

            if pys2x.button(BUTTON_START):
                logger.info("Start is being held")
            if pys2x.button(BUTTON_SELECT):
                logger.info("Select is being held")

            if pys2x.button(BUTTON_PAD_UP):
                logger.info("Up held this hard: 0x%02x" % pys2x.analog(ANALOG_PAD_UP))

            if pys2x.button(BUTTON_PAD_RIGHT):
                logger.info("Right held this hard: 0x%02x" % pys2x.analog(ANALOG_PAD_RIGHT))

            if pys2x.button(BUTTON_PAD_LEFT):
                logger.info("LEFT held this hard: 0x%02x" % pys2x.analog(ANALOG_PAD_LEFT))

            if pys2x.button(BUTTON_PAD_DOWN):
                logger.info("DOWN held this hard: 0x%02x" % pys2x.analog(ANALOG_PAD_DOWN))

            if pys2x.newButtonState():
                if pys2x.button(BUTTON_R1):
                    logger.info("R1 pressed")
                if pys2x.button(BUTTON_R2):
                    logger.info("R2 pressed")
                if pys2x.button(BUTTON_R3):
                    logger.info("R3 pressed")
                if pys2x.button(BUTTON_L1):
                    logger.info("L1 pressed")
                if pys2x.button(BUTTON_L2):
                    logger.info("L2 pressed")
                if pys2x.button(BUTTON_L3):
                    logger.info("L3 pressed")

            if pys2x.buttonPressed(BUTTON_TRIANGLE):
                logger.info("Triangle pressed")
            if pys2x.buttonPressed(BUTTON_CIRCLE):
                logger.info("Circle just pressed")
            if pys2x.newButtonState(BUTTON_CROSS):
                logger.info("X just changed")
            if pys2x.buttonReleased(BUTTON_SQUARE):
                logger.info("Square just released")

            # Set the large motor speed based on how hard blue (X) button is pressed
            largeMotorSpeed = pys2x.analog(ANALOG_CROSS)
            if pys2x.button(BUTTON_CROSS):
                logger.info("large motor speed: 0x%02x" % largeMotorSpeed)

            # Set small motor to vibrate on hard red (O) button pressed
            smallMotorEnable = bool(pys2x.button(BUTTON_CIRCLE))

            if pys2x.button(BUTTON_L3):
                logger.info("Left stick values: x=0x%02x, y=0x%02x" % (pys2x.analog(PAD_LX), pys2x.analog(PAD_LY)))
            if pys2x.button(BUTTON_R3):
                logger.info("Right stick values:                x=0x%02x, y=0x%02x" % (pys2x.analog(PAD_RX), pys2x.analog(PAD_RY)))

        pyb.delay(50)


if __name__ == "__main__":
    main()
