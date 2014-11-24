

class KnxBaosListener:
    """
    """
    def __init__(self):
        """
        """

    def handleResetInd(self):
        """ Handle reset indication

        BAOS has been reset (could be due to a change of the parameters via ETS).
        """
        pass
        #App_RetrieveParameterBytes()  # request parameter bytes
        #  ->  KnxBaos_GetParameterByte(PB_FIRST, PB_MAX - 1)

    def handleGetServerItemRes(self, startItem, itemId, itemDataLength, data):
        """ Handle the GetServerItem.Res data.

        A KNX telegram can hold more than one data. This functions gets called for
        every single data in a telegram array.

        @param startItem: start item from telegram
        @param itemId: current item ID from telegram
        @param itemDataLength: length of current byte data from telegram
        @param data: data from telegram
        """
        pass
    ##ifdef _USE_PROGMODE
        #KnxProgMode_HandleGetServerItemRes(
            #startItem, itemId, itemDataLength, data)  # forward to prog mode service
    ##endif

    def handleSetServerItemRes(self, startItem):
        """Handle the SetServerItem.Res data

        @param startItem Start item from telegram
        """
        pass

    def handleGetDatapointDescriptionRes(self, startDatapoint, dpValueLength, dpConfigFlags):
        """Handle the GetDatapointDescription.Res data

        A BAOS telegram can hold more than one data. This functions is called
        for every single value (data point) in a telegram array.

        @param startDataPoint Start data point from telegram
        @param dpValueLength Current length from telegram
        @param dpConfigFlags Current configuration flags from telegram
        """
        pass

    def handleGetDescriptionStringRes(self, sartStr, dpDescription, dpDescriptionLength):
        """Handle the GetDescriptionString.Res data

        A KNX telegram can hold more than one data. This functions gets called for
        every single data in a telegram array.

        @param startStr Start string from telegram
        @param dpDescription Pointer to current string from telegram
        @param dpDescriptionLength Length of current string from telegram
        """
        pass

    def handleGetDatapointValueRes(self, startDatapoint, dpId, dpState, dpLength, data):
        """ Handle the GetDatapointValue.Res data

        A KNX telegram can hold more than one data. This functions gets called for
        every single data in a telegram array.

        @param startDataPoint: start data point from telegram
        @param dpId: current data point ID from telegram
        @param dpState: current data point state from telegram
        @param dpLength: current data point length from telegram
        @param data: data from telegram
        """
        pass

    def handleDatapointValueInd(self, dpId, dpState, dpLength, data):
        """Handle the DatapointValue.Ind data

        A KNX telegram can hold more than one data. This functions gets called for
        every single data in a telegram array.

        @param dpId: current data point ID from telegram
        @param dpState: current data point state from telegram
        @param dpLength: current data point length from telegram
        @param data: data from telegram
        """
        pass
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

        @param startDataPoint: start data point from telegram
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
            #case PB_SWITCH_TYPE:                                                    # Set data point #1 and #2 type
                #m_nSwitchType = byte;
                #break;

            #case PB_LIGHT_TYPE:                                                        # Set data point #3, #4 and #5
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
         2 = No item found
         3 = Buffer is too small
         4 = Item is not writable
         5 = Service is not supported
         6 = Bad service parameter
         7 = Wrong data point ID
         8 = Bad data point command
         9 = Bad length of the data point value
        10 = Message inconsistent

        @param errorCode: KNX BAOS ObjectServer error code
        """
        pass
