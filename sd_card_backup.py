import time
import subprocess

from board import SCL, SDA
import busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
from pathlib import Path
from datetime import datetime
import uuid

        # Shell scripts for system monitoring from here:
        # https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load
        # cmd = "hostname -I | cut -d\' \' -f1"
        # IP = subprocess.check_output(cmd, shell=True).decode("utf-8")
        # cmd = "top -bn1 | grep load | awk '{printf \"CPU Load: %.2f\", $(NF-2)}'"
        # CPU = subprocess.check_output(cmd, shell=True).decode("utf-8")
        # cmd = "free -m | awk 'NR==2{printf \"Mem: %s/%s MB  %.2f%%\", $3,$2,$3*100/$2 }'"
        # MemUsage = subprocess.check_output(cmd, shell=True).decode("utf-8")
        # cmd = "df -h | awk '$NF==\"/\"{printf \"Disk: %d/%d GB  %s\", $3,$2,$5}'"
        # Disk = subprocess.check_output(cmd, shell=True).decode("utf-8")

class Display:
    def __init__(self, disp):
        self.disp = disp
        self.font = ImageFont.load_default()


    def _reset(self, draw):
        self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)

    def print(self, text):
        # self._reset()

        padding = -2
        top = padding
        bottom = self.disp.height-padding

        image = Image.new('1', (self.disp.width, self.disp.height))
        draw = ImageDraw.Draw(image)

        lines = text.split('\n')

        i = 0
        screen_width = 20
        while lines:
            line = lines.pop(0)
            if len(line) > screen_width:
                line, next_line = line[:screen_width], line[screen_width:]
                lines.insert(0, next_line)

            line_offset = i * 8
            draw.text((0, top+line_offset), line, font=self.font, fill=255) 
            i += 1

        self.disp.image(image)
        self.disp.show()

if __name__ == '__main__':
    # Create the I2C interface.
    i2c = busio.I2C(SCL, SDA)

    # Create the SSD1306 OLED class.
    # The first two parameters are the pixel width and pixel height.  Change these
    # to the right size for your display!
    disp = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)

    disp.fill(0)
    disp.show()
    d = Display(disp)

    state = 0
    card_location = None

    while True:
        if state == 0:
            d.print('Looking for backup device...')
            if list(Path('/media/backup').glob('*')):
                state += 1
                time.sleep(2)
        elif state == 1:
            d.print('Found backup device!\n Looking waiting for card to backup.')
            if list(Path('/media/card').glob('*')):
                state += 1
                continue

            paths = list(filter(lambda p: p.stem !='sda1', Path('/dev/').glob('sd*1')))
            if paths:
                card_location = paths[0]
                try:
                    output = subprocess.check_output(f'sudo mount -t exfat {str(card_location)} /media/card', shell=True).decode("utf-8") 
                    print(output)
                    print(Path('/media/card/').glob('*'))
                    state += 1
                except subprocess.CalledProcessError:
                    d.print('Failed to mount card')
 

        elif state == 2:
            d.print('Found card to backup!\n\n')
            card_id = None
            id_candidates = list(Path('/media/card').glob('*.id'))
            if id_candidates:
                card_id = id_candidates[0].stem
            else:
                card_id = str(uuid.uuid1())
                open(f'/media/card/{card_id}.id', 'a+').close()

            
            try:
                subprocess.check_output(f'mkdir -p /media/backup/{card_id}', shell=True).decode('utf-8')
                output = subprocess.check_output(f'sudo rsync -avh /media/card/  /media/backup/{card_id}', shell=True).decode("utf-8") 
                print(output)
                state += 1
            except subprocess.CalledProcessError:
                d.print('Failed to backup card')
        elif state == 3:
            d.print('Done!')

        time.sleep(.1)

# /dev/mmcblk0p1: LABEL_FATBOOT="boot" LABEL="boot" UUID="5203-DB74" TYPE="vfat" PARTUUID="6c586e13-01"
# /dev/mmcblk0p2: LABEL="rootfs" UUID="2ab3f8e1-7dc6-43f5-b0db-dd5759d51d4e" TYPE="ext4" PARTUUID="6c586e13-02"
# /dev/sda1: LABEL="Extreme SSD" UUID="76DD-4B90" TYPE="exfat" PARTUUID="001b675f-01"
# /dev/sdb1: TYPE="exfat"