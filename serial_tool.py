import argparse
import sys
import threading
import time
from datetime import datetime

import serial
from serial.tools import list_ports


def list_serial_ports():
    ports = list(list_ports.comports())
    if not ports:
        print("No serial ports found.")
        return

    for port in ports:
        desc = port.description or "Unknown device"
        hwid = port.hwid or "No hardware id"
        print(f"{port.device}\t{desc}\t{hwid}")


def parse_hex_bytes(text):
    compact = text.replace(" ", "").replace(",", "")
    if len(compact) % 2 != 0:
        raise ValueError("hex data length must be even")
    return bytes.fromhex(compact)


def timestamp():
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]


def reader_loop(port, stop_event):
    while not stop_event.is_set():
        try:
            data = port.read(port.in_waiting or 1)
        except serial.SerialException as exc:
            print(f"\n[error] read failed: {exc}")
            stop_event.set()
            return

        if data:
            hex_view = " ".join(f"{byte:02X}" for byte in data)
            try:
                text_view = data.decode("utf-8", errors="replace")
            except UnicodeDecodeError:
                text_view = ""
            print(f"\n[{timestamp()}] RX HEX: {hex_view}")
            if text_view:
                print(f"[{timestamp()}] RX TXT: {text_view}", end="" if text_view.endswith("\n") else "\n")


def open_serial(args):
    return serial.Serial(
        port=args.port,
        baudrate=args.baudrate,
        bytesize=args.bytesize,
        parity=args.parity,
        stopbits=args.stopbits,
        timeout=0.1,
    )


def run_terminal(args):
    stop_event = threading.Event()

    try:
        with open_serial(args) as port:
            print(f"Opened {args.port} at {args.baudrate} baud.")
            print("Type text and press Enter to send. Type /hex 01 02 0A to send hex. Type /quit to exit.")

            reader = threading.Thread(target=reader_loop, args=(port, stop_event), daemon=True)
            reader.start()

            while not stop_event.is_set():
                try:
                    line = input("> ")
                except (EOFError, KeyboardInterrupt):
                    break

                if line.strip().lower() in {"/quit", "/exit"}:
                    break

                try:
                    if line.startswith("/hex "):
                        payload = parse_hex_bytes(line[5:])
                    else:
                        payload = (line + ("\n" if args.append_newline else "")).encode(args.encoding)
                    port.write(payload)
                    port.flush()
                    print(f"[{timestamp()}] TX {len(payload)} bytes")
                except (ValueError, UnicodeEncodeError, serial.SerialException) as exc:
                    print(f"[error] send failed: {exc}")

    except serial.SerialException as exc:
        print(f"[error] cannot open serial port: {exc}", file=sys.stderr)
        return 1
    finally:
        stop_event.set()
        time.sleep(0.15)

    return 0


def build_parser():
    parser = argparse.ArgumentParser(description="Simple serial communication tool.")
    parser.add_argument("--list", action="store_true", help="list available serial ports")
    parser.add_argument("-p", "--port", help="serial port name, for example COM3 or /dev/ttyUSB0")
    parser.add_argument("-b", "--baudrate", type=int, default=115200, help="baud rate, default: 115200")
    parser.add_argument("--bytesize", type=int, choices=[5, 6, 7, 8], default=8, help="data bits")
    parser.add_argument("--parity", choices=["N", "E", "O", "M", "S"], default="N", help="parity")
    parser.add_argument("--stopbits", type=float, choices=[1, 1.5, 2], default=1, help="stop bits")
    parser.add_argument("--encoding", default="utf-8", help="text encoding for transmitted text")
    parser.add_argument("--append-newline", action="store_true", help="append LF when sending text lines")
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.list:
        list_serial_ports()
        return 0

    if not args.port:
        parser.error("--port is required unless --list is used")

    return run_terminal(args)


if __name__ == "__main__":
    raise SystemExit(main())
