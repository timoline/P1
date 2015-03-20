#!/bin/sh
# p1.sh
# navigate to www directory

P1_FOLDER=/var/www/p1

cd "${P1_FOLDER}"
sudo python3 "${P1_FOLDER}/P1.py" -c 1 -v4 -o json
cd / 