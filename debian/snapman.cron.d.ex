#
# Regular cron jobs for the snapman package
#
0 4	* * *	root	[ -x /usr/bin/snapman_maintenance ] && /usr/bin/snapman_maintenance
