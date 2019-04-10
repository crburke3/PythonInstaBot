from selenium import webdriver
from time import sleep
from Fire import Fire
from random import randint
import logging
import os
from Fire import ManagementLocations

latency = 1

class InstaBot:
    chrome: webdriver.Chrome
    authenticated = False
    username = ""
    access_token = ""
    firebase = ""
    password = ""
    whitelist: [str] = []
    following = 0
    followers = 0
    posts = 0
    verified = False

    def __init__(self, username: str, password: str, proxy: str = ""):
        mobile_emulation = {"deviceName": "Nexus 5"}
        from selenium.webdriver.chrome.options import Options
        mobile_emulation = {
            "deviceMetrics": {"width": 360, "height": 640, "pixelRatio": 3.0},
            "userAgent": "Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Mobile Safari/535.19"}
        chrome_options = Options()
        chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
        if proxy != "":
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('--proxy-server=%s' % proxy)
        self.chrome = webdriver.Chrome(chrome_options=chrome_options)
        self.chrome.set_window_size(300, 1000)
        print("Logging in...")
        self.username = username
        self.password = password
        self.firebase = Fire(bot=self)
        stats = self.get_user_stats()
        self.following = stats["following"]
        self.followers = stats["followers"]
        self.posts = stats["posts"]
        # if not os.path.isdir("logs"):
        #     os.mkdir("logs")
        # log_path = "logs/" + username + ".log"
        # open(log_path, 'a').close()
        # logging.basicConfig(filename=log_path, level=logging.INFO)
        self.login(username, password)
        self.whitelist = self.firebase.get_whitelist()

    def login(self, username: str, password: str):
        self.chrome.get("https://www.instagram.com/accounts/login/")
        sleep(2)
        dom = self.chrome.find_element_by_class_name("rgFsT ")  # Specifies the location of the username and password
        user = dom.find_element_by_name('username')
        pwd = dom.find_element_by_name('password')
        user.clear()
        pwd.clear()
        user.send_keys(username)
        pwd.send_keys(password)
        pwd.send_keys(u'\ue007')
        sleep(1 + latency)
        url = self.chrome.current_url
        if "challenge" in url:
            self.verify_if_available()
        if "login" in url:
            self.check_login()
        # self.check_notification()

    def check_notification(self):
        self.chrome.implicitly_wait(200)
        notification = self.chrome.find_elements_by_class_name("aOOlW   HoLwm ")
        if len(notification) > 0:
            notification[0].click()

    def authenticate(self, username: str, password: str):
        self.chrome.get("https://api.instagram.com/oauth/authorize/?client_id=e9be1d873671481cadc31086049841aa&redirect_uri=http://www.google.com&response_type=code")
        self.chrome.implicitly_wait(200)
        usr = self.chrome.find_element_by_name('username')
        pwd = self.chrome.find_element_by_name('password')
        usr.clear()
        pwd.clear()
        usr.send_keys(username)
        pwd.send_keys(password)
        pwd.send_keys(u'\ue007')
        sleep(2)
        url = self.chrome.current_url
        key = url.split("=")
        key_len = len(key)
        key = key[key_len - 2] + "=" + key[key_len - 1]
        self.access_token = key

    def get_following(self, username: str):
        ret_list: [str] = []
        self.chrome.get("https://www.instagram.com/" + username)
        sleep(1)
        # following_btn = self.chrome.find_elements_by_class_name("-nal3 ")
        following_btn = self.chrome.find_elements_by_xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "g47SY lOXF2", " " ))]')
        if len(following_btn) > 0:
            following_btn[2].click()
            sleep(1)
            follow_list = self.chrome.find_elements_by_class_name("wo9IH")
            if len(follow_list) == 0:
                self.chrome.refresh()
                self.get_following(username)
            else:
                last_user_count = len(follow_list)
                while True:
                    for user in follow_list:
                        element_height = user.location["y"]
                        self.chrome.execute_script("window.scrollTo(0, " + str(element_height - 120) + ");")
                        username = str(user.text).split("\n")[0]
                        if username not in ret_list:
                            ret_list.append(username)
                        sleep(0.2)
                    follow_list = self.chrome.find_elements_by_class_name("wo9IH")
                    if len(follow_list) <= last_user_count:
                        return ret_list
                    else:
                        last_user_count = len(follow_list)
        else:
            self.get_following()
        return ret_list

    def check_login(self):
        dom = self.chrome.find_elements_by_class_name("rgFsT ")  # Specifies the location of the username and password
        if len(dom) > 0:
            print("Failed Login")
            sleep(2)
            self.login(username=self.username, password=self.password)

    def follow_from_post(self, post_link: str, count: int)->[str]:
        consec_fail = 0
        ret_list: [str] = []
        check_list: [str] = []
        self.chrome.get(post_link)
        sleep(1)
        like_btn = self.chrome.find_elements_by_class_name("zV_Nj")
        if len(like_btn) > 0:
            self.chrome.execute_script("arguments[0].click();", like_btn[0])
            sleep(2)
            follow_count = 0
            new_scroll = 0
            old_scroll = 1
            while new_scroll != old_scroll:
                old_scroll = self.chrome.execute_script("return window.pageYOffset;")
                user_list = self.chrome.find_elements_by_xpath(
                    '//*[contains(concat( " ", @class, " " ), concat( " ", "ZUqME", " " ))]')
                for user in user_list:
                    username = str(user.text).split("\n")[0]
                    if username in check_list:
                        continue
                    followed_user = self.follow_user_from_list(user_element=user)
                    if followed_user == "fail":
                        consec_fail += 1
                        if consec_fail >= 2:
                            consec_fail = 0
                            sleep_time = randint(120, 200)
                            print("Max Followed, sleeping for : " + str(sleep_time) + " seconds")
                            sleep(sleep_time)
                    if followed_user != "fail":
                        consec_fail = 0
                    if followed_user != "":
                        follow_count += 1
                        ret_list.append(followed_user)
                    if follow_count >= count:
                        print("Finished Process on post: " + post_link)
                        print("--- Followed: " + str(follow_count))
                        return ret_list
                    if username != None:
                        check_list.append(username)
                    new_scroll = self.chrome.execute_script("return window.pageYOffset;")
            return  ret_list

    def follow_user_from_list(self, user_element, updated_server=False)->str:
        try:
            element_height = user_element.location["y"]
            self.chrome.execute_script("window.scrollTo(0, " + str(element_height - 120) + ");")
            follow_btn = user_element.find_element_by_xpath(
                './/*[contains(concat( " ", @class, " " ), concat( " ", "L3NKy", " " ))]')
            follow_tex = str(follow_btn.text)
            if ("Following" in follow_tex) & ("Requested" in follow_tex):
                return ""
            sleep(1)
            sleep(randint(0, 2))
            element_text = str(user_element.text).split("\n")
            username = element_text[0]
            follow_text = element_text[2]
            if (username not in self.whitelist) & ("Following" not in follow_text) & ("Requested" not in follow_text):
                follow_btn = user_element.find_element_by_xpath('.//*[contains(concat( " ", @class, " " ), concat( " ", "L3NKy", " " ))]')
                self.chrome.execute_script("arguments[0].click();", follow_btn)
                sleep(2)
                follow_btn_2 = user_element.find_element_by_xpath('.//*[contains(concat( " ", @class, " " ), concat( " ", "L3NKy", " " ))]')
                if ("Following" in follow_btn_2.text) | ("Requested" in follow_btn_2.text):
                    print("Followed: " + username)
                    if updated_server:
                        self.firebase.set_statistics(follows=[username])
                    self.firebase.local_save(followed=[username])
                    return username
                else:
                    print("FAIL: Insta follow block")
                    return "fail"
        except Exception as e:
            print("FAIL: " + str(e))
            if "range" in str(e):
                sleep(0.25)
            print("---failed: follow user from list")
            return ""
        return ""

    def unfollow_users_from_profile(self, count: int)->[str]:
        unfollow_count = 0
        unfollow_list: [str] = []
        self.__go_to_following__()
        user_list = self.chrome.find_elements_by_class_name("wo9IH")
        for user in user_list:
            completion = self.__unfollow_user_from_list__(user)
            if completion != "":
                unfollow_count += 1
                unfollow_list.append(completion)
                if unfollow_count >= count:
                    return unfollow_list
        return unfollow_list

    def __go_to_following__(self):
        if self.username not in self.chrome.current_url:
            self.chrome.get("https://www.instagram.com/" + self.username + "/following/")
        sleep(2 + latency)
        header_btns = self.chrome.find_elements_by_class_name(" LH36I")
        header_btns[2].click()
        sleep(2 + latency)
        if "following" not in self.chrome.current_url:
            self.chrome.execute_script("arguments[0].click();", header_btns[2])
            sleep(2 + latency)
        user_list = self.chrome.find_elements_by_class_name("wo9IH")
        if len(user_list) == 0:
            self.chrome.refresh()
            self.__go_to_following__()

    def __unfollow_user_from_list__(self, user_element, update_server=False)->str:
        try:
            user_text = str(user_element.text).split("\n")
            username = user_text[0]
            follow_text = user_text[2]
            if ("Requested" in follow_text) | ("Following" in follow_text):
                if username not in self.whitelist:
                    follow_btn = user_element.find_element_by_xpath('.//*[contains(concat( " ", @class, " " ), concat( " ", "_8A5w5", " " ))]')
                    btn_height = follow_btn.location["y"]
                    self.chrome.execute_script("window.scrollTo(0, " + str(btn_height - 120) + ");")
                    sleep(0.5)
                    self.chrome.execute_script("arguments[0].click();", follow_btn)
                    self.__unfollow_user_from_list_secondary__()
                    sleep(2)
                    # We need to refresh the user_element after clicking the secondary one
                    new_user_list = self.chrome.find_elements_by_class_name("wo9IH")
                    for new_user_element in new_user_list:
                        new_username = str(new_user_element.text).split("\n")[0]
                        if username == new_username:
                            follow_btn = new_user_element.find_element_by_xpath('.//*[contains(concat( " ", @class, " " ), concat( " ", "_0mzm- sqdOP  L3NKy       ", " " ))]')
                            follow_btn_text = str(follow_btn.text)
                            if ("Requested" not in follow_btn_text) & ("Following" not in follow_btn_text):
                                print("Unfollowed: " + username)
                                if update_server:
                                    self.firebase.set_statistics(unfollows=[username])
                                self.firebase.local_save(unfollowed=[username])
                                return username
        except Exception as e:
            print(e)
            return ""

    def __unfollow_user_from_list_secondary__(self):
        second_unfollow = self.chrome.find_element_by_xpath('.//*[contains(concat( " ", @class, " " ), concat( " ", "aOOlW -Cab_   ", " " ))]')
        second_unfollow.click()

    def find_posts(self, count=3)->[str]:
        print("Searching for random user...")
        rando = self.__go_to_random_followed_user__()
        print("---found user: " + rando)
        sleep(2)
        ret_posts: [str] = []
        displayed_posts = self.chrome.find_elements_by_xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "v1Nh3 kIKUG  _bz0w", " " ))]')
        for post in displayed_posts:
            post_url_holder = post.find_element_by_xpath(".//a")
            url = post_url_holder.get_attribute("href")
            ret_posts.append(str(url))
            if len(ret_posts) >= count:
                return ret_posts
        return ret_posts

    def __scroll_from_user_list__(self, user_element):
        scroll_distance = user_element.location["y"] + (60 * 10) - 120
        self.chrome.execute_script("window.scrollTo(0, " + str(scroll_distance) + ");")

    def get_user_stats(self)->dict:
        if self.chrome.current_url != "https://www.instagram.com/" + self.username + "/":
            self.chrome.get("https://www.instagram.com/" + self.username)
        header_btns = self.chrome.find_elements_by_class_name(" LH36I")
        follower_count = str(header_btns[2].text).split("\n")[0]
        following_count = str(header_btns[1].text).split("\n")[0]
        post_count = str(header_btns[0].text).split("\n")[0]
        ret_val = {
            "followers": follower_count,
            "following": following_count,
            "posts": post_count
        }
        return ret_val

    def __get_search_list__(self, user_list):
        curr_scroll = self.chrome.execute_script("return window.pageYOffset;")
        search_list = []
        for user in user_list:
            if (user.location["y"] >= curr_scroll) & (user.location["y"] <= curr_scroll + 600):  # 600 is the visible scroll distance
                search_list.append(user)
            if user.location["y"] > curr_scroll + 600:
                for i in range(search_list.count(None)): search_list.remove(None)  # filter all of the None's from the search list (avoids issue)
                return search_list

    def __go_to_random_followed_user__(self)->str:
        random_num = randint(0, int(int(self.following) / 5))  # get random user from first 1/5th of the following list
        self.__go_to_following__()
        user_list = self.chrome.find_elements_by_class_name("wo9IH")
        user_count = 0
        search_list = self.__get_search_list__(user_list)
        while True:
            curr_count = 0
            for user in search_list:
                if user_count == random_num:
                    username = str(user.text).split("\n")[0]
                    self.chrome.get("https://www.instagram.com/" + username)
                    return username
                user_count += 1
                curr_count += 1
                if curr_count >= len(search_list):
                    self.__scroll_from_user_list__(user_element=user)
            user_list = self.chrome.find_elements_by_class_name("wo9IH")
            search_list = self.__get_search_list__(user_list)

    def verify_if_available(self):
        choice_options = self.chrome.find_elements_by_class_name("UuB0U ")
        email_text = ""
        phone_text = ""
        if len(choice_options) > 0:
            for choice in choice_options:
                if "Email" in choice.text:
                    email_text = choice.text
                if "Phone" in choice.text:
                    phone_text = choice.text
            self.firebase.set_management_value(ManagementLocations.verifier, str(email_text) + "\n" + str(phone_text))
        while not self.verified:
            sleep(1)

    def __verifier_click__(self, option: str):
        choice_options = self.chrome.find_elements_by_class_name("UuB0U ")
        for choice in choice_options:
            if option in str(choice.text):
                self.chrome.execute_script("arguments[0].click();", choice)
                choice.click()
                sleep(3)
                secuirty_btn = self.chrome.find_element_by_xpath(
                    '//*[contains(concat( " ", @class, " " ), concat( " ", "_5f5mN       jIbKX KUBKM      yZn4P   ", " " ))]')
                self.chrome.execute_script("arguments[0].click();", secuirty_btn)
                sleep(1)

    def __verifier_code_enter__(self, code: str):
        code_field = self.chrome.find_element_by_id("security_code")
        code_field.send_keys(code)
        code_field.send_keys(u'\ue007')
        sleep(2)
        if "challenge" not in self.chrome.current_url:
            self.verified = True
            self.firebase.set_management_value(ManagementLocations.verifier, "")
        else:
            print("Validation Failed, send notification")

