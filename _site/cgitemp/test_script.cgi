#!/bin/bash
# get today’s date
OUTPUT="$(date)"
# You must add following two lines before
# outputting data to the web browser from shell
# script
echo "Content-type: text/html"
echo ""
echo "<html><head><title>Demo</title></head><body>"
echo "Today is $OUTPUT <br>"
echo "You can do anything with this Schell Script:) "
echo "Good Luck!"
echo "</body></html>"
