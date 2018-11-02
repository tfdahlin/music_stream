import datetime

class Log:
    def __init__(self):
        pass

    def logMissingArtwork(context):
        string = "Missing artwork.\n"
        if(context['song'] != None):
            string += "Song: " + context['song'] + "\n"
        if(context['artist'] != None):
            string += "Artist: " + context['artist'] +"\n"
        if(context['album'] != None):
            string += "Album: " + context['album']
        print(string)
        
    def logLogin(context):
        print("Login by user: " + context['username'])
        
    def logLogout(context):
        print("Logout by user: " + context['username'])
        
    def logMissingInfo(context):
        print("Missing info: " + context)
        
    def logUpdateStart():
        print("Updating database... [" + str(datetime.datetime.now())+"]")
        
    def logUpdateFinished():
        print("Database updated [" + str(datetime.datetime.now())+"]")
        
    def attemptedSQLInjection(context):
        print("===========Attempted SQL Injection===========")
        print("User " + context['username'] + " input invalid request with value " + str(context['value']))
        
    def logFileMissing(context):
        print("File is missing: " + context['filename'])