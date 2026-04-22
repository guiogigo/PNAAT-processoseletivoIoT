import time
from machine import I2C

class I2cLcd:
    def __init__(self, i2c, i2c_addr, num_lines, num_columns):
        self.i2c = i2c
        self.i2c_addr = i2c_addr
        self.num_lines = num_lines
        self.num_columns = num_columns
        self.backlight = 0x08
        
        time.sleep(0.05)
        self.hal_write_command(0x33)
        time.sleep(0.005)
        self.hal_write_command(0x32)
        time.sleep(0.001)
        self.hal_write_command(0x28)
        self.hal_write_command(0x0C) 
        self.hal_write_command(0x06) 
        self.clear()

    def hal_write_command(self, cmd):
        """Envia um comando para o LCD."""
        self.i2c.writeto(self.i2c_addr, bytes([cmd & 0xF0 | self.backlight | 0x04]))
        self.i2c.writeto(self.i2c_addr, bytes([cmd & 0xF0 | self.backlight]))
        self.i2c.writeto(self.i2c_addr, bytes([(cmd << 4) & 0xF0 | self.backlight | 0x04]))
        self.i2c.writeto(self.i2c_addr, bytes([(cmd << 4) & 0xF0 | self.backlight]))

    def hal_write_data(self, data):
        """Envia um caractere para ser escrito no LCD."""
        self.i2c.writeto(self.i2c_addr, bytes([data & 0xF0 | self.backlight | 0x05]))
        self.i2c.writeto(self.i2c_addr, bytes([data & 0xF0 | self.backlight | 0x01]))
        self.i2c.writeto(self.i2c_addr, bytes([(data << 4) & 0xF0 | self.backlight | 0x05]))
        self.i2c.writeto(self.i2c_addr, bytes([(data << 4) & 0xF0 | self.backlight | 0x01]))

    def clear(self):
        """Limpa o display."""
        self.hal_write_command(0x01)
        self.hal_write_command(0x02)
        time.sleep(0.005)
        
    def backlight_on(self):
        """Acende a luz de fundo."""
        self.backlight = 0x08
        self.hal_write_command(0)

    def backlight_off(self):
        """Apaga a luz de fundo."""
        self.backlight = 0x00
        self.hal_write_command(0)

    def putstr(self, string):
        """Escreve uma string no display."""
        for char in string:
            if char == '\n':
                self.hal_write_command(0xC0) 
            else:
                self.hal_write_data(ord(char))