from twython import Twython, TwythonStreamer
import os, time

APP_KEY = ' ENTER_YOUR_APP_KEY '
APP_SECRET = ' ENTER_YOUR_APP_SECRET '
ACCESS_TOKEN = ' ENTER_YOUR_ACCESS_TOKEN '
ACCESS_TOKEN_SECRET = ' ENTER_YOUR_TOKEN_SECRET '
FILE_NAME = 'data/vettel'

class MyStreamer(TwythonStreamer):
    def on_success(self, data):
		savefile = open(FILE_NAME, 'a+')
		statinfo = os.stat(FILE_NAME)
		if statinfo.st_size < 1000000:
			try:
				print data['coordinates']['coordinates']
				print statinfo.st_size
				try:
					data['text'].encode('utf-8')
					savefile.write('username=:'+data['user']['name'] + '\n')
					savefile.write('screenname=:'+data['user']['screen_name'] + '\n')
					text = data['text'].encode('utf-8')
					finaltext = text.replace('\n', '\t')
					savefile.write('text=:'+finaltext + '\n')
					savefile.write('time=:' + data['created_at'] + '\n')
					savefile.write('longitude=:'+str(data['coordinates']['coordinates'][0]) + '\n')
					savefile.write('latitude=:'+str(data['coordinates']['coordinates'][1]) + '\n')
					savefile.write('\n')
					
					#print data['text']
				except:
					print 'text not encodable'
			except:
				print 'No coordinates'
		else:
			self.disconnect()
		savefile.close()

    def on_error(self, status_code, data):
        print status_code
        self.disconnect()


stream = MyStreamer(APP_KEY, APP_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
stream.statuses.filter(track='sebastian vettel', locations='-180,-90,180,90')
