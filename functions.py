import dataclasses
import random
import struct

from const_vars import FIRMWARE_VERSION_LIST, EEPROM_SIZE
import serial_utils
import serial.tools.list_ports
from logger import log
import tkinter as tk
from tkinter import messagebox, ttk
from resources import tone, font

@dataclasses.dataclass
class SerialPortCheckResult:
    status: bool
    message: str
    firmware_version: int
    eeprom_size: int


def get_all_serial_port():
    ports = serial.tools.list_ports.comports()
    ports = [port.device for port in ports]
    log('可用串口: ' + str(ports))
    return ports


def serial_port_combo_postcommand(combo: ttk.Combobox):
    combo['values'] = get_all_serial_port()

def read_eeprom(serial_port: serial.Serial, window: tk.Tk, target_eeprom_offset):
    with serial.Serial(serial_port, 38400, timeout=2) as serial_port:
        total_steps = target_eeprom_offset // 128
        current_step = 0
        addr = 0x0
        offset = 0x0
        with open('eeprom.bin', 'wb') as fp:
            while addr < target_eeprom_offset:
                if addr - offset * 0x10000 >= 0x10000:
                    offset += 1
                read_write_data = serial_utils.read_extra_eeprom(serial_port, offset, addr - offset * 0x10000, 128)
                fp.write(read_write_data)
                addr += 128
                current_step += 1
                percent_float = (current_step / total_steps) * 100
                log(f'进度: {percent_float:.1f}%, addr={hex(addr)}', '')
                window.update()
        return True
    return False

def check_serial_port(serial_port: serial.Serial) -> SerialPortCheckResult:
    try:
        version = serial_utils.sayhello(serial_port)
        eeprom_size = 0
        if version.startswith('LOSEHU'):
            firmware_version = 0
            if version.endswith('K') or version.endswith('H'):
                firmware_version = 1
        else:
            firmware_version = 2

        msg = f'串口连接成功！\n版本号: {version}\n自动检测结果如下:\n固件版本: {FIRMWARE_VERSION_LIST[firmware_version]}\n'
        return SerialPortCheckResult(True, msg, firmware_version, eeprom_size)
    except Exception as e:
        msg = '串口连接失败！<-' + str(e)
        log(msg)
        return SerialPortCheckResult(False, msg, 2, 0)


def serial_port_combo_callback(_, serial_port: str, status_label: tk.Label):
    status_label['text'] = '当前操作: 检查串口连接'
    with serial.Serial(serial_port, 38400, timeout=2) as serial_port:
        serial_check = check_serial_port(serial_port)
        if serial_check.status:
            messagebox.showinfo('提示', serial_check.message)
        else:
            messagebox.showerror('错误', serial_check.message)
    status_label['text'] = '当前操作: 无'
