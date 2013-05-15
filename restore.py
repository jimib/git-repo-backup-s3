#! /usr/bin/python

import os, tarfile

from boto.s3.connection import S3Connection
from boto.s3.key import Key

AWS_KEY = "<AWS_KEY>"
AWS_SECRET = "<AWS_SECRET>"
bucketName = 'jimib-backups'
pathRootRepository = '/home/git/repositories'
pathRootUpload = 'rpi-git'
pathRootCache = '/home/git/s3-cache'

def percent_cb(complete, total):
	# pass
	print complete, total

print 'Connecting to S3...'

#open connection to S3
conn = S3Connection(AWS_KEY, AWS_SECRET)
print 'Connected to S3...'

#link to bucket
print 'Open bucket "' + bucketName + '"...'
bucket = conn.get_bucket(bucketName)
print 'Opened bucket "' + bucketName + '"...'

#download the root dir on bucket to our repository
def downloadDir(bucket, dirBucket, dirCache, dirRepo):
	result = bucket.list(dirBucket)
	for key in result:
		#try:
			path = key.name
			if path.find(dirBucket) > -1:
				path = path[len(dirBucket) + 1:]
		
			fullpath = os.path.join(dirCache, path)
			dirpath = os.path.dirname(fullpath)
			#if directory doesn't exist make it
			if not os.path.exists(dirpath):
				os.makedirs(dirpath)			

			if not os.path.exists(fullpath):
				print "download:" + path
	        		res = key.get_contents_to_filename(fullpath)
				print "downloaded: "+path
			else:
				print "skipped: "+path

			#check the repository and if it doesn't exist unzip 
			#from the cache 
			fullpathrepo = os.path.join(dirRepo, path)

			if not os.path.exists(fullpathrepo):
				dirpathrepo = os.path.dirname(fullpathrepo)

				if not os.path.exists(dirpathrepo):
					os.makedirs(dirpathrepo)

				#unzip it
				tfile = tarfile.open(fullpath)
 
				if tarfile.is_tarfile(fullpath):
					tfile = tarfile.open(fullpath)
					# extract all contents
	    				tfile.extractall(fullpathrepo)

		#except:
		#	print(key.name+":"+"FAILED")

downloadDir(bucket, pathRootUpload, pathRootCache, pathRootRepository)
