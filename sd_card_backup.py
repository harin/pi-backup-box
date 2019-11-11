import time
import subprocess

from board import SCL, SDA
import busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
from pathlib import Path
from datetime import datetime
import uuid
from rsync_with_progress import rsync

class Display:
    def __init__(self, disp):
        self.disp = disp
        self.font = ImageFont.load_default()


    def _reset(self, draw):
        self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)

    def print(self, text):
        # self._reset()
        print('logging:', text)
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
        Path('/media/backup').mkdir(exist_ok=True)
        if state == 0:
            d.print('Looking for backup device...')
            # TODO: Improve check if backup device is found.

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
                rsync('/media/card/', f'/media/backup/{card_id}', d.print)
                state += 1
            except subprocess.CalledProcessError:
                d.print('Failed to backup card')
        elif state == 3:
            d.print('Done!')
            exit()

        time.sleep(.1)
