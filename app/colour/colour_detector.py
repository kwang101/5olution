import smbus
import time
import colour
import datetime

rgb_converter = 256
max_register_diff = 1

# Inspired by Brad Berkland
def get_bus():
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

def convert_rgb_values(clear, red, green, blue):
    red = (float(red)/clear)*rgb_converter
    green = (float(green)/clear)*rgb_converter
    blue = (float(blue)/clear)*rgb_converter
    return (red,green,blue)

def get_current_rgb_values(bus):
    data = bus.read_i2c_block_data(0x29, 0)
    clear = clear = data[1] << 8 | data[0]
    red = data[3] << 8 | data[2]
    green = data[5] << 8 | data[4]
    blue = data[7] << 8 | data[6]
    return convert_rgb_values(clear,red,green,blue)

def get_current_colour(bus):
    current_values = get_current_rgb_values(bus)
    return colour.Colour(values[0], values[1], values[2])

def get_average(c0,c1,c2):
    red = (c0.red+c1.red+c2.red)/3
    green = (c0.green+c1.green+c2.green)/3
    blue = (c0.blue+c1.blue+c2.blue)/3
    return colour.Colour(red,green,blue)

def register_item(bus):
    colours = []
    normal_colour = get_current_colour(bus)
    for _ in range(20):
        colours.append(get_current_colour(bus))
        if len(colours) > 2:
            c0 = colours[len(colours)-1]
            c1 = colours[len(colours)-2]
            c2 = colours[len(colours)-3]
            average = get_average(c0,c1,c2)
            # Check that the colour is different from the normal colour
            if colour.get_difference(average, normal_colour) > max_register_diff:
                # Check that the three values are close enough, i.e. that the item stopped moving
                if (colour.get_difference(c0, c1) < max_register_diff) and (colour.get_difference(c1, c2) < max_register_diff):
                    return average
            colours.pop(0)
        time.sleep(1)
    return -1

def item_is_locked_in(bus, colour, endtime):
    while datetime.now() < endtime:
        if not colour.equals(get_current_colour(bus), colour):
            return False
    return True

