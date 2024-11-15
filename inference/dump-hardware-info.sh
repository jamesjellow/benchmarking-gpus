sudo apt install inxi libjson-xs-perl -y
inxi -Fxz > hardware.txt
inxi -Fxz --output json --output-file $HOME/hardware.json