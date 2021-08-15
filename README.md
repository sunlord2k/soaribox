# soaribox
SW &amp; HW for Soaribox
123

# Install process (only for raspbian):

cd /etc/

sudo git clone https://github.com/sunlord2k/soaribox

cd /etc/soaribox/dum1090

sudo dpkg -i dump1090-mutability_1.14_armhf.deb

In addition lighttpd webserver has to be installed!!!
All files from /etc/soaribox/dump1090/dump1090_thml go to /var/www/html/dump1090
Config file for lighttpd goes from /etc/soaribox/dump1090/89.... to /etc/lighttpd/conf-enabled

Probably some more stuff which I forgot but will be added to install.sh


# Pathes & things to know:

Logfiles: /etc/soaribox/soaribox.log

Status of dump1090 can be obtained via systemctl dump1090

jsoncopy takes care of feeding dump1090 Data to SoftRF
