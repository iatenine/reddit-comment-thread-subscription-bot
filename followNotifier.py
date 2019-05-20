import praw
import time
import pickle
import logging

#Set to your needs
SUBREDDIT = ******
AGENT = *****

NOTIFIER = "AutoModerator"
FOLLOW_TEXT = "!follow"
SUBSCRIBE_SUBJECT = "Follow Request"
DESIRED_FLAIR = "Unsolved"
TIME_LIMIT = 900   #Default for first run only (measured in secs)
CURR_TIME = time.time()
TIME_FILE = "time.pickle"
SUB_FILE = "subscribers.pickle"
reddit = praw.Reddit('bot', user_agent=AGENT)

#Log for debugging purposes
CURR_TIME_STR = str(time.strftime("%c"))
message_count = 0


def check_post(post):
	post = get_post_from_url(post)
	return post.link_flair_text == DESIRED_FLAIR

def get_last_run():
	last_run = 0
	last_time = load(TIME_FILE)
	save(CURR_TIME, TIME_FILE)

	if last_time == None:
		return TIME_LIMIT
	else:
		last_run = CURR_TIME - last_time
		return last_run


def get_subscribers():
	strArr = load(SUB_FILE)
	if strArr == None:
		strArr = []
	conversations = reddit.subreddit(SUBREDDIT).modmail.conversations(state='all', sort= 'unread', limit=20)

	for conv in conversations:
		try:
			if conv.user.name != NOTIFIER and str(conv.subject) != SUBSCRIBE_SUBJECT:
				continue
			messagetext = str(conv.messages[0].body_markdown)			
			if check_post(messagetext.split()[0]) == False:
				send_message("A thread you were following is now marked as Solved", messagetext.split()[0] + " is no longer marked unsolved. You have been automatically unsubscribed from further updates", messagetext.split()[1])
			else:
				strArr.append(messagetext.split())
			conv.archive()
		except Exception as e:
			logging.exception("Exception occurred")
			pass
	save(strArr, SUB_FILE)
	return strArr


def get_comments(submission):
	return submission.comments

def get_forest_str(post, time_span, exclude = ""):
	forest = get_comments(get_post_from_url(post))
	ret = ""
	src_link = get_post_from_url(post).url
	print("Checking past " + str(time_span) + " seconds")

	for comment in forest:
		age = CURR_TIME - comment.created_utc
		if comment.author == exclude:
			continue
		if comment.author == "Automoderator" or comment.body.lower() == FOLLOW_TEXT.lower():
			continue
		tempStr = ">" + comment.body + "\n"
		if len(comment.replies.list()) > 0:
			fire = False
			for reply in comment.replies.list():
				tempAge = CURR_TIME - reply.created_utc
				if tempAge < time_span:
					fire = True 
				tempStr += ">>" + reply.body + "\n" + "\n"
			if fire:
				ret += tempStr
		elif age < time_span:
			ret += tempStr
	if ret != "":
		ret += "\n\n[" + str(get_post_from_url(post).title) + "](" + str(src_link) + ")" 
	return ret	

def get_post_from_url(loc):
	submission = reddit.submission(url = loc)
	return submission		

def load(FILENAME):
	try:
		with open(FILENAME, 'rb') as handle:
			return pickle.load(handle)
	except:
		return None

def notify_subscribers():
	val = get_subscribers()
	time_span = get_last_run()

	if len(val) != 0:
		for i in val:
			link = i[0]
			subscriber = i[1]
			msg = get_forest_str(link, time_span, subscriber)
			if msg != "":
				send_message("New comments found in a thread you're following", msg, subscriber)

def save(var, FILENAME):
	with open(FILENAME, 'wb') as handle:
		pickle.dump(var, handle)

def send_message(message_subject, message_body, subscriber):
	try:
		reddit.redditor(subscriber).message(message_subject, message_body)
		logging.info('Sent message to %s', subscriber)
	except Exception as e:
		logging.exception("Exception occurred")
		pass

#Main loop begins here, why not
logging.basicConfig(level=logging.INFO, filename='20Q_error.log', format='%(asctime)s - %(levelname)s - %(message)s')
notify_subscribers()
