#!/bin/bash
#cd $HOME/contrib/pi4dec_frituur_resources/
cd $HOME/git/pi4dec_frituur/
pwd
python3 ./contrib/pi4dec_frituur_resources/pi4dec_frituur.py  "$(<./contrib/pi4dec_frituur_resources/example.json)"
