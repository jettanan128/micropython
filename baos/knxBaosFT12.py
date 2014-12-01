# -*- coding: utf-8 -*-

import pyb
import gc
import struct

import logging
import uasyncio.core as asyncio

from knxBaosExceptions import TimeoutError
from knxBaosFT12Frame import KnxBaosFT12Frame, KnxBaosFT12FixFrame, KnxBaosFT12VarFrame, FT12FrameError
from knxBaosTransmission import KnxBaosTransmission


class KnxBaosFT12:
    """
    """

    ACK = 0xe5  # acknowledge byte for FT1.2 protocol
    ACK_TIMEOUT = 30  # in ms

    def __init__(self, tlsap, uartNum=2):
        """
        """
        self._tlsap = tlsap  # find a better name

        self._logger = logging.getLogger("KnxBaosFT12")

        self._uart = pyb.UART(uartNum)
        self._uart.init(19200, bits=8, parity=0, stop=1)

    def _sendFrame(self, frame):
        """

        Manage retry -> no, at upper level, through transmission.result, waitConfirm and so. See pKNyX
        """
        self._logger.debug("_sendFrame(): frame={}".format(repr(frame)))
        for c in frame:
            self._uart.writechar(c)

        # Wait for ack
        startTime = pyb.millis()
        while pyb.elapsed_millis(startTime) < KnxBaosFT12.ACK_TIMEOUT:  # TODO: adjust timeout
            if self._uart.any():
                ack = self._uart.readchar()
                self._logger.debug("_sendFrame(): received ack={}".format(hex(ack)))
                if ack != KnxBaosFT12.ACK:
                    self._logger.error("_sendFrame(): wrong ack char ({})".format(hex(ack)))
                break
            else:
                pyb.delay(1)
        else:
            raise TimeoutError("timeout occured while reading ack")

    @asyncio.coroutine
    def _transmitterLoop(self):
        """ Poll message from tlsap and send telegram to uart

        @todo: limit transmission frequency
        """
        while True:
            try:
                transmission = self._tlsap.getOutMessage()

                if transmission is not None:
                    self._logger.debug("_transmitterLoop(): transmission={}".format(transmission))
                    message = transmission.payload
                    frame = KnxBaosFT12Frame.createMessageFrame(message)

                    try:
                        self._sendFrame(frame.payload)
                        transmission.result = KnxBaosTransmission.OK
                    except TimeoutError as e:
                        self._logger.error("_transmitterLoop(): {}".format(str(e)))
                        transmission.result = KnxBaosTransmission.NO_ACK
                    except Exception as e:
                        self._logger.critical("_transmitterLoop(): {}".format(str(e)))
                        transmission.result = KnxBaosTransmission.ERROR

                    if transmission.waitConfirm:
                        transmission.waitConfirm = False

                yield from asyncio.sleep(10)

            except Exception as e:
                self._logger.critical("_transmitterLoop(): {}".format(str(e)))

    @asyncio.coroutine
    def _receiverLoop(self):
        """ Poll uart for new telegram and send message to tlsap
        """
        while True:
            try:

                # If data available, read complete telegram
                if self._uart.any():
                    telegram = []
                    while not telegram or telegram[-1] != KnxBaosFT12Frame.END_CHAR:
                        c = self._uart.readchar()
                        if c == -1:
                            break
                        telegram.append(c)
                        #pyb.delay(5)
                        #@todo: adjust timeout and timeout_char

                    # Send ACK
                    self._uart.writechar(KnxBaosFT12.ACK)

                    self._logger.debug("_receiverLoop(): telegram={}".format(repr(telegram)))

                    # Build frame from telegram and dispatch
                    try:
                        frame = KnxBaosFT12Frame.createFromTelegram(telegram)

                        if isinstance(frame, KnxBaosFT12FixFrame):
                            if frame.controlByte == KnxBaosFT12FixFrame.RESET_IND:
                                self._logger.info("_receiverLoop(): received Reset.Ind")
                                KnxBaosFT12Frame.resetFcb()
                                # @todo: find a way to inform application
                                self._tlsap._handler._onResetInd()  # hugly!

                            elif frame.controlByte == KnxBaosFT12FixFrame.STATUS_RES:
                                self._logger.info("_receiverLoop(): received Status.Res")

                            else:
                                self._logger.debug("_receiverLoop(): received {} control byte".format(hex(frame.controlByte)))

                        elif isinstance(frame, KnxBaosFT12VarFrame):
                            self._tlsap.putInMessage(frame.message)

                        else:
                            self._logger.error("_receiverLoop(): unknown frame class ({})".format(repr(frame)))

                    except FT12FrameError:
                        self._logger.error("_receiverLoop(): invalid frame")

                yield from asyncio.sleep(10)

            except Exception as e:
                self._logger.critical("receiveLoop(): {}".format(str(e)))

    def start(self, loop):
        """ Start internal loops
        """
        loop.create_task(self._transmitterLoop())
        loop.create_task(self._receiverLoop())

    def resetDevice(self):
        """ Reset KnxBaos device
        """
        frame = KnxBaosFT12Frame.createResetFrame()
        try:
            self._sendFrame(frame.payload)
            KnxBaosFT12Frame.resetFcb()
        except TimeoutError as e:
            self._logger.error("resetDevice(): {}".format(str(e)))
