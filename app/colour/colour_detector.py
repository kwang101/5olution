import smbus
import time

rgb_converter = 256
bus = None

# Inspired by Brad Berkland
def get_bus():
	if bus is not None:
		return bus
	bus = smbus.SMBus(1)
	bus.write_byte(0x29,0x80|0x12)
	ver = bus.read_byte(0x29)
	if ver == 0x44:
	    bus.write_byte(0x29, 0x80|0x00) # 0x00 = ENABLE register
	    bus.write_byte(0x29, 0x01|0x02) # 0x01 = Power on, 0x02 RGB sensors enabled
	    bus.write_byte(0x29, 0x80|0x14) # Reading results start register 14, LSB then MSB
	else: 
    	raise ValueError("Version is incorrect")
    return bus

def convert_colours(clear, red, green, blue):
    red = (float(red)/clear)*rgb_converter
    green = (float(green)/clear)*rgb_converter
    blue = (float(blue)/clear)*rgb_converter
    return (red,green,blue)

def get_colours():
    data = get_bus().read_i2c_block_data(0x29, 0)
    clear = clear = data[1] << 8 | data[0]
    red = data[3] << 8 | data[2]
    green = data[5] << 8 | data[4]
    blue = data[7] << 8 | data[6]
    return convert_colours(clear,red,green,blue)