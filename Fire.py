from firebase_admin import firestore
from firebase_admin import credentials
import firebase_admin
from enum import Enum
import datetime
import pytz
from time import sleep
import os
import json

def get_timestamp()->str:
    date = datetime.datetime.now(pytz.timezone('America/New_York'))
    stringed = date.strftime('%Hh%Mm%Ss')
    return stringed

def get_date()->str:
    date = datetime.datetime.now(pytz.timezone('America/New_York'))
    stringed = date.strftime('%m-%d-%Y')
    return stringed

class ManagementLocations(Enum):
    email = "email_verification"
    phone = "phone_verification"
    verifier = "verifier_text"
    verifier_method = "verifier_method"


class Fire:
    db = ""
    bot = ""
    watcher = ""

    def on_verifier_snapshot(self, doc_snapshot, changes, read_time):
        values = self.get_management_values()
        if values[ManagementLocations.verifier_method.value] != "":
            verifier_method = values[ManagementLocations.verifier_method.value]
            self.bot.__verifier_click__(verifier_method)  # click the correct method
            self.set_management_value(ManagementLocations.verifier_method, "")  # set it to empty after login
        if values[ManagementLocations.email.value] != "":
            # User has entered the email verification Code
            print("Receieved Email verification Code: " + values[ManagementLocations.email.value])
            self.set_management_value(ManagementLocations.email, "")  # set it to empty after login
        if values[ManagementLocations.phone.value] != "":
            # User has entered the Text verification Code
            phone_value = values[ManagementLocations.phone.value]
            print("Recieved Text verification Code: " + phone_value)
            self.bot.__verifier_code_enter__(phone_value)
            self.set_management_value(ManagementLocations.phone, "")  # set it to empty after login

    def __init__(self, bot):
        cred = credentials.Certificate('instabot-bee53-firebase-adminsdk-uuob3-43254d1074.json')
        firebase_admin.initialize_app(cred, {
          'projectId': "instabot-bee53",
        })
        self.db = firestore.client()
        self.bot = bot
        self.watcher = self.db.collection(bot.username).document(u'management').on_snapshot(self.on_verifier_snapshot)

    def set_whitelist(self, users: [str]):
        user_dict = {"users": users}
        if not self.db.collection(self.bot.username).document(u'whitelist').get().exists:
            self.db.collection(self.bot.username).document(u'whitelist').set(user_dict)
        else:
            self.db.collection(self.bot.username).document(u'whitelist').update(user_dict)

    def get_whitelist(self)->[str]:
        users = self.db.collection(self.bot.username).document(u'whitelist').get().to_dict()
        return users["users"]

    def set_post_queue(self, post_list: [str]):
        post_dict = {"posts": post_list}
        if not self.db.collection(self.bot.username).document(u'post_queue').get().exists:
            self.db.collection(self.bot.username).document(u'post_queue').set(post_dict)
        else:
            self.db.collection(self.bot.username).document(u'post_queue').update(post_dict)

    def get_post_queue(self)->[str]:
        users = self.db.collection(self.bot.username).document(u'post_queue').get().to_dict()
        return users["posts"]

    def remove_from_queue(self, post_link: str):
        curr_queue: [str] = self.get_post_queue()
        for i in range(curr_queue.count(post_link)): curr_queue.remove(post_link)  # filter
        self.set_post_queue(curr_queue)

    def set_management_value(self, case: ManagementLocations, text: str):
        post_dict = {str(case.value): text}
        if not self.db.collection(self.bot.username).document(u'management').get().exists:
            self.db.collection(self.bot.username).document(u'management').set(post_dict)
        else:
            self.db.collection(self.bot.username).document(u'management').update(post_dict)

    def get_management_values(self)->dict:
        values = self.db.collection(self.bot.username).document(u'management').get().to_dict()
        return values

    def get_statistics(self)->dict:
        values = self.db.collection(self.bot.username).document("statistics").get().to_dict()
        return values

    def set_statistics(self, follows: [str] = [], unfollows: [str] = []):
        date = get_date()
        post_dict = {date: {
            "followed": follows,
            "unfollowed": unfollows
        }}
        if not self.db.collection(self.bot.username).document("statistics").get().exists:
            self.db.collection(self.bot.username).document("statistics").set(post_dict)
        else:
            current_list = self.get_statistics()
            try:
                fire_followed = current_list[date]["followed"]
                fire_unfollowed = current_list[date]["unfollowed"]
                for user in follows:
                    if user not in fire_followed:
                        fire_followed.append(user)
                for user in unfollows:
                    if user not in fire_unfollowed:
                        fire_unfollowed.append(user)
                current_list[date]["followed"] = fire_followed
                current_list[date]["unfollowed"] = fire_unfollowed
            except:
                current_list[date] = post_dict
            self.db.collection(self.bot.username).document("statistics").set(current_list, merge=True)

    def local_save(self, followed: [str] = [], unfollowed: [str] = []):
        date = get_date()
        current_dict = self.load_local_save()
        if current_dict != {}:
            curr_followed = current_dict[date]["followed"]
            curr_unfollowed = current_dict[date]["unfollowed"]
            for user in followed:
                if user not in curr_followed:
                    curr_followed.append(user)
            for user in unfollowed:
                if user not in curr_unfollowed:
                    curr_unfollowed.append(user)
            current_dict[date] = {
                "followed": curr_followed,
                "unfollowed": curr_unfollowed
            }
            with open('logs/' + self.bot.username + '.json', 'w') as outfile:
                json.dump(current_dict, outfile)
                print("Save Overitten")
        else:
            new_dict = {
                date: {
                    "followed": followed,
                    "unfollowed": unfollowed
                }
            }
            with open('logs/' + self.bot.username + '.json', 'w') as outfile:
                json.dump(new_dict, outfile)
                print("New Save Created")

    def load_local_save(self)->dict:
        if not os.path.isdir('logs'):
            os.mkdir("/logs/")
        filepath = 'logs/' + self.bot.username + ".json"
        if not os.path.exists(filepath):
            with open('logs/' + self.bot.username + '.json', 'w') as outfile:
                json.dump({}, outfile)
        with open(filepath) as json_file:
            data = json.load(json_file)
            return data

