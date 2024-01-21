import sys
import tkinter as tk
from tkinter import ttk
from const_vars import FIRMWARE_VERSION_LIST, EEPROM_SIZE
from logger import log

from functions import serial_port_combo_postcommand, serial_port_combo_callback, read_eeprom

window = tk.Tk()
version = '0.1'


class TextRedirector(tk.Text):
    def __init__(self, widget):
        super().__init__()
        self.widget = widget

    def write(self, strs):
        self.widget.insert(tk.END, strs)
        self.widget.see(tk.END)

    def flush(self):
        pass


def main():
    window.title(f'K5/K6 备份工具 v{version}')
    window.geometry('420x340')
    label1 = tk.Label(window, text=f'K5/K6 备份工具 v{version} (BG4IST & BD8DFN)')
    label1.place(x=10, y=10)

    label2 = tk.Label(window, text='当前操作: 无')
    label2.place(x=10, y=30)

    serial_port_label = tk.Label(window, text='串口')
    serial_port_label.place(x=10, y=60)
    serial_port_combo = ttk.Combobox(window, values=[], width=8, state='readonly')
    serial_port_combo.place(x=40, y=60)

    serial_port_combo['postcommand'] = lambda: serial_port_combo_postcommand(serial_port_combo)
    serial_port_combo.bind(
        '<<ComboboxSelected>>',
        lambda event: serial_port_combo_callback(event, serial_port_combo.get(), label2)
    )

    read_eeprom_button = tk.Button(
        window,
        text='读取EEPROM（8K）',
        command=lambda: read_eeprom(serial_port_combo.get(), window, 8192)
    )
    read_eeprom_button.place(x=10, y=100)

    write_font_old_button = tk.Button(
        window,
        text='读取EEPROM（128K）',
        command=lambda: read_eeprom(serial_port_combo.get(), window, 131072)
    )
    write_font_old_button.place(x=150, y=100)

    write_font_new_button = tk.Button(
        window,
        text='读取EEPROM（256K）',
        command=lambda: read_eeprom(serial_port_combo.get(), window, 262144)
    )
    write_font_new_button.place(x=10, y=140)

    textbox = tk.Text(window, width=56, height=10)
    textbox.place(x=10, y=185)
    sys.stdout = TextRedirector(textbox)

    log(f'K5/K6 备份工具 v{version} BG4IST & BD8DFN\n')

    window.mainloop()


if __name__ == '__main__':
    main()
