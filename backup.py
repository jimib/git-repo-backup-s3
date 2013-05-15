#! /usr/bin/python

import os, tarfile

from boto.s3.connection import S3Connection
from boto.s3.key import Key

from git import *

AWS_KEY = "<AWS_KEY>"
AWS_SECRET = "<AWS_SECRET>"
bucketName = 'jimib-backups'
pathRootRepository = '/home/git/repositories'
pathRootUpload = 'rpi-git'
pathRootCache = '/home/git/s3-cache'

#for emailing notifications (Using Gmail)
emailSender = '<EMAIL_SENDER>' #could be the same as recipient - good way to identify git server
emailRecipient = '<EMAIL_RECIPIENT>'
emailUser = "<EMAIL_USERNAME>"
emailPassword = "<EMAIL_PASSWORD>"

def percent_cb(complete, total):
	pass
	# print complete, total

print 'Connecting to S3...'

#open connection to S3
conn = S3Connection(AWS_KEY, AWS_SECRET)
print 'Connected to S3...'

#link to bucket
bucketName = 'jimib-backups'
print 'Open bucket "' + bucketName + '"...'
bucket = conn.get_bucket(bucketName)
print 'Opened bucket "' + bucketName + '"...'

def create_cache(fullpath, cachepath):
	cachedir = os.path.dirname(cachepath)
	if not os.path.exists(cachedir):
		os.makedirs(cachedir)

	#recreate cache by deleting old
	if os.path.exists(cachepath):
		os.remove(cachepath)

	#create the item
	print "create_cache: ", cachepath
	t = tarfile.open(name = cachepath, mode = 'w:gz')
	t.add(fullpath, os.path.basename(fullpath))
	t.close()

def upload_cache(cachepath, target):
	k = Key(bucket)
	print "upload:",cachepath,target 
	k.key = os.path.join(pathRootUpload, target)
	k.set_contents_from_filename(cachepath, cb=percent_cb, num_cb=10)
	k.close()

def is_cache_in_date(originalpath, cachepath):
	
	if not os.path.exists(cachepath):
		return False

	mtime_origin = os.stat(originalpath).st_mtime
	mtime_cache = os.stat(cachepath).st_mtime
	if mtime_origin > mtime_cache:
		return False
	elif has_directory_been_modified_since(originalpath, mtime_cache):
		return False

	return True

def has_directory_been_modified_since(path, mtime):
	for root, dirnames, files in os.walk(path):
		if os.stat(root).st_mtime > mtime:
			return True

	return False

#check each repository - if no cache or cache is out dated then we need to re-upload it
arrUpdatedRepos = []
for root, dirnames, files in os.walk(pathRootRepository):
	rootName = os.path.basename(root)
	fileName, fileExtension = os.path.splitext(rootName)
	if (fileExtension == ".git"):
		gitName = os.path.relpath(root, pathRootRepository)
		pathRel = gitName + ".tar.gz"
		cachepath = os.path.join(pathRootCache, pathRel)

		#get the last set of commits
		git = Git(root)
		
		if not is_cache_in_date(root, cachepath):
			gitDetails = "<strong>"+gitName+"</strong>"

			try:
                        	logs =  git.log('--pretty=oneline', '--since=1.hour').split('\n')
				gitDetails = gitDetails + "<br>" + "<br>".join(logs)
                	except:
                        	pass

			print gitDetails

			arrUpdatedRepos.append(gitDetails)
			create_cache(root, cachepath)
			#need to upload
			upload_cache(cachepath, pathRel)

print "Completed check..."
conn.close()

#notify of changes
if len(arrUpdatedRepos) > 0:
	import smtplib
 
	SMTP_SERVER = 'smtp.gmail.com'
	SMTP_PORT = 587
 
	subject = 'Git Repo Back Up'
	body = "Modified Repos:<br><br>"
	body = body + "<br><br>".join(arrUpdatedRepos)
 
	headers = ["From: " + emailSender,
           "Subject: " + subject,
           "To: " + emailRecipient,
           "Mime-Version: 1.0",
           "Content-Type: text/html;"]

	headers = "\r\n".join(headers)
 
	session = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
 
	session.ehlo()
	session.starttls()
	session.ehlo
	session.login(emailUser, emailPassword)
 
	session.sendmail(sender, recipient, headers + "\r\n\r\n" + body)
	session.quit()


