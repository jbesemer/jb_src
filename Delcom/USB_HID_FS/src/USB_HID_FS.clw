; CLW file contains information for the MFC ClassWizard

[General Info]
Version=1
LastClass=CUSB_HID_FSDlg
LastTemplate=CDialog
NewFileInclude1=#include "stdafx.h"
NewFileInclude2=#include "USB_HID_FS.h"

ClassCount=3
Class1=CUSB_HID_FSApp
Class2=CUSB_HID_FSDlg
Class3=CAboutDlg

ResourceCount=3
Resource1=IDD_ABOUTBOX
Resource2=IDR_MAINFRAME
Resource3=IDD_USB_HID_FS_DIALOG

[CLS:CUSB_HID_FSApp]
Type=0
HeaderFile=USB_HID_FS.h
ImplementationFile=USB_HID_FS.cpp
Filter=N

[CLS:CUSB_HID_FSDlg]
Type=0
HeaderFile=USB_HID_FSDlg.h
ImplementationFile=USB_HID_FSDlg.cpp
Filter=D
BaseClass=CDialog
VirtualFilter=dWC
LastObject=IDCANCEL

[CLS:CAboutDlg]
Type=0
HeaderFile=USB_HID_FSDlg.h
ImplementationFile=USB_HID_FSDlg.cpp
Filter=D

[DLG:IDD_ABOUTBOX]
Type=1
Class=CAboutDlg
ControlCount=5
Control1=IDC_STATIC,static,1342177283
Control2=IDC_STATIC,static,1342308480
Control3=IDC_STATIC,static,1342308352
Control4=IDOK,button,1342373889
Control5=IDC_STATIC,static,1342308352

[DLG:IDD_USB_HID_FS_DIALOG]
Type=1
Class=CUSB_HID_FSDlg
ControlCount=7
Control1=IDOK,button,1073807361
Control2=IDCANCEL,button,1342242816
Control3=IDC_Version,static,1342308352
Control4=IDC_STATIC,static,1342308352
Control5=IDC_STATIC,static,1342308352
Control6=IDC_CHECK0,button,1342242819
Control7=IDC_CHECK1,button,1342242819

