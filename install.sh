#!/bin/bash

echo "This program requires mongodb. Do you have it? Or it can be installed automaticly? [y/n/install]"
read item
case "$item" in
	y|Y) echo "OK!";;
	n|N) echo "instructions for installing mongodb can be found at https://docs.mongodb.com/v4.0/tutorial/install-mongodb-on-ubuntu/"
		exit 0;;
	install|Install|INSTALL) echo "It will install the latest wersion of mongodb"
		sudo apt install mongodb -y;;
	*) echo "Invalid answer"
		exit 0;;
esac		
echo "Installing python libraries"
sudo apt install python3-pip -y
pip3 install flask==1.1.1
pip3 install pycryptodome
pip3 install pymongo==3.10.0
pip3 install telebot
pip3 install pyTelegramBotApi==3.6.6
echo "Python libraries werw installed!"
echo "Generating secret key for flask sessions"
key=$(< /dev/urandom tr -dc _A-Z-a-z-0-9 | head -c${1:-32};echo;)
sed -e "s/secretkeydonthackplease/$key/" ./config.py | sudo tee ./config.py
echo "Key was generated. You can find it in config.py"


echo "The next step is to configurate database. All data in gorbin database in mongodb will be lost. Do you want to continue? [y/n]"
read item
case "$item" in
	y|Y) echo "Configuratiing database"
		python3 configure_db.py	
		echo "db was configurated!"	
		echo "Runing mongo_test2"
		python3 mongo_test2.py
		echo "The final cConfiguratiing database"
		python3 configure_db.py
		echo "db was finaly configurated!";;	
	n|N) echo "You can change the database name in config.py and then run mongo_test2.py"
	exit 0;;
	*) echo "Invalid answer"
		exit 0;;
esac




