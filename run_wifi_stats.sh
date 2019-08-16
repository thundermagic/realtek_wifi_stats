#!/bin/bash

# Copy this file to /usr/local/bin and make is executable

while true
    do
        cd /home/dietpi/realtek_wifi_stats
        python3 wifi_stat.py $1 $2 > /textfile_collector_result/wifi_stats.tmp
        mv /textfile_collector_result/wifi_stats.tmp /textfile_collector_result/wifi_stats.prom
        sleep 10
    done