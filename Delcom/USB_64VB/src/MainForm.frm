VERSION 5.00
Begin VB.Form MainForm 
   Caption         =   "Delcom USB 64 Bit IO VB Example Ver 0.1 04/28/2003"
   ClientHeight    =   3630
   ClientLeft      =   5295
   ClientTop       =   4215
   ClientWidth     =   8415
   LinkTopic       =   "MainForm"
   ScaleHeight     =   3630
   ScaleWidth      =   8415
   Begin VB.TextBox RDB 
      Alignment       =   2  'Center
      Enabled         =   0   'False
      Height          =   285
      Index           =   7
      Left            =   6120
      TabIndex        =   31
      Text            =   "00"
      Top             =   2400
      Width           =   735
   End
   Begin VB.TextBox RDB 
      Alignment       =   2  'Center
      Enabled         =   0   'False
      Height          =   285
      Index           =   6
      Left            =   5280
      TabIndex        =   30
      Text            =   "00"
      Top             =   2400
      Width           =   735
   End
   Begin VB.TextBox RDB 
      Alignment       =   2  'Center
      Enabled         =   0   'False
      Height          =   285
      Index           =   5
      Left            =   4440
      TabIndex        =   29
      Text            =   "00"
      Top             =   2400
      Width           =   735
   End
   Begin VB.TextBox RDB 
      Alignment       =   2  'Center
      Enabled         =   0   'False
      Height          =   285
      Index           =   4
      Left            =   3600
      TabIndex        =   28
      Text            =   "00"
      Top             =   2400
      Width           =   735
   End
   Begin VB.TextBox RDB 
      Alignment       =   2  'Center
      Enabled         =   0   'False
      Height          =   285
      Index           =   3
      Left            =   2760
      TabIndex        =   27
      Text            =   "00"
      Top             =   2400
      Width           =   735
   End
   Begin VB.TextBox RDB 
      Alignment       =   2  'Center
      Enabled         =   0   'False
      Height          =   285
      Index           =   2
      Left            =   1920
      TabIndex        =   26
      Text            =   "00"
      Top             =   2400
      Width           =   735
   End
   Begin VB.TextBox RDB 
      Alignment       =   2  'Center
      Enabled         =   0   'False
      Height          =   285
      Index           =   1
      Left            =   1080
      TabIndex        =   25
      Text            =   "00"
      Top             =   2400
      Width           =   735
   End
   Begin VB.TextBox RDB 
      Alignment       =   2  'Center
      Enabled         =   0   'False
      Height          =   285
      Index           =   0
      Left            =   240
      TabIndex        =   24
      Text            =   "00"
      Top             =   2400
      Width           =   735
   End
   Begin VB.TextBox WRB 
      Alignment       =   2  'Center
      Height          =   285
      Index           =   7
      Left            =   6120
      TabIndex        =   15
      Text            =   "00"
      Top             =   1800
      Width           =   735
   End
   Begin VB.TextBox WRB 
      Alignment       =   2  'Center
      Height          =   285
      Index           =   6
      Left            =   5280
      TabIndex        =   14
      Text            =   "00"
      Top             =   1800
      Width           =   735
   End
   Begin VB.TextBox WRB 
      Alignment       =   2  'Center
      Height          =   285
      Index           =   5
      Left            =   4440
      TabIndex        =   13
      Text            =   "00"
      Top             =   1800
      Width           =   735
   End
   Begin VB.TextBox WRB 
      Alignment       =   2  'Center
      Height          =   285
      Index           =   4
      Left            =   3600
      TabIndex        =   12
      Text            =   "00"
      Top             =   1800
      Width           =   735
   End
   Begin VB.TextBox WRB 
      Alignment       =   2  'Center
      Height          =   285
      Index           =   3
      Left            =   2760
      TabIndex        =   11
      Text            =   "00"
      Top             =   1800
      Width           =   735
   End
   Begin VB.TextBox WRB 
      Alignment       =   2  'Center
      Height          =   285
      Index           =   2
      Left            =   1920
      TabIndex        =   10
      Text            =   "00"
      Top             =   1800
      Width           =   735
   End
   Begin VB.TextBox WRB 
      Alignment       =   2  'Center
      Height          =   285
      Index           =   1
      Left            =   1080
      TabIndex        =   9
      Text            =   "00"
      Top             =   1800
      Width           =   735
   End
   Begin VB.TextBox WRB 
      Alignment       =   2  'Center
      Height          =   285
      Index           =   0
      Left            =   240
      TabIndex        =   8
      Text            =   "00"
      Top             =   1800
      Width           =   735
   End
   Begin VB.CommandButton WR2RD8 
      Caption         =   "WR2RD8"
      Enabled         =   0   'False
      Height          =   375
      Left            =   7080
      TabIndex        =   7
      Top             =   1680
      Width           =   975
   End
   Begin VB.CommandButton Read 
      Caption         =   "Read"
      Height          =   375
      Left            =   7080
      TabIndex        =   6
      Top             =   2880
      Width           =   975
   End
   Begin VB.CommandButton Write 
      Caption         =   "Write"
      Height          =   375
      Left            =   7080
      TabIndex        =   5
      Top             =   2280
      Width           =   975
   End
   Begin VB.CommandButton ExitButton 
      Caption         =   "&Exit"
      Height          =   375
      Left            =   7080
      TabIndex        =   0
      Top             =   600
      Width           =   975
   End
   Begin VB.Label Label1 
      Caption         =   "Byte7"
      Height          =   255
      Index           =   7
      Left            =   6240
      TabIndex        =   23
      Top             =   1440
      Width           =   495
   End
   Begin VB.Label Label1 
      Caption         =   "Byte6"
      Height          =   255
      Index           =   6
      Left            =   5400
      TabIndex        =   22
      Top             =   1440
      Width           =   495
   End
   Begin VB.Label Label1 
      Caption         =   "Byte5"
      Height          =   255
      Index           =   5
      Left            =   4560
      TabIndex        =   21
      Top             =   1440
      Width           =   495
   End
   Begin VB.Label Label1 
      Caption         =   "Byte4"
      Height          =   255
      Index           =   4
      Left            =   3720
      TabIndex        =   20
      Top             =   1440
      Width           =   495
   End
   Begin VB.Label Label1 
      Caption         =   "Byte3"
      Height          =   255
      Index           =   3
      Left            =   2880
      TabIndex        =   19
      Top             =   1440
      Width           =   495
   End
   Begin VB.Label Label1 
      Caption         =   "Byte2"
      Height          =   255
      Index           =   2
      Left            =   2040
      TabIndex        =   18
      Top             =   1440
      Width           =   495
   End
   Begin VB.Label Label1 
      Caption         =   "Byte1"
      Height          =   255
      Index           =   1
      Left            =   1200
      TabIndex        =   17
      Top             =   1440
      Width           =   495
   End
   Begin VB.Label Label1 
      Caption         =   "Byte0"
      Height          =   255
      Index           =   0
      Left            =   360
      TabIndex        =   16
      Top             =   1440
      Width           =   495
   End
   Begin VB.Label Label9 
      Caption         =   "DeviceName:"
      Height          =   255
      Left            =   120
      TabIndex        =   4
      Top             =   120
      Width           =   975
   End
   Begin VB.Label Version 
      Caption         =   "Version"
      Height          =   255
      Left            =   120
      TabIndex        =   3
      Top             =   960
      Width           =   1815
   End
   Begin VB.Label SerialNumber 
      Caption         =   "Serial Number"
      Height          =   375
      Left            =   120
      TabIndex        =   2
      Top             =   720
      Width           =   1815
   End
   Begin VB.Label DeviceNameLabel 
      Caption         =   "Device Name"
      Height          =   495
      Left            =   120
      TabIndex        =   1
      Top             =   360
      Width           =   6735
   End
End
Attribute VB_Name = "MainForm"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = False
' Delcom USB IO 64 Bit Read & Write example code
' MainForm 0.1 04/28/2008
' Delcom Engineering Copyright 2003  - www.delcom-eng.com
' This code makes function calls to the VB_BAS.bas file.
' Release Notes:
' V0.1 02/10/02 - Initial Release




' Closes the device on exit
Private Sub ExitButton_Click()
Dim Status As Boolean
Status = CloseDevice()      ' close device

End
End Sub

' Initialize the program
Private Sub Form_Load()
Dim Status As Long
Dim Packet As PacketStructure
Dim Ret As RetPacketStructure

Status = OpenDevice()       ' Gets the device name and opens the device

If Status = 0 Then          ' Check for errors
    Status = CloseDevice()  ' if errors exit
    End
Else
    DeviceNameLabel.Caption = VB_USB.lpDeviceName ' Displays the device Name
    Packet.MajorCmd = 11
    Packet.MinorCmd = 10
    Packet.DataLSB = 0
    Packet.DataMSB = 0
    Packet.Length = 0
    Ret = SendPacket(Packet) ' Get the Version infomation
    SerialNumber.Caption = "SerialNumber: " & ((Ret.B3 * &H1000000) + (Ret.B2 * &H10000) + (Ret.B1 * &H100) + (Ret.B0))
    Version.Caption = "Version: " & Ret.B4 & "  " & Ret.B6 & "/" & Ret.B5 & "/" & (2000 + Ret.B7)
    If (CInt(Ret.B4) >= 10) Then
        WR2RD8.Enabled = True
    End If
    
    
End If

'Timer1.Interval = 100       ' Set timer to 100 mSecond interval
'Timer1.Enabled = True       ' Enable the timer
End Sub




' Read 64 bit io with command 11-17
Private Sub Read_Click()

On Error GoTo ERROR_HANDLER

Dim Packet As PacketStructure
Dim Ret As RetPacketStructure
    
    Packet.MajorCmd = 11
    Packet.MinorCmd = 17
    Packet.Length = 8
    Ret = SendPacket(Packet)  ' Send the Packet

    RDB.Item(0) = Ret.B0
    RDB.Item(1) = Ret.B1
    RDB.Item(2) = Ret.B2
    RDB.Item(3) = Ret.B3
    RDB.Item(4) = Ret.B4
    RDB.Item(5) = Ret.B5
    RDB.Item(6) = Ret.B6
    RDB.Item(7) = Ret.B7
    
    
Exit Sub                            ' Exit Sub
ERROR_HANDLER:
    MsgBox "Read Error #" & Str$(Err) & " : " & Error & Chr(13)

End Sub


' Write 2 bytes & read 8 bytes using command 11-18
Private Sub WR2RD8_Click()
On Error GoTo ERROR_HANDLER

Dim Packet As PacketStructure
Dim Ret As RetPacketStructure
    
    Packet.MajorCmd = 11
    Packet.MinorCmd = 18
    Packet.Length = 8
    Packet.DataLSB = CInt(WRB.Item(0))
    Packet.DataMSB = CInt(WRB.Item(1))
   
    Ret = SendPacket(Packet)  ' Send the Packet
    RDB.Item(0) = Ret.B0
    RDB.Item(1) = Ret.B1
    RDB.Item(2) = Ret.B2
    RDB.Item(3) = Ret.B3
    RDB.Item(4) = Ret.B4
    RDB.Item(5) = Ret.B5
    RDB.Item(6) = Ret.B6
    RDB.Item(7) = Ret.B7
    
    
Exit Sub                            ' Exit Sub
ERROR_HANDLER:
    MsgBox "WR2B RD8B ERROR #" & Str$(Err) & " : " & Error & Chr(13)


End Sub

' write 8byte to command 10-17
Private Sub Write_Click()


Dim Packet As PacketStructure
Dim Ret As RetPacketStructure
    Packet.MajorCmd = 10
    Packet.MinorCmd = 17
    Packet.Length = 8
    Packet.DataExt(0) = CInt(WRB.Item(0))
    Packet.DataExt(1) = CInt(WRB.Item(1))
    Packet.DataExt(2) = CInt(WRB.Item(2))
    Packet.DataExt(3) = CInt(WRB.Item(3))
    Packet.DataExt(4) = CInt(WRB.Item(4))
    Packet.DataExt(5) = CInt(WRB.Item(5))
    Packet.DataExt(6) = CInt(WRB.Item(6))
    Packet.DataExt(7) = CInt(WRB.Item(7))
  Ret = SendPacket(Packet)  ' Send the Packet



End Sub
