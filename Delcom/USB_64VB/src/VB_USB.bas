Attribute VB_Name = "VB_USB"
' Filename: VB_USB
' Author:   Doug Lovett
' Birth:    01/20/2002
' Delcom Engineering Copyright 2002  - www.delcom-eng.com
' Subject:  Functions to access the USB IO Device.
' Include this file in your VB project and call these functions
' to access the USB IO device

' Global data variables
Public hDevice As Long      'Handle to the device
Public lpDeviceName As String 'Copy of the device name

' Registry and File Constants
Const HKEY_LOCAL_MACHINE = &H80000002
Const GENERIC_READ = &H80000000
Const GENERIC_WRITE = &H40000000
Const FILE_SHARE_WRITE = &H2
Const FILE_SHARE_READ = &H1
Const OPEN_EXISTING = &H3
Const CTL_CODE_SEND_PACKET = &H222028

Public Type PacketStructure
    Recipient   As Byte
    DeviceModel As Byte
    MajorCmd    As Byte
    MinorCmd    As Byte
    DataLSB     As Byte
    DataMSB     As Byte
    Length      As Integer
    DataExt(8)  As Byte
End Type

Public Type RetPacketStructure
    B0   As Byte
    B1   As Byte
    B2   As Byte
    B3   As Byte
    B4   As Byte
    B5   As Byte
    B6   As Byte
    B7   As Byte
End Type


' declare references to external procedures in a dynamic-link library (DLL).
Declare Function RegOpenKeyEx Lib "advapi32" Alias "RegOpenKeyExA" _
    (ByVal hKey As Long, ByVal lpSubKey As String, ByVal ulOptions As Long, _
    ByVal samDesired As Long, phkResult As Long) As Long

Declare Function RegQueryValueEx Lib "advapi32" Alias "RegQueryValueExA" _
    (ByVal hKey As Long, ByVal lpValueName As String, ByVal lpReserved As Long, _
    ByRef lpType As Long, ByVal szData As String, ByRef lpcbData As Long) As Long
    
Declare Function RegCloseKey Lib "advapi32" (ByVal hKey As Long) As Long

Declare Function CreateFile Lib "kernel32" Alias "CreateFileA" _
    (ByVal lpFileName As String, ByVal dwDesiredAccess As Long, _
     ByVal dwShareMode As Long, ByVal lpSecurityAttributes As Long, _
     ByVal dwCreationDisposition As Long, ByVal dwFlagsAndAttributes As Long, _
     ByVal hTemplateFile As Long) As Long
     
Declare Function CloseHandle Lib "kernel32" (ByVal hObject As Long) As Boolean

Declare Function DeviceIoControl Lib "kernel32" _
    (ByVal hDevice As Long, ByVal dwIocontrolCode As Long, _
     ByRef lpBuffer As PacketStructure, ByVal nInBufferSize As Long, _
     ByRef lpOutBuffer As RetPacketStructure, ByVal nOutBufferSize As Long, _
     ByRef lpBytesReturned As Long, ByVal lpOverLapped As Long) As Boolean
     
    
'OpenDevice - This function reads the device name from the registry and then
'opens the device and stores a handle to the device in hDevice. Returns zero
'on error.  This function also stores the full device name is DeviceName.
Function OpenDevice() As Boolean
On Error GoTo ERROR_HANDLER

'Get Device Name from the registry
lpDeviceName = GetRegValue(HKEY_LOCAL_MACHINE, _
                        "System\CurrentControlSet\Services\Delcom\USBIODS\Parameters\", _
                        "DeviceName", "")
If lpDeviceName = "" Then   ' exit on error
    MsgBox "Unable to open device, check connection and power."
    lpDeviceName = "Device Not Found!"
    OpenDevice = False
    Exit Function
End If
' Try and open the device. This will fail if device not present
hDevice = CreateFile(lpDeviceName, GENERIC_READ Or GENERIC_WRITE, _
                     FILE_SHARE_WRITE Or FILE_SHARE_READ, 0, _
                     OPEN_EXISTING, 0, 0)

If hDevice <= 0 Then    ' check for error
    MsgBox "Unable to open device, check connection and power"
    lpDeviceName = "Device Not Found!"
    OpenDevice = False
Else
    OpenDevice = True
End If

Exit Function
ERROR_HANDLER:
    MsgBox "OpenDevice() ERROR #" & Str$(Err) & " : " & Error
End Function

'CloseDevice - Closes the device, always close device after use.
'If you don't close the device after use, you will not be able
'to open it up again without cycle pluging the USB cable.
Function CloseDevice() As Boolean
On Error GoTo ERROR_HANDLER
CloseDevice = CloseHandle(hDevice)  ' Close the device
hDevice = 0                         ' Null the handle
If CloseDevice = False Then         ' Check for errors
    MsgBox "Error closing file"     ' Display errors
End If
Exit Function
ERROR_HANDLER:
    MsgBox "CloseDevice() ERROR #" & Str$(Err) & " : " & Error
End Function

'Sends the USB packet to the device
Function SendPacket(ByRef TxPacket As PacketStructure) As RetPacketStructure
Dim lpResult As Long
Dim RxPacket As RetPacketStructure

On Error GoTo ERROR_HANDLER
If hDevice <= 0 Then                ' check for valid handle
    MsgBox "SendPacket() Handle invalid!"
    Exit Function
End If

TxPacket.Recipient = 8      ' always 8
TxPacket.DeviceModel = 18   ' always 18

     ' Call the read length function
If 0 = DeviceIoControl(hDevice, CTL_CODE_SEND_PACKET, TxPacket, 8 + TxPacket.Length, _
                        RxPacket, 8, lpResult, 0) Then
    'MainForm.Timer1.Enabled = False ' turn off timer when error
    MsgBox "SendPacket() DeviceIoControl Failed. Timer Disabled"
    Exit Function
End If

SendPacket = RxPacket

Exit Function

ERROR_HANDLER:
    'MainForm.Timer1.Enabled = False ' turn off timer when error
    MsgBox "SendPacket() ERROR #" & Str$(Err) & " : " & Error & " Timer Disabled"
End Function

' GetRegValue - Gets the Key value in the registry given a registry key.
Function GetRegValue(hKey As Long, lpszSubKey As String, szKey As String, _
                     szDefault As String) As String
On Error GoTo ERROR_HANDLER

Dim phkResult As Long, lResult As Long
Dim szBuffer As String, lBuffSize As Long

'Create Buffer
szBuffer = Space(255)           ' Allocate buffer space
lBuffSize = Len(szBuffer)       ' Set the length

                                'Open the Key
RegOpenKeyEx hKey, lpszSubKey, 0, 1, phkResult

                                'Query the value
lResult = RegQueryValueEx(phkResult, szKey, 0, 0, szBuffer, lBuffSize)

RegCloseKey phkResult           'Close the Key

'Return obtained value
If lResult = ERROR_SUCCESS Then
    GetRegValue = szBuffer
Else
    GetRegValue = szDefault
End If
Exit Function

ERROR_HANDLER:
    MsgBox "GetRegValue() ERROR #" & Str$(Err) & " : " & Error & Chr(13) _
    & "Please exit and try again."
        
    GetRegValue = szDefault
End Function

