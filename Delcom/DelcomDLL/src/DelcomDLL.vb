' Delcom Engineering - Copyright 2007
' Delcom Dll VB.Net declaration class file
' Constants and Functions declaration
' File Date: 02/12/2007 Version 0.6
' How to use this Delcom class
' 1 Copy the DelcomDll.dll file into the directory that the compiled file runs from.
'   In most cases this is the projectname/bin/debug and projectname/bin/release directories.
' 2 Copy this file (DelcomDll.vb) in to the projectname directory.
' 3 Add this file to the project. (Right click in the Solution Explorer, Add/Existing item...)
' 4 In you main code add the following example code:
'   
'   Imports System
'   Imports System.Text
'   Imports Microsoft.VisualBasic
'
'   'VB.Net DelcomDll Example to blink the green led.
'   'All strings passed to DLL must be preallocated
'   Dim DeviceName As New StringBuilder("", Delcom.MAXDEVICENAMELEN)
'   Dim Result As Integer
'   Dim DeviceHandle As Integer
'   ' Try and find the first USB device. For the USB IO chips use Delcom.USBIODS.
'   Result = Delcom.DelcomGetNthDevice(Delcom.USBDELVI, 0, DeviceName)
'   If (Result) Then
'       MessageBox.Show(DeviceName.ToString, "Device Found")
'       ' Open the USB device
'       DeviceHandle = Delcom.DelcomOpenDevice(DeviceName, 0)
'       ' Blink the Green LED
'       Result = Delcom.DelcomLEDControl(DeviceHandle, Delcom.GREENLED, Delcom.LEDFLASH)
'       'Close the USB Device
'       Result = Delcom.DelcomCloseDevice(DeviceHandle)
'   Else ' Device not found
'       MessageBox.Show("Device Not Found")
'       End If




Imports System
Imports System.Text
Imports Microsoft.VisualBasic
Imports System.Runtime.InteropServices

Public Class Delcom
    ' Delcom USB Devices
    Public Const USBIODS = 1
    Public Const USBDELVI = 2
    Public Const USBNDSPY = 3

    ' USBDELVI LED MODES
    Public Const LEDOFF = 0
    Public Const LEDON = 1
    Public Const LEDFLASH = 2

    ' USBDELVI LED COlORS
    Public Const GREENLED = 0
    Public Const REDLED = 1
    Public Const BLUELED = 2

    ' Device Name Maximum Length
    Public Const MAXDEVICENAMELEN = 512

    ' USB Packet Structures

    ' USB Data IO Packact
    <StructLayout(LayoutKind.Sequential)> _
    Public Structure PacketStructure
        Public Recipient As Byte
        Public DeviceModel As Byte
        Public MajorCmd As Byte
        Public MinorCmd As Byte
        Public DataLSB As Byte
        Public DataMSB As Byte
        Public Length As Byte
        Public DataExt0 As Byte
        Public DataExt1 As Byte
        Public DataExt2 As Byte
        Public DataExt3 As Byte
        Public DataExt4 As Byte
        Public DataExt5 As Byte
        Public DataExt6 As Byte
        Public DataExt7 As Byte
    End Structure


    ' Return data struture
    <StructLayout(LayoutKind.Sequential)> _
    Public Structure DataExtStructure
        Public Data0 As Byte
        Public Data1 As Byte
        Public Data2 As Byte
        Public Data3 As Byte
        Public Data4 As Byte
        Public Data5 As Byte
        Public Data6 As Byte
        Public Data7 As Byte
    End Structure



    ' Delcom DLL Fucnctions - See the DelcomDLL.pdf for documentation

    ' Gets the DelcomDLL verison
    <DllImport("delcomdll.dll", CallingConvention:=CallingConvention.Cdecl)> _
    Overloads Shared Function DelcomGetDLLVersion() As Double
    End Function

    ' Sets the verbose controll - used for debugging
    <DllImport("delcomdll.dll", CallingConvention:=CallingConvention.Cdecl)> _
    Overloads Shared Function DelcomVerboseControl(ByVal Mode As Long, ByVal caption As StringBuilder) As Integer
    End Function

    ' Gets the DLL date
    <DllImport("delcomdll.dll", CallingConvention:=CallingConvention.Cdecl)> _
        Overloads Shared Function DelcomGetDLLDate(ByVal datestring As StringBuilder) As Integer
    End Function

    ' Generic Functions

    'Gets DeviceCount
    <DllImport("delcomdll.dll", CallingConvention:=CallingConvention.Cdecl)> _
        Overloads Shared Function DelcomGetDeviceCount(ByVal ProductType As Integer) As Integer
    End Function

    ' Gets Nth Device
    <DllImport("delcomdll.dll", CallingConvention:=CallingConvention.Cdecl)> _
        Overloads Shared Function DelcomGetNthDevice(ByVal ProductType As Integer, ByVal NthDevice As Integer, ByVal DeviceName As StringBuilder) As Integer
    End Function

    ' Open Device
    <DllImport("delcomdll.dll", CallingConvention:=CallingConvention.Cdecl)> _
        Overloads Shared Function DelcomOpenDevice(ByVal DeviceName As StringBuilder, ByVal Mode As Integer) As Integer
    End Function

    ' Close Device
    <DllImport("delcomdll.dll", CallingConvention:=CallingConvention.Cdecl)> _
        Overloads Shared Function DelcomCloseDevice(ByVal DeviceHandle As Integer) As Integer
    End Function


    ' Read USB Device Version
    <DllImport("delcomdll.dll", CallingConvention:=CallingConvention.Cdecl)> _
        Overloads Shared Function DelcomReadDeviceVersion(ByVal DeviceHandle As Integer) As Integer
    End Function

    ' Read USB Device SerialNumber
    <DllImport("delcomdll.dll", CallingConvention:=CallingConvention.Cdecl)> _
        Overloads Shared Function DelcomReadDeviceSerialNum(ByVal DeviceName As StringBuilder, ByVal DeviceHandle As Integer) As Integer
    End Function

    ' Send USB Packet
    <DllImport("delcomdll.dll", CallingConvention:=CallingConvention.Cdecl)> _
        Overloads Shared Function DelcomSendPacket(ByVal DeviceHandle As Integer, ByRef PacketOut As PacketStructure, ByRef PacketIn As PacketStructure) As Integer
    End Function



    ' USBDELVI - Visual Indicator Functions

    ' Set LED Functions
    <DllImport("delcomdll.dll", CallingConvention:=CallingConvention.Cdecl)> _
        Overloads Shared Function DelcomLEDControl(ByVal DeviceHandle As Integer, ByVal Color As Integer, ByVal Mode As Integer) As Integer
    End Function

    ' Set LED Freq/Duty functions
    <DllImport("delcomdll.dll", CallingConvention:=CallingConvention.Cdecl)> _
        Overloads Shared Function DelcomLoadLedFreqDuty(ByVal DeviceHandle As Integer, ByVal Color As Byte, ByVal Low As Byte, ByVal High As Byte) As Integer
    End Function


    ' Set Auto Confirm Mode
    <DllImport("delcomdll.dll", CallingConvention:=CallingConvention.Cdecl)> _
        Overloads Shared Function DelcomEnableAutoConfirm(ByVal DeviceHandle As Integer, ByVal Mode As Integer) As Integer
    End Function

    ' Set Auto Clear Mode
    <DllImport("delcomdll.dll", CallingConvention:=CallingConvention.Cdecl)> _
        Overloads Shared Function DelcomEnableAutoClear(ByVal DeviceHandle As Integer, ByVal Mode As Integer) As Integer
    End Function


    ' Set Buzzer Function
    <DllImport("delcomdll.dll", CallingConvention:=CallingConvention.Cdecl)> _
        Overloads Shared Function DelcomBuzzer(ByVal DeviceHandle As Integer, ByVal Mode As Byte, ByVal Freq As Byte, ByVal Repeat As Byte, ByVal OnTime As Byte, ByVal OffTime As Byte) As Integer
    End Function

    ' Set LED Phase Delay
    <DllImport("delcomdll.dll", CallingConvention:=CallingConvention.Cdecl)> _
        Overloads Shared Function DelcomLoadInitialPhaseDelay(ByVal DeviceHandle As Integer, ByVal Color As Byte, ByVal Delay As Byte) As Integer
    End Function

    ' Set Led Sync Functions
    <DllImport("delcomdll.dll", CallingConvention:=CallingConvention.Cdecl)> _
        Overloads Shared Function DelcomSyncLeds(ByVal DeviceHandle As Integer) As Integer
    End Function


    ' Set LED PreScalar Functions
    <DllImport("delcomdll.dll", CallingConvention:=CallingConvention.Cdecl)> _
        Overloads Shared Function DelcomLoadPreScalar(ByVal DeviceHandle As Integer, ByVal PreScalar As Byte) As Integer
    End Function


    ' Get Button Status
    <DllImport("delcomdll.dll", CallingConvention:=CallingConvention.Cdecl)> _
        Overloads Shared Function DelcomGetButtonStatus(ByVal DeviceHandle As Integer) As Integer
    End Function

    ' Set LED Power
    <DllImport("delcomdll.dll", CallingConvention:=CallingConvention.Cdecl)> _
        Overloads Shared Function DelcomLEDPower(ByVal DeviceHandle As Integer, ByVal Color As Integer, ByVal Power As Integer) As Integer
    End Function



    ' USBIODS - USB IO Functions

   ' Set Port Pin
    <DllImport("delcomdll.dll", CallingConvention:=CallingConvention.Cdecl)> _
        Overloads Shared Function DelcomWritePin(ByVal DeviceHandle As Integer, ByVal Port As Byte, ByVal Pin As Byte, ByVal Value As Byte) As Integer
    End Function


    ' Set Ports
    <DllImport("delcomdll.dll", CallingConvention:=CallingConvention.Cdecl)> _
        Overloads Shared Function DelcomWritePorts(ByVal DeviceHandle As Integer, ByVal Port0 As Byte, ByVal Port1 As Byte) As Integer
    End Function


    ' Get Ports 
    <DllImport("delcomdll.dll", CallingConvention:=CallingConvention.Cdecl)> _
        Overloads Shared Function DelcomReadPorts(ByVal DeviceHandle As Integer, ByRef Port0 As Byte, ByRef Port1 As Byte) As Integer
    End Function


    ' Set 64Bit Value
    <DllImport("delcomdll.dll", CallingConvention:=CallingConvention.Cdecl)> _
        Overloads Shared Function DelcomWrite64Bit(ByVal DeviceHandle As Integer, ByRef DataExt As DataExtStructure) As Integer
    End Function

    ' Get 64Bit Value
    <DllImport("delcomdll.dll", CallingConvention:=CallingConvention.Cdecl)> _
        Overloads Shared Function DelcomRead64Bit(ByVal DeviceHandle As Integer, ByRef DataExt As DataExtStructure) As Integer
    End Function

    ' Write I2C Functions 
    <DllImport("delcomdll.dll", CallingConvention:=CallingConvention.Cdecl)> _
        Overloads Shared Function DelcomWriteI2C(ByVal DeviceHandle As Integer, ByVal CmdAdd As Byte, ByVal Length As Byte, ByRef DataExt As DataExtStructure) As Integer
    End Function

    ' Read I2C Functions
    <DllImport("delcomdll.dll", CallingConvention:=CallingConvention.Cdecl)> _
        Overloads Shared Function DelcomReadI2C(ByVal DeviceHandle As Integer, ByVal CmdAdd As Byte, ByVal Length As Byte, ByRef DataExt As DataExtStructure) As Integer
    End Function

    ' Get I2C Slect Read 
    <DllImport("delcomdll.dll", CallingConvention:=CallingConvention.Cdecl)> _
        Overloads Shared Function DelcomSelReadI2C(ByVal DeviceHandle As Integer, ByVal SetAddCmd As Byte, ByVal Address As Byte, ByVal ReadCmd As Byte, ByVal Length As Byte, ByRef DataExt As DataExtStructure) As Integer
    End Function

    ' Read I2C EEPROM Functions
    <DllImport("delcomdll.dll", CallingConvention:=CallingConvention.Cdecl)> _
        Overloads Shared Function DelcomReadI2CEPPROM(ByVal DeviceHandle As Integer, ByVal Address As Integer, ByVal Size As Integer, ByVal CtrlCode As Byte, ByRef Data As String) As Integer
    End Function

    ' Write I2C EEPROM Functions
    <DllImport("delcomdll.dll", CallingConvention:=CallingConvention.Cdecl)> _
        Overloads Shared Function DelcomReadI2CEPPROM(ByVal DeviceHandle As Integer, ByVal Address As Integer, ByVal Size As Integer, ByVal CtrlCode As Byte, ByVal WriteDelay As Byte, ByRef Data As String) As Integer
    End Function


    ' Setup RS232 Mode
    <DllImport("delcomdll.dll", CallingConvention:=CallingConvention.Cdecl)> _
        Overloads Shared Function DelcomRS232Ctrl(ByVal DeviceHandle As Integer, ByVal Mode As Integer, ByVal Value As Integer) As Integer
    End Function


    ' Write RS232 Function
    <DllImport("delcomdll.dll", CallingConvention:=CallingConvention.Cdecl)> _
        Overloads Shared Function DelcomWriteRS232(ByVal DeviceHandle As Integer, ByVal Length As Long, ByRef DataExt As DataExtStructure) As Integer
    End Function


    ' Read RS232 Function
    <DllImport("delcomdll.dll", CallingConvention:=CallingConvention.Cdecl)> _
        Overloads Shared Function DelcomReadRS232(ByVal DeviceHandle As Integer, ByRef DataExt As DataExtStructure) As Integer
    End Function


    ' SPI Write Function
    <DllImport("delcomdll.dll", CallingConvention:=CallingConvention.Cdecl)> _
        Overloads Shared Function DelcomSPIWrite(ByVal DeviceHandle As Integer, ByVal ClockCount As Integer, ByRef DataExt As DataExtStructure) As Integer
    End Function
    ' SPI Set Clock Function
    <DllImport("delcomdll.dll", CallingConvention:=CallingConvention.Cdecl)> _
        Overloads Shared Function DelcomSPISetClock(ByVal DeviceHandle As Integer, ByVal ClockPeriod As Integer) As Integer
    End Function
    ' SPI Read Function
    <DllImport("delcomdll.dll", CallingConvention:=CallingConvention.Cdecl)> _
        Overloads Shared Function DelcomSPIRead(ByVal DeviceHandle As Integer, ByRef DataExt As DataExtStructure) As Integer
    End Function
    ' SPI Write8 Read 64 Function
    <DllImport("delcomdll.dll", CallingConvention:=CallingConvention.Cdecl)> _
        Overloads Shared Function DelcomSPIWrite8Read64(ByVal DeviceHandle As Integer, ByVal WrData As Integer, ByVal ClockCount As Integer, ByRef DataExt As DataExtStructure) As Integer
    End Function




    ' USBNDSPY Functions

    ' Set Numeric Mode
    <DllImport("delcomdll.dll", CallingConvention:=CallingConvention.Cdecl)> _
            Overloads Shared Function DelcomNumericMode(ByVal DeviceHandle As Integer, ByVal Mode As Byte, ByVal Rate As Byte) As Integer
    End Function

    ' Set Numeric Scan Rate
    <DllImport("delcomdll.dll", CallingConvention:=CallingConvention.Cdecl)> _
            Overloads Shared Function DelcomNumericScanRate(ByVal DeviceHandle As Integer, ByVal ScanRate As Byte) As Integer
    End Function

    ' Setup Numeric Digits
    <DllImport("delcomdll.dll", CallingConvention:=CallingConvention.Cdecl)> _
            Overloads Shared Function DelcomNumericSetup(ByVal DeviceHandle As Integer, ByVal Digits As Byte) As Integer
    End Function

    ' Set Numeric Raw Mode
    <DllImport("delcomdll.dll", CallingConvention:=CallingConvention.Cdecl)> _
            Overloads Shared Function DelcomNumericRaw(ByVal DeviceHandle As Integer, ByVal Str As StringBuilder) As Integer
    End Function

    ' Set Numeric Integer Mode
    <DllImport("delcomdll.dll", CallingConvention:=CallingConvention.Cdecl)> _
            Overloads Shared Function DelcomNumericInteger(ByVal DeviceHandle As Integer, ByVal Number As Integer, ByVal Base As Integer) As Integer
    End Function


    ' Set Numeric Hexdecimal Mode
    <DllImport("delcomdll.dll", CallingConvention:=CallingConvention.Cdecl)> _
            Overloads Shared Function DelcomNumericHexaDecimal(ByVal DeviceHandle As Integer, ByVal Number As Integer, ByVal Base As Integer) As Integer
    End Function

    ' Set Numeric Double Mode
    <DllImport("delcomdll.dll", CallingConvention:=CallingConvention.Cdecl)> _
            Overloads Shared Function DelcomNumericDouble(ByVal DeviceHandle As Integer, ByVal Number As Double, ByVal Base As Integer) As Integer
    End Function



End Class