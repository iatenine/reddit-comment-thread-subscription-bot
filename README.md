# Reddit Comment Thread Subscription Bot

This bot is designed to notify users who have chosen to subscribe to a Reddit submission of updates to comments and their replies
for which they are not the author or the top-level post author (and would thereby be aware or notified by Reddit anyways)

Pre-requisites
--------------
- [followNotifier.py](https://github.com/iatenine/PRAWFollowNotifier/blob/master/followNotifier.py)
- Python 3
- Crontab
- Automoderator and modmail access to the targeted subreddit


Getting Started
---------------
You will first need the following code added to your Automoderator config:

    type: comment
    body: "!follow"
    action: remove
    moderators_exempt: false
    modmail_subject: "Follow Request"
    modmail: "{{author}}"
    message_subject: Follow Confirmation
    message:
        This message is a confirmation that you have been subscribed to follow {{title}}. You will be updated with a message every 15 mins if a conversation has been updated (excluding your own)
        
 Confirmation message and message_subject can be set as you see fit or even omitted
 
 Next, be sure to add a 'bot' field to the bottom of your praw.ini file that will pass the username, password, 
 client ID and secret to Reddit:
 
    [bot]
    client_id=*******
    client_secret=**********
    password=********
    username=*******
    
 [How to get a client id or secret](https://github.com/reddit-archive/reddit/wiki/OAuth2)
 
 Now, Fill in all fields marked with ***** at the top of followNotifier.py with the relevant info to your situation
 By default the time frame is set to the past 15 mins (900 secs) but this can be manipulated by changing the value of TIME_LIMIT
 
 Now add the cron job by executing:
 
     crontab -e
 And adding to the bottom:
 
     */15 * * * * python3 /path/to/followNotifier.py
 
 *This runs every 15 mins by default but can (and should) be changed to whatever time frame is set under TIME_LIMIT
 **Due to both Reddit policies and potentially long execution times of the script is not recommended to fire the script more
 than once every 5 mins
