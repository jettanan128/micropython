# -*- coding: utf-8 -*-

""" SmartButton management.

(C) 2015 Frédéric Mantegazza

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
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
"""

import pyb

# Misc delays, in ms
DEBOUNCE_DELAY = 25
CLICK_DELAY = 150
DOUBLE_CLICK_DELAY = 250
HOLD_DELAY = 800


class SmartButton(object):
    """ Smart button management class

    @ivar _pin: pin to use as button input
    @type _pin: pyb.Pin
    """
    def __init__(self, pin, pressLevel, callback):
        """ Init smart button object

        @param pin: a valid Pin
        @type pin: str or pyb.Pin

        @param pressLevel: level when button is pressed (0 or 1)
        @type pressLevel: int
        """
        super(SmartButton, self).__init__()

        self._pin = pin
        self._pressLevel = pressLevel
        self._callback = callback

        self._fsmState = 'idle'
        self._pressTime = pyb.millis()
        self._changeTime = pyb.millis()
        self._pinState = 0
        self._lastPinState = 0

        self._extInt = pyb.ExtInt(pin, pyb.ExtInt.IRQ_RISING_FALLING, pyb.Pin.PULL_UP, self._update)

    @property
    def _pinStateChanged(self):
        return self._lastPinState ^ self._pinState

    def _update(self, line):
        """
        """
        if pyb.elapsed_millis(self._changeTime) < DEBOUNCE_DELAY:
            self._changeTime = pyb.millis()
            return

        if self._pressLevel:
            self._pinState = bool(self._pin.value())
        else:
            self._pinState = not self._pin.value()

        trigger = dict(press=False, release=False, click=False, doubleClick=False, hold=False, doubleHold=False)

        if self._fsmState == 'idle':
            if self._pinStateChanged and self._pinState:
                trigger['press'] = True
                self._pressTime = pyb.millis()
                self._fsmState = 's1'

        elif self._fsmState == 's1':
            if pyb.elapsed_millis(self._pressTime) > HOLD_DELAY:
                trigger['hold'] = True
                self._fsmState = 's4'

            elif self._pinStateChanged and not self._pinState:
                trigger['release'] = True
                if pyb.elapsed_millis(self._pressTime) < CLICK_DELAY:
                    self._fsmState = 's2'
                else:
                    self._fsmState = 'idle'

        elif self._fsmState == 's2':
            if pyb.elapsed_millis(self._pressTime) > DOUBLE_CLICK_DELAY:
                trigger['click'] = True
                self._fsmState = 'idle'

            elif self._pinStateChanged and self._pinState:
                trigger['press'] = True
                if pyb.elapsed_millis(self._pressTime) < DOUBLE_CLICK_DELAY:
                    self._pressTime = pyb.millis()
                    self._fsmState = 's3'
                else:
                    self._pressTime = pyb.millis()
                    self._fsmState = 's1'

        elif self._fsmState == 's3':
            if pyb.elapsed_millis(self._pressTime) > HOLD_DELAY:
                trigger['doubleHold'] = True
                self._fsmState = 's4'

            elif self._pinStateChanged and not self._pinState:
                trigger['release'] = True
                if pyb.elapsed_millis(self._pressTime) < CLICK_DELAY:
                    trigger['doubleClick'] = True
                self._fsmState = 'idle'

        elif self._fsmState == 's4':
            if self._pinStateChanged and not self._pinState:
                trigger['release'] = True
                self._fsmState = 'idle'

        self._lastPinState = self._pinState

        if True in trigger.viewvalues():
            self._callback(trigger)


def main():
    def callback(trigger):
        for key, value in trigger.iteritems():
            if value:
                print(key)

    pin = pyb.Pin('X17')
    button = SmartButton(pin, 0, callback)
    while True:
        pyb.wfi()


if __name__ == "__main__":
    main()
