# 串口通信工具

这是一个简单的 Python 串口通信程序，用于电脑和单片机、传感器模块、串口转 USB 模块之间进行收发调试。

## 功能

- 枚举当前电脑可用串口。
- 打开指定串口并持续接收数据。
- 支持发送普通文本。
- 支持发送十六进制数据。
- 接收数据同时显示文本和 HEX 格式。

## 环境要求

- Python 3.9 或更新版本。
- `pyserial` 依赖库。

安装依赖：

```bash
pip install -r requirements.txt
```

## 使用方法

查看可用串口：

```bash
python serial_tool.py --list
```

打开串口：

```bash
python serial_tool.py --port COM3 --baudrate 115200
```

Linux 示例：

```bash
python serial_tool.py --port /dev/ttyUSB0 --baudrate 115200
```

发送普通文本：

```text
hello
```

发送十六进制数据：

```text
/hex 01 03 00 00 00 02 C4 0B
```

退出程序：

```text
/quit
```

## 常见问题

- 如果提示串口打不开，请确认串口号正确，并关闭其他正在占用串口的软件。
- 如果接收乱码，请确认波特率、数据位、校验位、停止位和设备端配置一致。
- 如果需要每次文本发送自动追加换行，可以添加 `--append-newline` 参数。

## 示例

```bash
python serial_tool.py --port COM3 --baudrate 9600 --append-newline
```
