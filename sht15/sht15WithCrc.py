# -*- coding: utf-8 -*-

""" Sensirion SHT1x & SHT7x family temperature and humidity sensors

Created by Markus Schatzl, November 28, 2008
Released into the public domain

Revised (v1.1) by Carl Jackson, August 4, 2010
Rewritten (v2.0) by Carl Jackson, December 10, 2010
Ported to micropython by Frederic Mantegazza, november, 2014
"""

import math
import pyb
import gc

from sht15 import SHT15, SHT15Exception, SR_MASK, CMD_STAT_REG_R, CMD_MEAS_TEMP, CMD_MEAS_HUMI

# Crc polynomial: x**8 + x**5 + x**4 + 1
POLY = 0x31


class CrcError(SHT15Exception):
    """
    """


class SHT15WithCrc(SHT15):
    """
    """
    def __init__(self, dataPin, clockPin):
        """
        """
        self._crc = 0

        #self._statusRegister = 0x00  # sensor status register default state

        super(SHT15WithCrc, self).__init__(dataPin, clockPin)

    def _updateCrc(self, value):
        """   
        """

        self._crc ^= value
        for i in range(8, 0, -1):
            if self._crc & 0x80:
                self._crc = (self._crc << 1) ^ POLY
            else:
                self._crc = self._crc << 1

    def _bitReverse(self, value):
        """ Bit-reverse a byte (for CRC calculations)
        """
        result = 0

        for i in range(8, 0, -1):
            result = (result << 1) | (value & 0x01)
            value >>= 1

        return result

    def _readSR(self):
        """ Read status register
        """

        # Initialize CRC calculation
        self._crc = self._bitReverse(self._statusRegister & SR_MASK)

        self.startTransmission()
        try:
            self._putByte(CMD_STAT_REG_R)
        except SHT15Exception:
            return 0xff

        # Include command byte in CRC calculation
        self._updateCrc(CMD_STAT_REG_R)
        result = self.getByte(acq=True)
        self._updateCrc(result)
        val = self._getByte(acq=False)
        val = self._bitReverse(val)
        if val != self._crc:
            raise CrcError

        return self._getByte(ack=False)

    def _readData(self):
        """ Get measurement data from sensor (including CRC)
        """

        # CRC computation
        val = self._getByte(acq=True)
        self._updateCrc(val)
        data = val
        val = self._getByte(acq=True)
        self._updateCrc(val)
        data = (data << 8) | val
        val = self._getByte(acq=False)
        val = self._bitReverse(val)
        if val != self._crc :
            raise CrcError("wrong CRC when reading data")

        data = self._getByte(ack=True)
        data = (data << 8) | self._getByte(ack=False)

        return data

    def _initiateMeasure(self, cmd):
        """ Initiate measure
        """
        if cmd == "temp":
            cmd = CMD_MEAS_TEMP
        elif cmd == 'hum':
            cmd = CMD_MEAS_HUMI
        else:
            WrongParam("measure cmd (%s) must be in ('temp', hum')" % cmd)

        self._measureReady = False
        self._measureInitiatedAt = pyb.millis()


        # Initialize CRC calculation
        self._crc = self._bitReverse(self._statusRegister & SR_MASK)

        # Include command byte in CRC calculation
        self._updateCrc(cmd)

        self._startTransmission()
        self._putByte(cmd)


def main():
    sht15 = SHT15WithCrc('Y11', 'Y12')
    print(sht15.measure())
    

if __name__ == "__main__":
    main()
