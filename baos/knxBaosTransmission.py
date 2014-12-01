# -*- coding: utf-8 -*-

from knxBaosExceptions import TransmissionError


class KnxBaosTransmission:
    """ Transmission class

    @ivar _payload: real stuf to transmit
    @type _payload: any

    @ivar _waitConfirm:
    @type _waitConfirm: bool

    @ivar _result:
    @type _result: int
    """
    OK = 0         # Message was successfully transmitted
    ERROR = 1      # Layer 2: unspecified error
                   # (Due to standard EIB-BCU's return no specific error codes, i.e.
                   #  stands for LINE_BUSY, NO_ACK, NACK or DEST_BUSY respectively.)
    LINE_BUSY = 2  # Layer 2: message timed out cause transmission line was busy
    NO_ACK = 3     # Layer 2: message was transmitted, but no acknowledge was received
    NACK = 4       # Layer 2: message was transmitted, but L2-NACK received
    DEST_BUSY = 5  # Layer 2: message was transmitted, but destination sent BUSY

    AVAILABLE_CODES = (OK,
                       ERROR,
                       LINE_BUSY,
                       NO_ACK,
                       NACK,
                       DEST_BUSY
                      )

    def __init__(self, payload, waitConfirm=True):
        """

        @param payload: real stuf to transmit
        @type payload: any

        @param waitConfirm:
        @type waitConfirm: bool

        raise TransmissionError:
        """
        self._payload = payload
        self._waitConfirm = waitConfirm
        self._result = KnxBaosTransmission.OK

    def __repr__(self):
        return "<Transmission(payload={}, waitConfirm={}, result={})>".format(repr(self._payload), self._waitConfirm, self._result)

    @property
    def payload(self):
        return self._payload

    @property
    def waitConfirm(self):
        return self._waitConfirm

    @waitConfirm.setter
    def waitConfirm(self, flag):
        self._waitConfirm = flag

    @property
    def result(self):
        return self._result

    @result.setter
    def result(self, code):
        if code not in KnxBaosTransmission.AVAILABLE_CODES:
            raise TransmissionError("invalid result code (%s)" % repr(code))

        self._result = code
