# Rivian_Shop_Monitor
Monitor the availability of a specific vehicle configuration. This helped me find my configuration so sharing it for others to see, modify, whatever. I know it's ugly but this was not intended to be used for long, just something quick and dirty to do a job.

# Support
None whatsoever. 

# How I ran this
Ubuntu 22.04, chrome webdriver, selenium, python 3, mailx, running in a terminal in a VNC session with `watch -n 600 ./rivian_shop_selenium_runner.sh`. VNC session was 1080p, you need some vertical resolution otherwise buttons overlap and selenium crashes.

# If you want to use this
Modify the python code to fit your preferred configuration options (lines 47-102). Read the text on the website and edit to fit your config, then run it to test.

# How it works
The filtering you would edit is pretty simple (lines 47-102)
1. Searches for a button with matching text and clicks it
2. Collapses a section when done
3. Scrolls down when needed to prevent buttons overlapping and selenium crashing
4. Clicks the show results button
5. Emails a screenshot if there are any vehicles listed

