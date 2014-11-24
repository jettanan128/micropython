import logging


class KnxBaosListener:
    """
    """
    def __init__(self):
        """
        """

        self._logger = logging.getLogger("KnxBaosListener")

    def handleResetInd(self):
        """ Handle reset indication

        BAOS has been reset (could be due to a change of the parameters via ETS).
        """
        pass
        #App_RetrieveParameterBytes()  # request parameter bytes
        #  ->  KnxBaos_GetParameterByte(PB_FIRST, PB_MAX - 1)

    def handleGetServerItemRes(self, itemId, itemData):
        """ Handle the GetServerItem.Res data

        A KNX telegram can hold more than one data. This functions gets called for
        every single data in a telegram array.

        @param itemId: current Item ID from telegram
        @param itemData: data of current Item from telegram
        """
        self._logger.debug("handleGetServerItemRes(): itemId={}, itemData={}".format(itemId, repr(itemData)))

    def handleSetServerItemRes(self, startItem):
        """Handle the SetServerItem.Res data

        @param startItem Start Item from telegram
        """
        self._logger.debug("handleSetServerItemRes(): startItem={}".format(startItem))

    def handleGetDatapointDescriptionRes(self, dpId, dpValueLength, dpConfigFlags):
        """Handle the GetDatapointDescription.Res data

        A BAOS telegram can hold more than one data. This functions is called
        for every single value (Datapoint) in a telegram array.

        @param dpId: current Datapoint ID from telegram
        @param dpValueLength: length of current Datapoint from telegram
        @param dpConfigFlags: configuration flags of current Datapoint from telegram
        """
        self._logger.debug("handleGetDatapointDescriptionRes(): dpId={}, dpValueLength={}, dpConfigFlags={}".format(dpId, dpValueLength, dpConfigFlags))

    def handleGetDescriptionStringRes(self, dpId, dpDescriptionStr):
        """Handle the GetDescriptionString.Res data

        A KNX telegram can hold more than one data. This functions gets called for
        every single data in a telegram array.

        @param dpId: current Datapoint ID from telegram
        @param dpDescriptionStr: description string of current Datapointfrom telegram
        """
        self._logger.debug("handleGetDescriptionStringRes(): dpId={}, dpDescriptionStr={}".format(dpId, dpDescriptionStr))

    def handleGetDatapointValueRes(self, dpId, dpState, dpData):
        """ Handle the GetDatapointValue.Res data

        A KNX telegram can hold more than one data. This functions gets called for
        every single data in a telegram array.

        @param dpId: current Datapoint ID from telegram
        @param dpState: state of current Datapoint from telegram
        @param dpData: data of current Datapointfrom telegram
        """
        self._logger.debug("handleGetDatapointValueRes(): dpId={}, dpState={}, dpData={}".format(dpId, dpState, repr(dpData)))

    def handleDatapointValueInd(self, dpId, dpState, dpData):
        """Handle the DatapointValue.Ind data

        A KNX telegram can hold more than one data. This functions gets called for
        every single data in a telegram array.

        @param dpId: current Datapoint ID from telegram
        @param dpState: state of current Datapoint from telegram
        @param dpData: data of current Datapointfrom telegram
        """
        self._logger.debug("handleDatapointValueInd(): dpId={}, dpState={}, dpData={}".format(dpId, dpState, repr(dpData)))
        #switch(dpId)
        #{
            #case DP_LED0_SWITCH_I:                                                    # Switch object selected

                #if(dpLength == 1)                                                    # We expect 1 byte data length
                #{
                    ## Example for receiving a 32 bit value with correct endianess:
                    ## float fValue = *(float *)KnxBaos_Net2Host32(data);

                    #if(*data == SWITCH_ON)                                            # Switch on
                    #{
                        #AppDim_Switch(TRUE);
                    #}
                    #else if(*data == SWITCH_OFF)                                    # Switch off
                    #{
                        #AppDim_Switch(FALSE);
                    #}
                #}

                #break;

            #case DP_LED0_DIM_RELATIVE_I:                                            # Relative dimming object selected

                #if(dpLength == 1)                                                    # We expect 1 byte data length
                #{
                    #AppDim_DimRelative(*data);
                #}

                #break;

            #case DP_LED0_DIM_ABSOLUTE_I:                                            # Absolute dimming object selected

                #if(dpLength == 1)                                                    # We expect 1 byte data length
                #{
                    #AppDim_DimAbsolute(((uint16_t)*data)*255/100);
                #}

                #break;

            #default:                                                                # Ignore all other data points
                #break;
        #}
    #}

    def handleSetDatapointValueRes(self startDatapoint):
        """ Handle the SetDatapointValue.Res data

        @param startDataPoint: start Datapoint from telegram
        """
        pass

    def handleGetParameterByteRes(self, byteNum, byte):
        """ Handle the GetParameterByte.Res data

        A KNX telegram can hold more than one data. This functions gets called for
        every single data in a telegram array.

        @param byteNum: current byte number from telegram
        @param byte: current byte from telegram
        """
        pass
        #switch(byteNum)                                                                # Parameter byte number
        #{
            #case PB_SWITCH_TYPE:                                                    # Set Datapoint #1 and #2 type
                #m_nSwitchType = byte;
                #break;

            #case PB_LIGHT_TYPE:                                                        # Set Datapoint #3, #4 and #5
                #m_nLightType = byte;
                #break;

            #default:                                                                # Ignore all other parameter bytes
                #break;
        #}
    #}

    def handleError(self, errorCode):
        """ Handle error code

         0 = No error (this function gets never called with that)
         1 = Internal error
         2 = No Item found
         3 = Buffer is too small
         4 = Item is not writable
         5 = Service is not supported
         6 = Bad service parameter
         7 = Wrong Datapoint ID
         8 = Bad Datapoint command
         9 = Bad length of the Datapoint value
        10 = Message inconsistent

        @param errorCode: KNX BAOS ObjectServer error code
        """
        pass
