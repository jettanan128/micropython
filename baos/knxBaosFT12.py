# -*- coding: utf-8 -*-

import pyb
import gc
import struct

import logging
import uasyncio.core as asyncio

from knxBaosExceptions import TimeoutError
from knxBaosFT12Frame import KnxBaosFT12Frame, KnxBaosFT12FixFrame, KnxBaosFT12VarFrame, FT12FrameError


class KnxBaosFT12:
    """
    """

    ACK = 0xe5  # acknowledge byte for FT1.2 protocol

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
        while pyb.elapsed_millis(startTime) < 10:
            if self._uart.any():
                ack = self._uart.readchar()
                self._logger.debug("_sendFrame(): received ack={}".format(hex(ack)))
                break
            else:
                pyb.delay(1)
        else:
            raise TimeoutError("timeout while reading ack")

    @asyncio.coroutine
    def _transmitterLoop(self):
        """ Poll message from tlsap and send telegram to uart
        """
        while True:
            try:
                message = self._tlsap.getOutMessage()  # @todo: switch to transmission
                if message is not None:
                    frame = KnxBaosFT12Frame.createMessageFrame(message)
                    self._sendFrame(frame.payload)  # Check timeout
                    # set transmission OK

                yield from asyncio.sleep(10)

            except Exception as e:
                #self._logger.debug("receiveLoop()")
                #self._logger.debug(str(e))
                raise

    @asyncio.coroutine
    def _receiverLoop(self):
        """ Poll uart for new telegram and send message to tlsap
        """
        while True:
            try:

                # If data available, read complete telegram
                if self._uart.any():
                    telegram = []
                    while self._uart.any():
                        c = self._uart.readchar()
                        telegram.append(c)
                        if telegram[-1] == KnxBaosFT12Frame.END_CHAR:
                            break
                        pyb.delay(1)
                        #@todo: use timeout_char?

                    # Send ACK
                    self._uart.writechar(KnxBaosFT12.ACK)

                    self._logger.debug("_receiverLoop(): telegram={}".format(repr(telegram)))

                    # Build frame from telegram and dispatch
                    try:
                        frame = KnxBaosFT12Frame.createFromTelegram(telegram)

                        if isinstance(frame, KnxBaosFT12FixFrame):
                            if frame.controlByte == KnxBaosFT12FixFrame.RESET_IND:
                                self._logger.info("received Reset.Ind")
                                KnxBaosFT12Frame.resetFcb()

                            elif frame.controlByte == KnxBaosFT12FixFrame.STATUS_RES:
                                self._logger.info("received Status.Res")

                            else:
                                self._logger.debug("_receiverLoop(): received {} control byte".format(hex(frame.controlByte)))

                        elif isinstance(frame, KnxBaosFT12VarFrame):
                            self._tlsap.putInMessage(frame.message)  # @todo: switch to transmission

                        else:
                            self._logger.critical("unknown frame class ({})".format(repr(frame)))

                    except FT12FrameError:
                        self._logger.error("_receiverLoop(): invalid frame")
                        raise

                yield from asyncio.sleep(10)

            except Exception as e:
                #self._logger.error("_receiverLoop()")
                #self._logger.error(e)
                raise

    def start(self, loop):
        """ Start internal loops
        """
        loop.create_task(self._transmitterLoop())
        loop.create_task(self._receiverLoop())

    def resetDevice(self):
        """ Reset KnxBaos device
        """
        frame = KnxBaosFT12Frame.createResetFrame()
        self._sendFrame(frame.payload)
        KnxBaosFT12Frame.resetFcb()
