
# Pi Backup Box

A cheap box to backup your sd cards on the go!

Heavily inspired by [Little Backup Box](https://github.com/dmpop/little-backup-box), but written in python.

## Installation
On a raspberry pi, do
```
cd ~
git clone https://github.com/harin/pi-backup-box
```

Add the script to crontab by running `crontab -e` then add this line to the bottom
```
@reboot python3 /home/pi/pi_backup_box/sd_card_backup.py &
```