import praw
import time

SUBREDDIT = *****                       #Your subreddit name
NOTIFIER = "AutoModerator"              #Whatever entity delivers the notification messages, most likely Automoderator
FOLLOW_TEXT = "!follow"                 #The message commenters use to follow a thread (requires automod coordination)
ERROR_HANDLER = *****                   #Reddit user who will handle all error messages
SUBSCRIBE_SUBJECT = "Follow Request"    #The modmail subject delivered by notifier when a user subscribes
DESIRED_FLAIR = "Unsolved"              #Can only subscribe to posts with this flair
TIME_LIMIT = 900                        #The oldest a post can be in secs and still provide updates
CURR_TIME = time.time()                 #Establish time at the top to reduce variability caused by long script load times
AGENT = ******                          #Your user_agent id from Reddit

reddit = praw.Reddit('bot', user_agent=AGENT)    #Must set 'bot' in lib/python3.6/site-packages/praw.ini

def error_catch(e):
	send_message("Exception caught", e, ERROR_HANDLER)

def send_message(message_subject, message_body, subscriber):
	try:
		reddit.redditor(subscriber).message(message_subject, message_body)
	except Exception as e:
		error_catch(e)
		pass

def get_subscribers():
	strArr = []
	conversations = reddit.subreddit(SUBREDDIT).modmail.conversations(state='all', sort= 'unread', limit=20)
	for conv in conversations:
		try:
			if conv.user.name != NOTIFIER and str(conv.subject) != SUBSCRIBE_SUBJECT:
				continue
			messagetext = str(conv.messages[0].body_markdown)			
			if check_post(messagetext.split()[0]) == False:
				send_message("A thread you were following is no longer valid", messagetext.split()[0] + " is no longer marked unsolved. You have been automatically unsubscribed from further updates", messagetext.split()[1])
				conv.archive()   #Send message that post has been marked as "solved"
			else:
				strArr.append(messagetext.split())
		except Exception as e:
			error_catch(e)
			pass
	return strArr

#Returns id of a post corresponding to a url passed into the loc argument
def get_post_from_url(loc):
	submission = reddit.submission(url = loc)
	return submission

def get_comments(submission):
	return submission.comments

def get_forest_str(post, exclude = ""):
	forest = get_comments(get_post_from_url(post))
	ret = ""

	for comment in forest:
		age = CURR_TIME - comment.created_utc
		if comment.author == exclude or age > TIME_LIMIT:
			continue
		if comment.author == "Automoderator" or comment.body.lower() == FOLLOW_TEXT.lower():
			continue
		ret += ">" + comment.body + "\n"
		if len(comment.replies.list()) > 0:
			for reply in comment.replies.list():
				ret += ">>" + reply.body + "\n" + "\n"
	return ret			

def check_post(post):
	post = get_post_from_url(post)
	return post.link_flair_text == DESIRED_FLAIR

#Main loop begins here, why not
val = get_subscribers()

if len(val) != 0:
	for i in val:
		link = i[0]
		subscriber = i[1]
		msg = get_forest_str(link, subscriber)
		if msg != "":
			send_message("New comments found in a thread you're following", msg, subscriber)
