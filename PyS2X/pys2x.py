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

CTRL_BYTE_DELAY = 0
MAX_DELAY = 1500

# Button constants
PSB_SELECT      = 0x0001
PSB_L3          = 0x0002
PSB_R3          = 0x0004
PSB_START       = 0x0008
PSB_PAD_UP      = 0x0010
PSB_PAD_RIGHT   = 0x0020
PSB_PAD_DOWN    = 0x0040
PSB_PAD_LEFT    = 0x0080
PSB_L2          = 0x0100
PSB_R2          = 0x0200
PSB_L1          = 0x0400
PSB_R1          = 0x0800
PSB_GREEN       = 0x1000
PSB_RED         = 0x2000
PSB_BLUE        = 0x4000
PSB_PINK        = 0x8000
PSB_TRIANGLE    = 0x1000
PSB_CIRCLE      = 0x2000
PSB_CROSS       = 0x4000
PSB_SQUARE      = 0x8000

# Guitar Hero buttons constants
GREEN_FRET      = 0x0200
RED_FRET        = 0x2000
YELLOW_FRET     = 0x1000
BLUE_FRET       = 0x4000
ORANGE_FRET     = 0x8000
STAR_POWER      = 0x0100
UP_STRUM        = 0x0010
DOWN_STRUM      = 0x0040
WHAMMY_BAR      = 8

# Sticks values
PSS_RX = 5
PSS_RY = 6
PSS_LX = 7
PSS_LY = 8

# Analog buttons
PSAB_PAD_RIGHT   =  9
PSAB_PAD_UP      = 11
PSAB_PAD_DOWN    = 12
PSAB_PAD_LEFT    = 10
PSAB_L2          = 19
PSAB_R2          = 20
PSAB_L1          = 17
PSAB_R1          = 18
PSAB_GREEN       = 13
PSAB_RED         = 14
PSAB_BLUE        = 15
PSAB_PINK        = 16
PSAB_TRIANGLE    = 13
PSAB_CIRCLE      = 14
PSAB_CROSS       = 15
PSAB_SQUARE      = 16

# Controllers
DUALSHOCK = 0x03
GUITAR_HERO = 0x01
WIRELESS_DUALSHOCK = 0x0c

ENTER_CONFIG = bytearray((0x01, 0x43, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00))
SET_MODE = bytearray((0x01, 0x44, 0x00, 0x01, 0x03, 0x00, 0x00, 0x00, 0x00))
SET_BYTES_LARGE = bytearray((0x01, 0x4F, 0x00, 0xFF, 0xFF, 0x03, 0x00, 0x00, 0x00))
EXIT_CONFIG = bytearray((0x01, 0x43, 0x00, 0x00, 0x5A, 0x5A, 0x5A, 0x5A, 0x5A))
ENABLE_RUMBLE = bytearray((0x01, 0x4D, 0x00, 0x00, 0x01))
TYPE_READ = bytearray((0x01, 0x45, 0x00, 0x5A, 0x5A, 0x5A, 0x5A, 0x5A, 0x5A))

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

        self._buttons = 0xffff
        self._buttonsPrev = self._buttons
        self._lastReadTimeStamp = 0
        self._readDelay = 1
        self._controllerType = None
        self._pressure = False
        self._rumble = False
        self._rawData = 21 * [0]

        self._logger = logging.getLogger("PyS2x")
        self._logger.level = LOGGING_LEVEL

        self._cs = pyb.Pin('Y5', pyb.Pin.OUT_PP)
        self._cs.high()
        self._spi = pyb.SPI(2, pyb.SPI.MASTER, firstbit=pyb.SPI.LSB, baudrate=500000, polarity=1, phase=1, crc=None)

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

    def _shiftInOut(self, byte):
        """
        """
        ans = self._spi.send_recv(byte)
        pyb.udelay(CTRL_BYTE_DELAY)

        return int.from_bytes(ans)

    def _sendCmd(self, cmd):
        """
        """
        self._cs.low() # low enable joystick
        pyb.udelay(CTRL_BYTE_DELAY)

        for i in range(len(cmd)):
            self._shiftInOut(cmd[i])

        self._cs.high()  # high disable joystick
        pyb.delay(self._readDelay)

    def _reconfigure(self):
        """
        """
        self._logger.debug("_reconfigure(): send ENTER_CONFIG")
        self._sendCmd(ENTER_CONFIG)

        self._logger.debug("_reconfigure(): send SET_MODE")
        self._sendCmd(SET_MODE)

        if self._rumble:
            self._logger.debug("_reconfigure(): send ENABLE_RUMBLE")
            self._sendCmd(ENABLE_RUMBLE)

        if self._pressure:
            self._logger.debug("_reconfigure(): send SET_BYTES_LARGE")
            self._sendCmd(SET_BYTES_LARGE)

        self._logger.debug("_reconfigure(): send EXIT_CONFIG")
        self._sendCmd(EXIT_CONFIG)

    def read(self, motor1=False, motor2=0x00):
        """
        """
        delay = pyb.millis() - self._lastReadTimeStamp

        # Waited to long?
        if delay > MAX_DELAY:
            self._reconfigure()

        # Waited too short?
        if delay < self._readDelay:
            pyb.delay(self._readDelay - delay)

        #if motor2 != 0x00:
            #motor2 = int(0x40 + motor2 / 0xff * (0xff - 0x40))  # nothing below 0x40 will make it spin

        dword = bytearray((0x01, 0x42, 0x00, motor1, motor2, 0x00, 0x00, 0x00, 0x00))
        dword2 = bytearray((0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00))

        # Try a few times to get valid data...
        for retry in range(5):
            if retry:
                self._logger.warning("read(): retry=%d" % retry)

            self._cs.low()  # low enable joystick
            pyb.udelay(CTRL_BYTE_DELAY)

            # Send the command to send button and joystick data
            #self._logger.debug("read(): send button/joystick data...")
            for i, byte in enumerate(dword):
                self._rawData[i] = self._shiftInOut(byte)

            # If controller is in full data return mode, get the rest of data
            if self._rawData[1] == 0x79:
                #self._logger.debug("read()): controller is in full data return mode. Read rest of data...")
                for i, byte in enumerate(dword2):
                    self._rawData[i+9] = self._shiftInOut(byte)

            self._cs.high()  # high disable joystick
            pyb.udelay(CTRL_BYTE_DELAY)

            # Check to see if we received valid data or not.
            # We should be in analog mode for our data to be valid
            if self._rawData[1] & 0xf0 == 0x70:
                break

            # If we got to here, we are not in analog mode, try to recover...
            self._reconfigure()  # try to get back into analog mode
            pyb.delay(self._readDelay)

        # If we get here and still not in analog mode, try increasing _readDelay...
        if self._rawData[1] & 0xf0 != 0x70:
            if self._readDelay < 10:
                self._readDelay += 1  # see if this helps out...
                self._logger.warning("read()): increased _readDelay to %d" % self._readDelay)

        # Store the previous buttons states
        self._buttonsPrev = self._buttons

        # Store as one value for multiple functions
        self._buttons = (self._rawData[4] << 8) + self._rawData[3]

        self._lastReadTimeStamp = pyb.millis()

        #return (self._rawData[1] & 0xf0) == 0x70

    def configure(self, pressure=False, rumble=False):
        """
        """
        ans = []

        # Dummy read
        self.read()
        #self.read()

        # If still anything but 0x41, 0x73 or 0x79, then it's not talking
        if self._rawData[1] != 0x41 and self._rawData[1] != 0x73 and self._rawData[1] != 0x79:
            self._logger.critical("Controller mode not matched or no controller found")
            self._logger.critical("Expected 0x41 or 0x73, got %s" % hex(self._rawData[1]))
            self._logger.critical("Check wiring...")

            raise PyS2xError

        for retry in range(10):

            # Start config run
            self._logger.debug("configure(): send ENTER_CONFIG")
            self._sendCmd(ENTER_CONFIG)
            pyb.udelay(CTRL_BYTE_DELAY)

            # Read type
            self._cs.low()  # low enable joystick
            pyb.udelay(CTRL_BYTE_DELAY)

            self._logger.debug("configure(): send TYPE_READ and readback controller type")
            for byte in TYPE_READ:
                ans.append(self._shiftInOut(byte))
            self._logger.debug("configure()): ans=%s" % repr(ans))

            self._cs.high()  # high disable joystick
            pyb.udelay(CTRL_BYTE_DELAY)

            self._controllerType = ans[3]
            self._logger.debug("configure()): _controllerType=%d" % self._controllerType)

            self._logger.debug("configure(): send SET_MODE")
            self._sendCmd(SET_MODE)

            if rumble:
                self._logger.debug("configure(): send ENABLE_RUMBLE")
                self._sendCmd(ENABLE_RUMBLE)
                self._rumble = True

            if pressure:
                self._logger.debug("configure(): send SET_BYTES_LARGE")
                self._sendCmd(SET_BYTES_LARGE)
                self._pressure = True

            self._logger.debug("configure(): send EXIT_CONFIG")
            self._sendCmd(EXIT_CONFIG)

            self.read()

            if pressure :
                if self._rawData[1] == 0x79:
                    break

                elif self._rawData[1] == 0x73:
                    self._logger.warning("Controller refusing to enter 'pressure' mode; may not support it")
                    break

            if self._rawData[1] == 0x73:
                break

            if self._rawData[1] & 0xf0 != 0x70:
                if self._readDelay < 10:
                    self._readDelay += 1  # see if this helps out...
                    self._logger.warning("configure()): increased _readDelay to %d" % self._readDelay)
            #self._readDelay += 1  # add 1ms to self._readDelay

        else:
            self._logger.critical("Controller not accepting commands")
            self._logger.critical("Mode still set at %s" % hex(self._rawData[1]))

            raise PyS2xError


def main():
    logger = logging.getLogger("main()")
    logger.level = LOGGING_LEVEL

    pys2x = PyS2x()

    motor = False
    vibrate = 0

    # Add delay to give wireless ps2 module some time to startup, before configuring it
    pyb.delay(300)

    error = pys2x.configure(pressure=True, rumble=True)
    logger.info("Found Controller, configured successful (pressure=%s, rumble=%s)" % (pys2x.pressure, pys2x.rumble))
    logger.info("Try out all the buttons, X will vibrate the controller, faster as you press harder    ")
    logger.info("holding L1 or R1 will print out the analog stick values.")

    if pys2x.controllerType == DUALSHOCK:
        logger.info("DualShock Controller found")
    elif pys2x.controllerType == GUITAR_HERO:
        logger.info("GuitarHero Controller found")
    elif pys2x.controllerType == WIRELESS_DUALSHOCK:
        logger.info("Wireless Sony DualShock Controller found")
    else:
        logger.critical("Unknown Controller type found (0x%02x)" % pys2x.controllerType)
        raise SystemExit

    while True:
        # You must Read Gamepad to get new values and set vibration values
        # pys2x.read(small motor on/off, larger motor strenght from 0-255)
        # if you don't enable the rumble, use pys2x.read() with no values
        # You should call this at least once a second

        if pys2x.controllerType == GUITAR_HERO:
            pys2x.read()

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

            if pys2x.button(PSB_START):
                logger.info("Start is being held")
            if pys2x.button(PSB_SELECT):
                logger.info("Select is being held")

            if pys2x.button(ORANGE_FRET):
                logger.info("Wammy Bar Position: %d" % pys2x.analog(WHAMMY_BAR))

        else:
            pys2x.read(motor, vibrate)  # read controller and set large motor to spin at 'vibrate' speed
            #logger.info((len(pys2x._rawData) * "%02x ") % tuple(pys2x._rawData))

            if pys2x.button(PSB_START):
                logger.info("Start is being held")
            if pys2x.button(PSB_SELECT):
                logger.info("Select is being held")

            if pys2x.button(PSB_PAD_UP):
                logger.info("Up held this hard: %d" % pys2x.analog(PSAB_PAD_UP))

            if pys2x.button(PSB_PAD_RIGHT):
                logger.info("Right held this hard: %d" % pys2x.analog(PSAB_PAD_RIGHT))

            if pys2x.button(PSB_PAD_LEFT):
                logger.info("LEFT held this hard: %d" % pys2x.analog(PSAB_PAD_LEFT))

            if pys2x.button(PSB_PAD_DOWN):
                logger.info("DOWN held this hard: %d" % pys2x.analog(PSAB_PAD_DOWN))

            if pys2x.newButtonState():
                if pys2x.button(PSB_L3):
                    logger.info("L3 pressed")
                if pys2x.button(PSB_R3):
                    logger.info("R3 pressed")
                if pys2x.button(PSB_L2):
                    logger.info("L2 pressed")
                if pys2x.button(PSB_R2):
                    logger.info("R2 pressed")
                if pys2x.button(PSB_TRIANGLE):
                    logger.info("Triangle pressed")

            if pys2x.buttonPressed(PSB_CIRCLE):
                logger.info("Circle just pressed")
            if pys2x.newButtonState(PSB_CROSS):
                logger.info("X just changed")
            if pys2x.buttonReleased(PSB_SQUARE):
                logger.info("Square just released")

            # Set the large motor vibrate speed based on how hard blue (X) button is pressed
            vibrate = pys2x.analog(PSAB_CROSS)
            if pys2x.button(PSB_CROSS):
                logger.info("vibrate: %d" % vibrate)

            motor = bool(pys2x.button(PSB_CIRCLE))

            if pys2x.button(PSB_L1) or pys2x.button(PSB_R1):
                logger.info("Stick Values: %d, %d, %d, %d" % (pys2x.analog(PSS_LY), pys2x.analog(PSS_LX), pys2x.analog(PSS_RY), pys2x.analog(PSS_RX)))

        pyb.delay(50)


if __name__ == "__main__":
    main()
