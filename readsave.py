import os, itertools
#from google.appengine.ext import ndb

FILENAME = 'tweets.txt'


def isa_group_separator(line):
	return line=='\n'

with open(FILENAME, 'r') as fp:
	for key,group in itertools.groupby(fp, isa_group_separator):
		#print(key, list(group))
		if not key:
			for item in group:
				field,value = item.split('=:')
				value = value.strip()
				#print field + '!!!!!!' + value
			print '\n'



