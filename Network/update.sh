#!/bin/sh

#echo 'Update network'
#python network.py

echo 'Convert bot to csv '
python bot_detect.py

cd BotDetection
echo 'Bot info update'
python BotDetection.py
cd ..

echo 'Update bot, cascade info'
python graph_info.py update

echo 'Polarization update'
Rscript user_polarization.R
cd PolarResult
python convert.py
cd ..


