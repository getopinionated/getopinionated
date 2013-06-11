#!/bin/bash
#testing server
cd /home/de317070/webapps/getopinionated/getopinionated/getopinionated
git fetch
newUpdatesAvailable=`git diff HEAD FETCH_HEAD`
if [ "$newUpdatesAvailable" != "" ]
then
	git update-index --assume-unchanged getopinionated/local_settings.py
	git rm --cached getopinionated/local_settings.py
	git reset --hard
	git pull
	python2.7 $HOME/webapps/getopinionated/getopinionated/manage.py collectstatic --noinput
	$HOME/webapps/getopinionated/apache2/bin/restart
fi