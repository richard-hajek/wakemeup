#!/usr/bin/env bash

feh "$1" &
sleep 10
killall feh
rm "$1"
