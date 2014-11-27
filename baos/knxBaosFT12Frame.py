# -*- coding: utf-8 -*-

from knxBaosExceptions import FT12FrameError


class KnxBaosFT12Frame:
    """ FT1.2 frame object

    @ivar _payload: raw frame
    @param _payload: list or tuple

    raise FT12FrameError:
    """

    HEADER_SIZE = 0x04

    # Service code for KNX EMI2
    # Reset used for fixed frame telegrams transmitted in packets of length 1
    EMI2_L_RESET_IND = 0xa0

    # Standard KNX frame, inclusive bus monitor mode!
    MIN_FRAME_LENGTH = 4  # 1!!! for ACK...
    MAX_FRAME_LENGTH = 128

    START_FIX_FRAME = 0x10  # start byte for frames with fixed length
    START_VAR_FRAME = 0x68  # start byte for frames with variable length
    CONTROL_SEND = 0x53  # control field for sending udata to module
    CONTROL_RCV_MASK = 0xdf  # mask to check control field for receiving
    CONTROL_RCV = 0xd3  # control field for receiving udata to module
    END_CHAR = 0x16  # the end character for FT1.2 protocol
    FCB_MASK = 0x20  # mask to get fcb byte in control field

    _lastSendFcb = 0x00
    _lastRecvFcb = 0x00

    def __init__(self, payload=None):
        """ Creates a new FT1.2 frame

        Create a KnxBaosFT12Frame from FT1.2 raw frame

        @param payload: FT1.2 raw frame
        @type payload: list or tuple

        @raise KnxNetIPHeaderError:
        """

        self._payload = payload

        if payload is not None:
            self._checkValidity()

    def __str__(self):
        return "<KnxBaosFT12Frame({})>".format(self._payload)

    @staticmethod
    def createFromTelegram(telegram):
        """ Create frame from telegram

        Depending of first char, it build a fxed length frame, or a variable length frame.
        """
        if telegram[0] == KnxBaosFT12Frame.START_FIX_FRAME:
            frame = KnxBaosFT12FixFrame(telegram)
        elif telegram[0] == KnxBaosFT12Frame.START_VAR_FRAME:
            frame = KnxBaosFT12VarFrame(telegram)
        else:
            raise FT12FrameError("invalid start char ({})".format(hex(telegram[0])))

        return frame

    @staticmethod
    def createMessageFrame(message):
        """ Create a standard message frame

        This frame is variable length.
        This static method build the complete raw frame from given message.

        @param message: message to encapsulate
        @type message: list or tuple
        """
        frame = KnxBaosFT12VarFrame()

        header = (KnxBaosFT12Frame.START_VAR_FRAME, len(message)+1, len(message)+1, KnxBaosFT12Frame.START_VAR_FRAME)
        controlField = KnxBaosFT12Frame.CONTROL_SEND | KnxBaosFT12VarFrame._nextSendFcb
        checksum = KnxBaosFT12VarFrame.computeChecksum(controlField, message)

        frame._payload = header + (controlField,) + message + (checksum, KnxBaosFT12Frame.END_CHAR)

        return frame

    @staticmethod
    def createResetFrame():
        """ Create a reset frame

        This frame is fixed length.
        """
        frame = KnxBaosFT12FixFrame()
        frame._payload = (KnxBaosFT12Frame.START_FIX_FRAME, KnxBaosFT12FixFrame.RESET_REQ, KnxBaosFT12FixFrame.RESET_REQ, KnxBaosFT12Frame.END_CHAR)

        return frame

    @staticmethod
    def resetFcb():
        """ Reset FCB
        """
        KnxBaosFT12Frame._nextSendFcb = 0x00
        KnxBaosFT12Frame._nextRecvFcb = 0x00

    @property
    def _nextSendFcb(self):
        nextSendFcb = KnxBaosFT12Frame._lastSendFcb
        KnxBaosFT12Frame._lastSendFcb ^= KnxBaosFT12Frame.FCB_MASK
        return nextSendFcb

    @property
    def _nextRecvFcb(self):
        nextRecvFcb = KnxBaosFT12Frame._lastRecvFcb
        KnxBaosFT12Frame._lastRecvFcb ^= KnxBaosFT12Frame.FCB_MASK
        return nextRecvFcb

    @property
    def payload(self):
        return self._payload

    @property
    def header(self):
        return self._payload[:4]

    def _checkValidity(self):
        """ Check if frame is valid
        """

        # Check frame length
        if not KnxBaosFT12Frame.MIN_FRAME_LENGTH <= len(self._payload) <= KnxBaosFT12Frame.MAX_FRAME_LENGTH:
            raise FT12FrameError("invalid frame length ({}, should be 4)".format(len(self.header)))

        # Check end field
        if self._payload[-1] != KnxBaosFT12Frame.END_CHAR:
            raise FT12FrameError("invalid end char ({})".format(self._payload[-1]))

        # Check header second/third char (should be the same)
        if self.header[1] != self.header[2]:
            raise FT12FrameError("invalid header ({}, should be 4)".format(self.header))


class KnxBaosFT12FixFrame(KnxBaosFT12Frame):
    """ FT1.2 fixed length frame object
    """
    # Control bytes for fixed length telegrams
    RESET_REQ = 0x40  # send a reset request to BAU
    RESET_IND = 0xc0  # reset indication
    STATUS_REQ = 0x49  # status request
    STATUS_RES = 0x8b  # respond status
    CONFIRM_ACK = 0x80  # confirm acknowledge
    CONFIRM_NACK = 0x81  # confirm not acknowledge

    @property
    def controlByte(self):
        """ Return control byte
        """
        return self.header[1]

    def _checkValidity(self):
        """ Check if frame is valid
        """
        super(KnxBaosFT12FixFrame, self)._checkValidity()

        if self.header[0] == KnxBaosFT12Frame.START_FIX_FRAME:
            if self.controlByte not in (KnxBaosFT12FixFrame.RESET_REQ,
                                        KnxBaosFT12FixFrame.RESET_IND,
                                        KnxBaosFT12FixFrame.STATUS_REQ,
                                        KnxBaosFT12FixFrame.STATUS_RES,
                                        KnxBaosFT12FixFrame.CONFIRM_ACK,
                                        KnxBaosFT12FixFrame.CONFIRM_NACK):
                raise FT12FrameError("invalid fixed frame control byte ({})".format(hex(self.controlByte)))

        else:
            raise FT12FrameError("invalid frame type ({})".format(hex(self.header[0])))

class KnxBaosFT12VarFrame(KnxBaosFT12Frame):
    """ FT1.2 variable length frame object
    """

    @staticmethod
    def computeChecksum(controlField, message):
        checksum = controlField
        for c in message:
            checksum += c
        checksum %= 0x100

        return checksum

    @property
    def controlField(self):
        try:
            return self._payload[4]
        except IndexError:
            raise FT12FrameError("frame too short")

    @property
    def checksum(self):
        return self._payload[-2]

    @property
    def checksumComputed(self):
        checksum = self.controlField
        for c in self.message:
            checksum += c
        checksum %= 0x100

        return checksum

    @property
    def message(self):
        return self._payload[5:-2]

    def _checkValidity(self):
        """ Check if frame is valid
        """
        super(KnxBaosFT12FixFrame, self)._checkValidity()

        if self.header[0] == KnxBaosFT12Frame.START_VAR_FRAME:

            # Check header
            if self.header[-1] != KnxBaosFT12Frame.START_VAR_FRAME or \
               self.header[1] != self.header[2]:
                raise FT12FrameError("invalid variable frame header ({})".format(self.header))

            # Check message length
            if len(self.message) != self.header[1] - 1:
                raise FT12FrameError("invalid message length ({}, should be {})".format(len(self.message), self.header[1]-1))

            # Check controlField
            # TODO

            # Check checksum
            if self.checksumComputed != self.checksum:
                raise FT12FrameError("invalid checksum ({}, should be {})".format(hex(self.checksumComputed), hex(self.checksum)))

        else:
            raise FT12FrameError("invalid frame type ({})".format(hex(self.header[0])))
