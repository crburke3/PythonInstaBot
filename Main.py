from InstaFunctions import InstaBot
import datetime
import pytz
from time import sleep

daily_follows = 500
unfollow_timeframe = 4  # In Days
time_zone = 'America/New_York'
working_hours = (0, 23)
suggested_posts = ["https://www.instagram.com/p/BrL_1mulv9O/", "https://www.instagram.com/p/Bv7e_u9HVD5/"]
username = "christianburkezz"
# insta = InstaBot(username, "Ledzep123", proxy="142.234.201.107:80")  # new york proxy
insta = InstaBot(username, "Ledzep123")
# following = insta.get_following(username)
# insta.set_whitelist(username, following)
# new = insta.follow_from_post(post_link="https://www.instagram.com/p/BvqwCqpAqwC/", count=500)
# insta.unfollow_users_from_profile(count=7)


def get_timestamp()->str:
    date = datetime.datetime.now(pytz.timezone('America/New_York'))
    stringed = date.strftime('%Hh%Mm%Ss')
    return stringed

todays_follow_count = 0

while True:
    curr_time = datetime.datetime.now(pytz.timezone(time_zone))
    while (curr_time.hour >= working_hours[0]) & (curr_time.hour <= working_hours[1]):
        print("Starting: " + str(get_timestamp()))
        curr_time = datetime.datetime.now(pytz.timezone(time_zone))
        queue = insta.firebase.get_post_queue()
        for post in queue:
            try:
                insta.firebase.remove_from_queue(post)
                followed = insta.follow_from_post(post_link=post, count=50)
                todays_follow_count += len(followed)
                print("-------------------- Followed: " + str(len(followed)))
                insta.firebase.set_statistics(follows=followed)
            except Exception as e:
                print(str(e))
        new_posts = insta.find_posts()
        insta.firebase.set_post_queue(new_posts)
        print("Fnding new posts at: " + str(get_timestamp()))
    sleep(60)
