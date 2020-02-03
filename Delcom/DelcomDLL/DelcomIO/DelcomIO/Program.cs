using System;
using System.Collections.Generic;
using System.Text;
using System.Timers;

namespace DelcomIO
{
    class Program
    {
        static uint hUSB;
        static byte PORT_LOW = 0xFF;    // input port must be driven low to sense pull-ups
        static byte LED_OFF = 0xFF;
        // static byte LED_ON  = 0x00;

        static void Main(string[] args)
        {
            int Result;
            StringBuilder DeviceName = new StringBuilder(Delcom.MAXDEVICENAMELEN);  
            
            // Serach for the first match USB device, For USB IO Chips use USBIODS
            Result = Delcom.DelcomGetNthDevice(Delcom.USBIODS, 0, DeviceName);

            if(Result == 0 ) {  // if not found, exit
                Console.WriteLine( "Device not found!\n" );
                return;
            }

            Console.WriteLine( "Delcom C# Example Program." );
            Console.WriteLine( "Device found: "+ DeviceName );

            // const int PORT0 = 0;    // Dip switches
            // const int PORT1 = 1;    // LEDs
            const int MILLISECONDS = 1;

            hUSB = Delcom.DelcomOpenDevice(DeviceName, 0);                   // open the device
            Delcom.DelcomWritePorts(hUSB, LED_OFF, LED_OFF);
//            SetupPort0();

            // Hook up the event handler for the Elapsed event.
            Timer Timer1 = new System.Timers.Timer(100 *MILLISECONDS );
            Timer1.Elapsed += new ElapsedEventHandler(OnTimer1);
            Timer1.AutoReset = true;
            Timer1.Enabled = true;

            Console.WriteLine("Press any key to exit the program.");
            Console.ReadKey();

            Delcom.DelcomWritePorts(hUSB, 0, LED_OFF);
            Delcom.DelcomCloseDevice(hUSB);                                  // close the device
        }

        static byte isOn = 0;
        // static byte LED0 = 0x01;
        static byte prevPort0 = 0;

        private static void OnTimer1(object source, ElapsedEventArgs e)
        {
            byte port0, port1;

            // Delcom.DelcomWritePorts(hUSB, 0, (byte)(LED_OFF ^ (LED0 * isOn)));
            Delcom.DelcomWritePin(hUSB, 1, 0, isOn);

            isOn ^= 0x01;

            Delcom.DelcomReadPorts(hUSB, out port0, out port1);

            if (port0 != prevPort0)
            {
                Console.WriteLine("Switches: {0:x} -> {1:x}", prevPort0, port0);
                prevPort0 = port0;
            }
        }

        private static void SendCmd(byte major, byte minor, byte msb, byte lsb)
        {
            Delcom.PacketStructure send = new Delcom.PacketStructure();
            Delcom.PacketStructure recv;

            send.Recipient = 8;
            send.DeviceModel = 18;
            send.MajorCmd = major;
            send.MinorCmd = minor;
            send.DataMSB = msb;
            send.DataLSB = lsb;
            send.Length = 0;

            Delcom.DelcomSendPacket(hUSB, ref send, out recv);
        }

        private static void SetupPort0()
        {
            // enable all port0 pull-ups
            SendCmd(10, 30, 0, 0);

            // set drive level for all port0 pins

            byte level = 15;    // I tried values of 0, 1, and 15

            for (byte pin = 0; pin < 8; pin++)
                SendCmd(10, 32, pin, level);
        }
    }
}
