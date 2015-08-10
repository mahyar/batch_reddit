This is my ugly, hacked up script that lets you download a set of user resources 
(comments, submissions, etc) from a reddit user and save it to a json file. You can also delete those resources from reddit with this script if your logged in as them.

Go see how to setup a reddit app with praw / prawoauth2

**LIMITATIONS:** 

Since you can only fetch 1000 items of a type from reddit, you can only download your latest
1000 items of each type.  Maybe deleting them and then trying again will let you get the next 1000?

This 1000 item limit is a reddit server limitation, not a limit of this script.  The script maybe could get around it by
getting the oldest item of each type, and then doing a search for all items by user x before time y, if
that is possible. (TODO)

**DOES NOT DOWNLOAD YOUR INBOX / PMs**  (TODO Should do this one day)

**Why did I make it?**

1. There is nothing like google takeout in reddit, so you cannot export all of your data as a user.
2. When you press the delete user button, you do not delete your comments or your submissions, you just remove your username tag from them.  And whats worse, once you have done that, you cannot go back and remove your actual content.