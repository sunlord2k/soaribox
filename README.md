# soaribox
SW &amp; HW for Soaribox
123

# Install process (only for raspbian):
Generate a fresh install of raspbian
Do no start the SoariBox, but do this on the SD-Card:

cd /home/pi
git clone https://github.com/sunlord2k/soaribox

Add the following line to /etc/rc.local
sudo bash -c '/usr/bin/python3 /home/pi/soaribox/install.py > /home/pi/soaribox/install.log 2>&1' &

maybe try this on rc.local(works but no real logging):
sudo bash -c '/usr/bin/python3 /home/pi/soaribox/install.py | tee -a /home/pi/soaribox/install.log 2>&1' &

Next try with cronjob:



This is for later:

cd /home/pi/soaribox/dum1090

sudo dpkg -i dump1090-mutability_1.14_armhf.deb

In addition lighttpd webserver has to be installed!!!
All files from /etc/soaribox/dump1090/dump1090_thml go to /var/www/html/dump1090
Config file for lighttpd goes from /etc/soaribox/dump1090/89.... to /etc/lighttpd/conf-enabled



# Pathes & things to know:


Status of dump1090 can be obtained via systemctl dump1090

jsoncopy takes care of feeding dump1090 Data to SoftRF
