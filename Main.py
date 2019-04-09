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
insta = InstaBot(username, "Ledzep123")  # new york proxy

# following = insta.get_following(username)
# insta.set_whitelist(username, following)
# new = insta.follow_from_post(post_link="https://www.instagram.com/p/BvqwCqpAqwC/", count=500)
# insta.unfollow_users_from_profile(count=7)


def get_timestamp()->str:
    date = datetime.datetime.now(pytz.timezone('America/New_York'))
    stringed = date.strftime('%Hh%Mm%Ss')
    return stringed


print("Starting: " + str(get_timestamp()))
while True:
    curr_time = datetime.datetime.now(pytz.timezone(time_zone))
    while (curr_time.hour >= working_hours[0]) & (curr_time.hour <= working_hours[0]):
        curr_time = datetime.datetime.now(pytz.timezone(time_zone))
        queue = insta.get_post_queue()
        for post in queue:
            try:
                followed = insta.follow_from_post(post_link=post, count=50)
                print("-------------------- Followed :" + str(len(followed)))
            except:
                print("watever")
            insta.remove_from_queue(post)
        new_posts = insta.find_posts()
        insta.set_post_queue(new_posts)
        print("Fnding new posts at: " +str(get_timestamp()))
    sleep(60)
