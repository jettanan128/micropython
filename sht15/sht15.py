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

import logging
import uasyncio.core as asyncio


# Clock pulse timing (us)
# Lengthening these may assist communication over long wires
PULSE_LONG  = 3
PULSE_SHORT = 1

# Status register bit definitions
SR_LOW_RES  =  0x01  # 12-bit Temp / 8-bit RH (vs. 14 / 12)
SR_NORELOAD =  0x02  # No reload of calibrarion data
SR_HEAT_ON  =  0x04  # Built-in heater on
SR_BATT_LOW =  0x40  # VDD < 2.47V

# SHT15 command definitions:
#                          adr  command r/w
CMD_MEAS_TEMP   = 0x03   # 000  0001    1
CMD_MEAS_HUMI   = 0x05   # 000  0010    1
CMD_STAT_REG_W  = 0x06   # 000  0011    0
CMD_STAT_REG_R  = 0x07   # 000  0011    1
CMD_SOFT_RESET  = 0x1e   # 000  1111    0

# Status register writable bits
SR_MASK = 0x07

# Temperature & humidity equation constants
D1  = -40.1          # for deg C @ 5V
D2h =   0.01         # for deg C, 14-bit precision
D2l =   0.04         # for deg C, 12-bit precision

C1  = -2.0468        # for V4 sensors
C2h =  0.0367        # for V4 sensors, 12-bit precision
C3h = -1.5955E-6     # for V4 sensors, 12-bit precision
C2l =  0.5872        # for V4 sensors, 8-bit precision
C3l = -4.0845E-4     # for V4 sensors, 8-bit precision

T1  =  0.01          # for V3 and V4 sensors
T2h =  0.00008       # for V3 and V4 sensors, 12-bit precision
T2l =  0.00128       # for V3 and V4 sensors, 8-bit precision



class SHT15Exception(Exception):
    """
    """


class WrongParam(SHT15Exception):
    """
    """


class NoAcknowledge(SHT15Exception):
    """
    """


class Timeout(SHT15Exception):
    """
    """


class InvalidMeasure(SHT15Exception):
    """
    """


class SHT15:
    """ SHT15 Sensirion management class
    """
    def __init__(self, dataPin, clockPin):
        """ Init object

        @param dataPin: pin for data line
        @type dataPin: str or pyb.Pin.cpu.Name or pyb.Pin.board.Name

        @param clockPin: pin for clock line
        @type clockPin: str or pyb.Pin.cpu.Name or pyb.Pin.board.Name

        All functions exit with clockPin low and dataPin in input mode
        """
        self._pinData = pyb.Pin(dataPin, pyb.Pin.OUT_PP)
        self._pinClock = pyb.Pin(clockPin, pyb.Pin.OUT_PP)

        self._rawDataTemp = None
        self._rawDataHumi = None
        self._measureInitiatedAt = 0
        self._measureReady = False

        # Sensor status register default state
        self._statusRegister = 0x00

        self._initSensor()

    @property
    def temperature(self):
        """
        """
        if self._rawDataTemp is None:
            raise InvalidMeasure

        if self._statusRegister & SR_LOW_RES:
            return D1 + D2l * self._rawDataTemp
        else:
            return D1 + D2h * self._rawDataTemp

    @property
    def humidity(self):
        """
        """
        if self._rawDataTemp is None:
            raise InvalidMeasure

        if self._statusRegister & SR_LOW_RES:
            humidity = C1 + C2l * self._rawDataHumi + C3l * self._rawDataHumi ** 2
            humidity += (self.temperature - 25.0) * (T1 + T2l * self._rawDataHumi)
        else:
            humidity = C1 + C2h * self._rawDataHumi + C3h * self._rawDataHumi ** 2
            humidity += (self.temperature - 25.0) * (T1 + T2h * self._rawDataHumi)

        if humidity > 100.0:
            humidity = 100.0
        elif humidity < 0.1:
            humidity = 0.1

        return humidity

    @property
    def dewPoint(self):
        """
        """
        k = math.log(self.humidity / 100) + (17.62 * self.temperature) / (243.12 + self.temperature)

        return 243.12 * k / (17.62 - k)


    def _initSensor(self):
        """ Put sensor to default state
        """
        # Sensor status register default state
        self._statusRegister = 0x00

        # Reset communication link with sensor
        self._resetConnection()

        # Send soft reset command
        self._putByte(CMD_SOFT_RESET)

    def _resetConnection(self):
        """Communication link reset

        # At least 9 SCK cycles with DATA=1, followed by transmission start sequence
        #      ______________________________________________________         ________
        # DATA:                                                      |_______|
        #          _    _    _    _    _    _    _    _    _        ___     ___
        # SCK : __| |__| |__| |__| |__| |__| |__| |__| |__| |______|   |___|   |______
        """

        # Set data register high before turning on
        self._pinData.high()

        # output driver (avoid possible low pulse)
        self._pinData.init(pyb.Pin.OUT_PP)
        pyb.udelay(PULSE_LONG)

        # 9 clock cycles
        for i in range(0, 9):
            self._pinClock.high()
            pyb.udelay(PULSE_LONG)
            self._pinClock.low()
            pyb.udelay(PULSE_LONG)

        self._startTransmission()

    def _startTransmission(self):
        """Generate SHT15-specific transmission start sequence

        # This is where SHT15 does not conform to the I2C standard and is
        # the main reason why the AVR TWI hardware support can not be used.
        #       _____         ________
        # DATA:      |_______|
        #           ___     ___
        # SCK : ___|   |___|   |______
        """

        # Set data register high before turning on
        self._pinData.high()

        # output driver (avoid possible low pulse)
        self._pinData.init(pyb.Pin.OUT_PP)
        pyb.udelay(PULSE_SHORT)
        self._pinClock.high()
        pyb.udelay(PULSE_SHORT)
        self._pinData.low()
        pyb.udelay(PULSE_SHORT)
        self._pinClock.low()
        pyb.udelay(PULSE_LONG)
        self._pinClock.high()
        pyb.udelay(PULSE_SHORT)
        self._pinData.high()
        pyb.udelay(PULSE_SHORT)
        self._pinClock.low()
        pyb.udelay(PULSE_SHORT)

        self._pinData.init(pyb.Pin.IN, pull=pyb.Pin.PULL_UP)

    def _putByte(self, value):
        """ Write byte to sensor and check for acknowledge

        @raise: NoAcknowledge
        """

        # Set data line to output mode
        self._pinData.init(pyb.Pin.OUT_PP)

        # Bit mask to transmit MSB first
        mask = 0x80
        for i in range(8, 0, -1):
            self._pinData.value(value & mask)
            pyb.udelay(PULSE_SHORT)

            # Generate clock pulse
            self._pinClock.high()
            pyb.udelay(PULSE_LONG)
            self._pinClock.low()
            pyb.udelay(PULSE_SHORT)

            # Shift mask for next data bit
            mask >>= 1

        # Return data line to input mode
        self._pinData.init(pyb.Pin.IN, pull=pyb.Pin.PULL_UP)

        # Clock #9 for ACK
        self._pinClock.high()
        pyb.udelay(PULSE_LONG)

        # Verify ACK ('0') received from sensor
        if self._pinData.value():
            raise NoAcknowledge("SHT15 didn't acknowledge data")

        # Finish with clock in low state
        pyb.udelay(PULSE_SHORT)
        self._pinClock.low()

    def _getByte(self, ack):
        """  Read byte from sensor

        @param ack: send acknowledge if True
        @type ack: bool

        @raise:
        """
        result = 0

        for i in range(8, 0, -1):

            # Shift received bits towards MSB
            result <<= 1

            # Generate clock pulse
            self._pinClock.high()
            pyb.udelay(PULSE_SHORT)

            # Merge next bit into LSB position
            result |= self._pinData.value()

            self._pinClock.low()
            pyb.udelay(PULSE_SHORT)

        self._pinData.init(pyb.Pin.OUT_PP)

        # Assert ACK ('0') if ack == 1
        self._pinData.value(ack ^ 1)
        pyb.udelay(PULSE_SHORT)

        # Clock #9 for ACK / NO_ACK
        self._pinClock.high()
        pyb.udelay(PULSE_LONG)

        # Finish with clock in low state
        self._pinClock.low()
        pyb.udelay(PULSE_SHORT)

        # Return data line to input mode
        self._pinData.init(pyb.Pin.IN, pull=pyb.Pin.PULL_UP)

        return result

    def _readSR(self):
        """ Read status register
        """
        self.startTransmission()
        try:
            self._putByte(CMD_STAT_REG_R)
        except SHT15Exception:
            return 0xff

        return self._getByte(ack=False)

    def _writeSR(self, value):
        """ Write status register
        """

        # Mask off unwritable bits
        value &= SR_MASK

        # Save local copy
        self._statusRegister = value

        self.startTransmission()
        self._putByte(CMD_STAT_REG_W)
        self._putByte(value)

    def _readData(self):
        """ Get measurement result from sensor
        """
        data = self._getByte(ack=True)
        data = (data << 8) | self._getByte(ack=False)

        return data

    def _initiateMeasure(self, cmd):
        """ Initiate measure
        """
        if cmd == "temp":
            cmd = CMD_MEAS_TEMP
        elif cmd == '_rawDataHumi':
            cmd = CMD_MEAS_HUMI
        else:
            WrongParam("measure cmd (%s) must be in ('temp', _rawDataHumi')" % cmd)

        self._measureReady = False
        self._measureInitiatedAt = pyb.millis()

        self._startTransmission()
        self._putByte(cmd)

    def _measureReady(self):
        """ Check if non-blocking measurement has completed
        """

        # Already done?
        if self._measureReady:
            return True

        # Measure ready yet?
        if self._pinData.value():
            return False

        self._measureReady = True

        return True

    def _waitForMeasureReady(self, timeout=720):
        """ wait for non blocking measure to complete

        raise: TimeoutError
        """
        while True:
            if self._measureReady():
                return
            if pyb.elapsed_millis(self._measureInitiatedAt) >= timeout:
                raise Timeout("timeout while waiting for measure")

            yield from asyncio.sleep(10)

    @asyncio.coroutine
    def loop(self, refresh=5000):
        """ Measurement loop

        This method continuously does measures at 'refresh' rate.
        It is built as a state machine and uses asyncio module.

        @param refresh: refresh measure rate, in ms
        @type refresh: int
        """
        logger = logging.getLogger('sht15')
        state = 'idle'
        lastReading = 0

        while True:
            if state == 'idle':
                if pyb.elapsed_millis(lastReading) >= refresh:
                    logger.debug("%d:start new measure", pyb.millis())
                    lastReading = pyb.millis()
                    state = 'read temp'

            elif state == 'read temp':
                logger.debug("%d:read raw temp", pyb.millis())
                self._initiateMeasure('temp')
                state = 'wait temp'

            elif state == 'wait temp':
                if self.measureReady():
                    logger.debug("%d:temp data ready", pyb.millis())
                    self._rawDataTemp = self._readData()
                    state = 'read humi'

            elif state == 'read humi':
                logger.debug("%d:read raw humi", pyb.millis())
                self._initiateMeasure('humi')
                state = 'wait humi'

            elif state == 'wait humi':
                if self.measureReady():
                    logger.debug("%d:humi data ready", pyb.millis())
                    self._rawDataHumi = self._readData()
                    logger.debug("%d:measure done in %sms", pyb.millis(), pyb.elapsed_millis(lastReading))
                    state = 'idle'

            yield from asyncio.sleep(10)

    def measure(self):
        """ All-in-one (blocking)

        @return: temperature, humidity, dewpoint
        @rtype: tuple of 3 float
        """
        self._initiateMeasure('temp')
        self._waitForMeasureReady()
        self._rawDataTemp = self._readData()

        self._rawDataHumi = self._initiateMeasure('_rawDataHumi')
        self._waitForMeasureReady()
        self._rawDataHumi = self._readData()

        return self.temperature, self.humidity, self.dewPoint

    def reset(self):
        """ Reset function

        Soft reset returns sensor status register to default values
        """
        self._initSensor()
        
        
        def main():
            sht15 = SHT15WithCrc('Y11', 'Y12')
            print(sht15.measure())
            
        
        if __name__ == "__main__":
            main()


def main():
    sht15 = SHT15('Y11', 'Y12')
    print(sht15.measure())
    

if __name__ == "__main__":
    main()
