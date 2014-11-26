

class KNXnetIPHeaderValueError(PKNyXValueError):
    """
    """


class KnxBaosFT12Header(object):
    """ FT1.2 header object

    @ivar _serviceType: Service type identifier
    @type _serviceType: int

    @ivar _totalSize: total size of the KNXNet/IP telegram
    @type _totalSize: int

    raise KNXnetIPHeaderValueError:
    """

    # Services identifier values
    CONNECT_REQ = 0x0205
    CONNECT_RES = 0x0206
    CONNECTIONSTATE_REQ = 0x0207
    CONNECTIONSTATE_RES = 0x0208
    DISCONNECT_REQ = 0x0209
    DISCONNECT_RES = 0x020A
    DESCRIPTION_REQ = 0x0203
    DESCRIPTION_RES = 0x204
    SEARCH_REQ = 0x201
    SEARCH_RES = 0x202
    DEVICE_CONFIGURATION_REQ = 0x0310
    DEVICE_CONFIGURATION_ACK = 0x0311
    TUNNELING_REQ = 0x0420
    TUNNELING_ACK = 0x0421
    ROUTING_IND = 0x0530
    ROUTING_LOST_MSG = 0x0531

    SERVICE = (CONNECT_REQ, CONNECT_RES,
               CONNECTIONSTATE_REQ, CONNECTIONSTATE_RES,
               DISCONNECT_REQ, DISCONNECT_RES,
               DESCRIPTION_REQ, DESCRIPTION_RES,
               SEARCH_REQ, SEARCH_RES,
               DEVICE_CONFIGURATION_REQ, DEVICE_CONFIGURATION_ACK,
               TUNNELING_REQ, TUNNELING_ACK,
               ROUTING_IND, ROUTING_LOST_MSG
              )

    HEADER_SIZE = 0x06
    KNXNETIP_VERSION = 0x10

    def __init__(self, frame=None, service=None, serviceLength=0):
        """ Creates a new KNXnet/IP header

        Header can be loaded either from frame or from sratch

        @param frame: byte array with contained KNXnet/IP frame
        @type frame: sequence

        @param service: service identifier
        @type service: int

        @param serviceLength: length of the service structure
        @type serviceLength: int

        @raise KnxNetIPHeaderValueError:
        """

        # Check params
        if frame is not None and service is not None:
            raise KNXnetIPHeaderValueError("can't give both frame and service type")

        if frame is not None:
            frame = bytearray(frame)
            if len(frame) < KnxBaosFT12Header.HEADER_SIZE:
                    raise KNXnetIPHeaderValueError("frame too short for KNXnet/IP header (%d)" % len(frame))

            headersize = frame[0] & 0xff
            if headersize != KnxBaosFT12Header.HEADER_SIZE:
                raise KNXnetIPHeaderValueError("wrong header size (%d)" % headersize)

            protocolVersion = frame[1] & 0xff
            if protocolVersion != KnxBaosFT12Header.KNXNETIP_VERSION:
                raise KNXnetIPHeaderValueError("unsupported KNXnet/IP protocol (%d)" % protocolVersion)

            self._service = (frame[2] & 0xff) << 8 | (frame[3] & 0xff)
            if self._service not in KnxBaosFT12Header.SERVICE:
                raise KNXnetIPHeaderValueError("unsupported service (%d)" % self._service)

            self._totalSize = (frame[4] & 0xff) << 8 | (frame[5] & 0xff)
            if len(frame) != self._totalSize:
                raise KNXnetIPHeaderValueError("wrong frame length (%d; should be %d)" % (len(frame), self._totalSize))

        elif service is not None:
            if service not in KnxBaosFT12Header.SERVICE:
                raise KNXnetIPHeaderValueError("unsupported service (%d)" % self._service)
            if not serviceLength:
                raise KNXnetIPHeaderValueError("service length missing")
            self._service = service
            self._totalSize = KnxBaosFT12Header.HEADER_SIZE + serviceLength

        else:
            raise KNXnetIPHeaderValueError("must give either frame or service type")

    def __repr__(self):
        s = "<KnxBaosFT12Header(service='%s', totalSize=%d)>" % (self.serviceName, self._totalSize)
        return s

    def __str__(self):
        s = "<KnxBaosFT12Header('%s')>" % self.serviceName
        return s

    @property
    def service(self):
        return self._service

    @property
    def totalSize(self):
        return self._totalSize

    @property
    def frame(self):
        s = struct.pack(">2B2H", KnxBaosFT12Header.HEADER_SIZE, KnxBaosFT12Header.KNXNETIP_VERSION, self._service, self._totalSize)
        return bytearray(s)

    @property
    def serviceName(self):
        if self._service == KnxBaosFT12Header.CONNECT_REQ:
            return "connect.req"
        elif self._service == KnxBaosFT12Header.CONNECT_RES:
            return "connect.res"
        elif self._service == KnxBaosFT12Header.CONNECTIONSTATE_REQ:
            return "connectionstate.req"
        elif self._service == KnxBaosFT12Header.CONNECTIONSTATE_RES:
            return "connectionstate.res"
        elif self._service == KnxBaosFT12Header.DISCONNECT_REQ:
            return "disconnect.req"
        elif self._service == KnxBaosFT12Header.DISCONNECT_RES:
            return "disconnect.res"
        elif self._service == KnxBaosFT12Header.DESCRIPTION_REQ:
            return "description.req"
        elif self._service == KnxBaosFT12Header.DESCRIPTION_RES:
            return "description.res"
        elif self._service == KnxBaosFT12Header.SEARCH_REQ:
            return "search.req"
        elif self._service == KnxBaosFT12Header.SEARCH_RES:
            return "search.res"
        elif self._service == KnxBaosFT12Header.DEVICE_CONFIGURATION_REQ:
            return "device-configuration.req"
        elif self._service == KnxBaosFT12Header.DEVICE_CONFIGURATION_ACK:
            return "device-configuration.ack"
        elif self._service == KnxBaosFT12Header.TUNNELING_REQ:
            return "tunneling.req"
        elif self._service == KnxBaosFT12Header.TUNNELING_ACK:
            return "tunneling.ack"
        elif self._service == KnxBaosFT12Header.ROUTING_IND:
            return "routing.ind"
        elif self._service == KnxBaosFT12Header.ROUTING_LOST_MSG:
            return "routing-lost.msg"
        else:
            return "unknown/unsupported service"
