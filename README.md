# music_stream
## Overview
A Django web application for dynamically serving music. Originally designed so that I could share my music collection with my family without needing to keep putting it on flash drives for them, it became a bit of a pet project so I could have something to showcase for job applications.

## Dependencies
### Mandatory dependencies
1. Python3 (https://www.python.org/)
   Written for Python3
2. eyeD3 (https://eyed3.readthedocs.io/en/latest/)
   MP3 file processing, might be able to remove one or the other
3. mutagen (https://mutagen.readthedocs.io/en/latest/)
   MP3 file processing, might be able to remove one or the other

### Optional dependencies
1. wakeonlan (https://pypi.org/project/wakeonlan/)
   Specific use-case where the music file host goes to sleep sometimes
2. Pillow (https://pillow.readthedocs.io/en/5.3.x/)
   Specific use-case for converting .webp album artwork to .png to serve the file
