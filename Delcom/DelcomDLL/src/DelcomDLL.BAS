' Delcom Engineering - Copyright 2005
' Delcom Dll VB declare file
' Constant and Function declaration
' 02/12/07 Version 0.6

Public Const USBIODS = 1
Public Const USBDELVI = 2
Public Const USBNDSPY = 3

Public Const LEDOFF = 0
Public Const LEDON = 1
Public Const LEDFLASH = 2

Public Const GREENLED = 0
Public Const REDLED = 1
Public Const BLUELED = 2

Public Const MAXDEVICENAMELEN = 512

Private Type PacketStructure
    Recipient   As Byte
    DeviceModel As Byte
    MajorCmd    As Byte
    MinorCmd    As Byte
    DataLSB     As Byte
    DataMSB     As Byte
    Length      As Byte
    DataExt(7)  As Byte
End Type

Private Type DataExtStructure
    B(7) As Byte
End Type



' Declare references to the external procedures in the dynamic-link library (DLL).
    
Private Declare Function DelcomVerboseControl Lib "DelcomDLL.dll" _
    (ByVal Mode As Long, ByVal caption As String) As Long
    
Private Declare Function DelcomGetDLLVersion Lib "DelcomDLL.dll" _
    () As Double

Private Declare Function DelcomGetDLLDate Lib "DelcomDLL.dll" _
    (ByVal datestring As String) As Long

' Generic Functions
Private Declare Function DelcomGetDeviceCount Lib "DelcomDLL.dll" _
    (ByVal ProductType As Long) As Long
    
Private Declare Function DelcomGetNthDevice Lib "DelcomDLL.dll" _
    (ByVal ProductType As Long, ByVal NthDevice As Long, ByVal DeviceName As String) As Long
    
Private Declare Function DelcomOpenDevice Lib "DelcomDLL.dll" _
    (ByVal DeviceName As String, ByVal Mode As Long) As Long
    
Private Declare Function DelcomCloseDevice Lib "DelcomDLL.dll" _
    (ByVal DeviceHandle As Long) As Long
    
Private Declare Function DelcomReadDeviceVersion Lib "DelcomDLL.dll" _
    (ByVal DeviceHandle As Long) As Long
    
Private Declare Function DelcomReadDeviceSerialNum Lib "DelcomDLL.dll" _
    (ByVal DeviceName As String, ByVal DeviceHandle As Long) As Long
 
Private Declare Function DelcomSendPacket Lib "DelcomDLL.dll" _
    (ByVal DeviceHandle As Long, ByRef PacketOut As PacketStructure, ByRef PacketIn As PacketStructure) As Long
    
' USBDELVI - Visual Indicator Functions
Private Declare Function DelcomLEDControl Lib "DelcomDLL.dll" _
    (ByVal DeviceHandle As Long, ByVal Color As Long, ByVal Mode As Long) As Long
        
Private Declare Function DelcomLoadLedFreqDuty Lib "DelcomDLL.dll" _
    (ByVal DeviceHandle As Long, ByVal Color As Byte, ByVal Low As Byte, ByVal High As Byte) As Long
    
Private Declare Function DelcomEnableAutoConfirm Lib "DelcomDLL.dll" _
    (ByVal DeviceHandle As Long, ByVal Mode As Long) As Long

Private Declare Function DelcomEnableAutoClear Lib "DelcomDLL.dll" _
    (ByVal DeviceHandle As Long, ByVal Mode As Long) As Long

Private Declare Function DelcomBuzzer Lib "DelcomDLL.dll" _
    (ByVal DeviceHandle As Long, ByVal Mode As Byte, ByVal Freq As Byte, ByVal Repeat As Byte, ByVal OnTime As Byte, ByVal OffTime As Byte) As Long

Private Declare Function DelcomLoadInitialPhaseDelay Lib "DelcomDLL.dll" _
    (ByVal DeviceHandle As Long, ByVal Color As Byte, ByVal Delay As Byte) As Long

Private Declare Function DelcomSyncLeds Lib "DelcomDLL.dll" _
    (ByVal DeviceHandle As Long) As Long

Private Declare Function DelcomLoadPreScalar Lib "DelcomDLL.dll" _
    (ByVal DeviceHandle As Long, ByVal PreScalar As Byte) As Long

Private Declare Function DelcomGetButtonStatus Lib "DelcomDLL.dll" _
    (ByVal DeviceHandle As Long) As Long

Private Declare Function DelcomLEDPower Lib "DelcomDLL.dll" _
    (ByVal DeviceHandle As Long, Color As Long, Power As Long) As Long
    
 
' USBIODS - USB IO Functions
Private Declare Function DelcomWritePin Lib "DelcomDLL.dll" _
    (ByVal DeviceHandle As Long, ByVal Port As Byte, ByVal Pin As Byte, ByVal Value As Byte) As Long

Private Declare Function DelcomWritePorts Lib "DelcomDLL.dll" _
    (ByVal DeviceHandle As Long, ByVal Port0 As Byte, ByVal Port1 As Byte) As Long
    
Private Declare Function DelcomReadPorts Lib "DelcomDLL.dll" _
    (ByVal DeviceHandle As Long, ByRef Port0 As Byte, ByRef Port1 As Byte) As Long
    
Private Declare Function DelcomWrite64Bit Lib "DelcomDLL.dll" _
    (ByVal DeviceHandle As Long, ByRef DataExt As DataExtStructure) As Long
    
Private Declare Function DelcomRead64Bit Lib "DelcomDLL.dll" _
    (ByVal DeviceHandle As Long, ByRef DataExt As DataExtStructure) As Long
        
Private Declare Function DelcomWriteI2C Lib "DelcomDLL.dll" _
    (ByVal DeviceHandle As Long, ByVal CmdAdd As Byte, ByVal Length As Byte, ByRef DataExt As DataExtStructure) As Long
      
Private Declare Function DelcomReadI2C Lib "DelcomDLL.dll" _
    (ByVal DeviceHandle As Long, ByVal CmdAdd As Byte, ByVal Length As Byte, ByRef DataExt As DataExtStructure) As Long

Private Declare Function DelcomSelReadI2C Lib "DelcomDLL.dll" _
    (ByVal DeviceHandle As Long, ByVal SetAddCmd As Byte, ByVal Address As Byte, ByVal ReadCmd As Byte, ByVal Length As Byte, ByRef DataExt As DataExtStructure) As Long

Private Declare Function DelcomReadI2CEEPROM Lib "DelcomDLL.dll" _
    (ByVal DeviceHandle As Long, ByVal Address As Long, ByVal Size As Long, ByVal CtrlCode As Byte, ByRef Data As String) As Long

Private Declare Function DelcomWriteI2CEEPROM Lib "DelcomDLL.dll" _
    (ByVal DeviceHandle As Long, ByVal Address As Long, ByVal Size As Long, ByVal CtrlCode As Byte, ByVal WriteDelay As Byte, ByRef Data As String) As Long

Private Declare Function DelcomRS232Ctrl Lib "DelcomDLL.dll" _
    (ByVal DeviceHandle As Long, ByVal Mode As Long, ByVal Value As Long) As Long

Private Declare Function DelcomWriteRS232 Lib "DelcomDLL.dll" _
    (ByVal DeviceHandle As Long, ByVal Length As Long, ByRef DataExt As DataExtStructure) As Long
    
Private Declare Function DelcomReadRS232 Lib "DelcomDLL.dll" _
    (ByVal DeviceHandle As Long, ByRef DataExt As DataExtStructure) As Long
 

Private Declare Function DelcomSPIWrite Lib "DelcomDLL.dll" _
    (ByVal DeviceHandle As Long, ByVal ClockCount As Long, ByRef Data As String) As Long
Private Declare Function DelcomSPISetClock Lib "DelcomDLL.dll" _
    (ByVal DeviceHandle As Long, ByVal ClockCount As Long) As Long
Private Declare Function DelcomSPIRead Lib "DelcomDLL.dll" _
    (ByVal DeviceHandle As Long, ByRef Data As String) As Long
Private Declare Function DelcomSPIWr8Read64 Lib "DelcomDLL.dll" _
    (ByVal DeviceHandle As Long, ByVal WrData As Long, ByVal ClockCount As Long, ByRef Data As String) As Long



'   USBNDSPY Functions
Private Declare Function DelcomNumericMode Lib "DelcomDLL.dll" _
    (ByVal DeviceHandle As Long, ByVal Mode As Byte, ByVal Rate As Byte) As Long
Private Declare Function DelcomNumericScanRate Lib "DelcomDLL.dll" _
    (ByVal DeviceHandle As Long, ByVal ScanRate As Byte) As Long
Private Declare Function DelcomNumericSetup Lib "DelcomDLL.dll" _
    (ByVal DeviceHandle As Long, ByVal Digits As Byte) As Long
Private Declare Function DelcomNumericRaw Lib "DelcomDLL.dll" _
    (ByVal DeviceHandle As Long, ByVal Str As String) As Long
Private Declare Function DelcomNumericInteger Lib "DelcomDLL.dll" _
    (ByVal DeviceHandle As Long, ByVal Number As Long, ByVal Base As Long) As Long
Private Declare Function DelcomNumericHexaDecimal Lib "DelcomDLL.dll" _
    (ByVal DeviceHandle As Long, ByVal Number As Long, ByVal Base As Long) As Long
Private Declare Function DelcomNumericDouble Lib "DelcomDLL.dll" _
    (ByVal DeviceHandle As Long, ByVal Number As Double, ByVal Base As Long) As Long
