# music_stream
## Overview
A Django web application for dynamically serving music. Originally designed so that I could share my music collection with my family without needing to keep putting it on flash drives for them, it became a bit of a pet project so I could have something to showcase for job applications.

## Dependencies
### Mandatory dependencies
Python3 (https://www.python.org/)</br>* Written for Python3
eyeD3 (https://eyed3.readthedocs.io/en/latest/)</br> * MP3 file processing, might be able to remove one or the other
mutagen (https://mutagen.readthedocs.io/en/latest/)</br> * MP3 file processing, might be able to remove one or the other

### Optional dependencies
wakeonlan (https://pypi.org/project/wakeonlan/)</br> * Specific use-case where the music file host goes to sleep sometimes
Pillow (https://pillow.readthedocs.io/en/5.3.x/)</br> * Specific use-case for converting .webp album artwork to .png to serve the file
