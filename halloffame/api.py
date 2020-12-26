# File: api.py
# Creation: Thursday December 3rd 2020
# Author: Arthur Dujardin
# Contact: arthur.dujardin@ensg.eu
#          arthurd@ifi.uio.no
# --------
# Copyright (c) 2020 Arthur Dujardin


import time
from tqdm import tqdm
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .utils import xpath_soup, convert_date


class HallOfFameAPI:
    r"""
    API to access data on ``facebook.com`` in its basic version.

    * :attr:`BASE_URL` (str): URL used to scrape data.
    
    * :attr:`LOGIN_URL` (str): URL used to login.
    
    * :attr:`executable_path` (str): Path to the executable driver. It should be something like `geckodriver.exe`. 
        Find one at `this repo <https://github.com/mozilla/geckodriver/releases>`__.
    
    * :attr:`driver` (selenium.webdriver): The driver used to connect on facebook.
    
    * :attr:`reaction2href` (dict): Dictionary where the keys are the reactions (``"LIKE"``, ``"AHAH"`` etc.) 
        and values are ``href`` pointing to a single reaction. As Facebook is constantly changing the ids for their reaction icons,
        they cannot be scrapped. The workaround here is to scrape known reactions, and save their classes in cache.
        Then, this final dictionary linking classes to reactions is used to scrape unknown reactions.

    * :attr:`class2reaction` (dict): Dictionary mapping classes to their reaction. E.g. ``"sx_973dvziD"`` may link to the reaction ``"AHAH"``.
        Note that reaction classes always start with ``"sx_"``.
        
    .. note::
        You should provide the ``reaction2href`` data. To do so, simply create posts with you facebook account, 
        and manually add a single unique reaction on all of them (e.g. ``"LIKE"`` for the first post, ``"AHAH"`` for the second etc.).
        Then, click on the reaction icon, and save the href (everything after ``https://m.facebook.com``). 
        Note that the href must start with a back slash.
        Finally, copy & paste all these hrefs to the ``reaction2href`` dict, and provide it when you connect to ``HallOfFameAPI``.

    """

    BASE_URL = "https://m.facebook.com"
    LOGIN_URL = "https://mbasic.facebook.com"

    def __init__(self, executable_path="geckodriver.exe", reaction2href={}):
        self.executable_path = executable_path
        self.driver = webdriver.Firefox(executable_path=executable_path)
        self.reaction2href = reaction2href
        self.class2reaction = {}

    def login(self, email, password):
        self._login(email, password)
        try:
            self._reconnect(email, password)
        except Exception:
            pass

    def _login(self, email, password):
        self.driver.get(self.LOGIN_URL)
        form = self.driver.find_element_by_xpath("//form[@id ='login_form']")
        email_input = form.find_element_by_name("email")
        password_input = form.find_element_by_name("pass")
        email_input.send_keys(email)
        password_input.send_keys(password)
        submit_button = self.driver.find_element_by_xpath("//input[@type ='submit']")
        submit_button.click()

    def _reconnect(self, email, password):
        login_button = self.driver.find_element_by_xpath('/html/body/div/div/div[2]/div/div[2]/div[2]/a[1]')
        login_button.click()
        self.login(email, password)

    def _get_reaction_class(self, href):
        # Connect to a single reaction page
        self.driver.get(f"https://m.facebook.com/{href}")
        page = self.driver.page_source
        soup = BeautifulSoup(page, 'lxml')
        # Get the emoji
        reaction = soup.select("._1uja._59qr")[0]
        react_classes = reaction.select("i.img._59aq")[0].get("class")
        # Search for the class that defines the emoji ("LIKE", "AHAH", "WOW", etc.)
        for react_class in react_classes:
            if react_class[:3] == "sx_":
                return react_class
        return None

    def init_reactions(self):
        self.class2reaction = {}
        for reaction, href in self.reaction2href.items():
            self.class2reaction[self._get_reaction_class(href)] = reaction.upper()


    def scroll_end(self, sleep=3, scroll_max=None):
        """Scroll down until the end of the current document is reached.

        Args:
            driver (selenium.webdriver.firefox.webdriver.WebDriver): WebDriver used to connect to facebook.
                The current supported driver is only limited to Firefox.
            sleep (int, optional): Sleep delay between each scroll. 
                If the sleep delay is too small, the function may exit before the end of the document is reached. 
                Defaults to ``3``.
            scroll_max (int, optional): Number of maximum scroll to make. If ``None``, will scroll until the end. Defaults to ``None``.

        .. note::
            The function modify the ``driver`` in place.
        """
        # Get scroll height
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        if scroll_max is None:
            scroll_max = 99
        while scroll_max > 0:
            scroll_max -= 1
            # Scroll down to bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # Wait to load page
            time.sleep(sleep)
            # Calculate new scroll height and compare with last scroll height
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def get_reactions(self, post_id):
        """Get the reaction from a page's post.

        Args:
            driver (selenium.webdriver.firefox.webdriver.WebDriver): WebDriver connected to the post page.
                The current supported driver is only limited to Firefox.

        Returns:
            list: list of reactions (dict) conaining the user and reaction.
        """
        self.driver.get(f"{self.BASE_URL}/ufi/reaction/profile/browser/?ft_ent_identifier={post_id}")
        page = self.driver.page_source
        soup = BeautifulSoup(page, 'lxml')
        # get the total number of reactions
        try:
            num_reactions = int(soup.find("span", {"data-sigil": "reaction_profile_sigil"}).text.split(" ")[1])
        except IndexError:
            num_reactions = 0
        # If > 50 reactions, load all the pages of reactions (scroll down + load more button)
        if num_reactions > 50:
            while True:
                try:
                    # Find the "load more" button, and click
                    load_more_soup = soup.select(".primarywrap strong")[0]
                    load_more = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.XPATH, xpath_soup(load_more_soup))))
                    load_more.click()
                    # One scroll down to go to the next "load more" button, if any
                    self.scroll_end(sleep=3, scroll_max=None)
                except Exception:
                    break
            # Load the entire page with Beautiful Soup
            page = self.driver.page_source
            soup = BeautifulSoup(page, 'lxml')

        # Load the item (content of the reaction)
        raw_reactions = soup.select(".item")
        reactions = []
        for reaction in raw_reactions:
            # Get the name of the person who reacted
            user = reaction.select("span strong")[0].text
            user_id = reaction.select("a")[0].get("href").split("/")[1].split("&")[0].split("?groupid")[0]
            # Find the reaction emoji
            react_classes = reaction.parent.select("i.img._59aq")[0].get("class")
            # Convert the emoji class to id
            react_type = None
            # While loop in case the ids changed (facebook change id, for security reasons)
            while react_type is None:
                for react_class in react_classes:
                    if react_class in self.class2reaction.keys():
                        react_type = self.class2reaction[react_class]
                # If ids changed, update the reaction to class dict
                if react_type is None:
                    self.init_reactions()
            # Add the reaction
            reactions.append({
                "user": user,
                "user_id": user_id,
                "reaction": react_type
            })
        return reactions

    def _unfold_comments(self):
        """Function used to unfold all discussions from a thread.

        Args:
            driver (selenium.webdriver.firefox.webdriver.WebDriver): WebDriver connected to the post page.
                The current supported driver is only limited to Firefox.
        """
        unfolded_comments = self.driver.find_elements_by_class_name("_2b1h.async_elem")
        for comment in unfolded_comments:
            comment.click()

    def get_comments(self, group_id, post_id):
        """Retrieve all comments from a page post.

        Args:
            driver (selenium.webdriver.firefox.webdriver.WebDriver): WebDriver connected to the post page.
                The current supported driver is only limited to Firefox.

        .. note::
            This function can be slow as it also extracts reactions for all comments.
        """
        self.driver.get(f"{self.BASE_URL}/groups/{group_id}/permalink/{post_id}/?anchor_composer=false")
        self._unfold_comments()
        page = self.driver.page_source
        soup = BeautifulSoup(page, 'lxml')

        # Search for all comments
        all_comments = []
        comments = soup.findAll("div", {"data-sigil": "comment"})
        for comment in comments:
            comment_user = comment.select("._2b05 a")[0].text
            comment_user_id = comment.select("._2b05 a")[0].get("href").split("/")[1].split("&")[0].split("?groupid")[0]
            comment_date = comment.select("abbr")[0].text
            comment_href = comment.select("._2b05 a")[0].get("href")
            comment_id = comment.get("data-uniqueid")
            comment_text = comment.find("div", {"data-sigil": "comment-body"}).text
            # Search for reactions
            comments_reactions = []
            reactions_soup = comment.select("._14v5 a._14v8._4edm")
            if reactions_soup:
                comment_href = reactions_soup[0].get("href")
                comment_group_id, comment_id = comment_href.split("ft_ent_identifier=")[1].split("&")[0].split("_")
                comments_reactions = self.get_reactions(comment_id)

            # Search for replies
            replies = []
            reply_comments = comment.findAll("div", {"data-sigil": "comment inline-reply"})
            for reply_comment in reply_comments:
                reply_user = reply_comment.select("._2b05 a")[0].text
                reply_user_id = reply_comment.select("._2b05 a")[0].get("href").split("/")[1].split("&")[0].split("?groupid")[0]
                reply_date = reply_comment.select("abbr")[0].text
                reply_href = reply_comment.select("._2b05 a")[0].get("href")
                reply_id = reply_comment.get("data-uniqueid")
                reply_text = reply_comment.find("div", {"data-sigil": "comment-body"}).text
                # Search for reactions
                reply_reactions = []
                reply_reactions_soup = reply_comment.select("._14v5 a._14v8._4edm")
                if reply_reactions_soup:
                    reply_href = reply_reactions_soup[0].get("href")
                    reply_group_id, reply_id = reply_href.split("ft_ent_identifier=")[1].split("&")[0].split("_")
                    reply_reactions = self.get_reactions(reply_id)
                # Update the reply comment
                replies.append({
                    "href": reply_href,
                    "comment_id": reply_id,
                    "text": reply_text,
                    "user": reply_user,
                    "user_id": reply_user_id,
                    "date": convert_date(reply_date).isoformat(),
                    "reactions": reply_reactions
                })
            # Add the comment and all the replies
            all_comments.append({
                "href": comment_href,
                "comment_id": comment_id,
                "text": comment_text,
                "user": comment_user,
                "user_id": comment_user_id,
                "date": convert_date(comment_date).isoformat(),
                "reactions": comments_reactions,
                "replies": replies
            })
        return all_comments

    def _find_posts(self, group_id, sleep=3, scroll_max=None, topk=-1):
        self.driver.get(f"https://m.facebook.com/groups/{group_id}")
        self.scroll_end(sleep=sleep, scroll_max=scroll_max)
        page = self.driver.page_source
        soup = BeautifulSoup(page, 'lxml')
        articles = soup.find_all("article")
        posts, raw_articles = [], []
        for article in articles:
            try:
                # Retrieve the text (paragraphs) of the post
                text = ""
                text_soup = article.select(".story_body_container ._5rgt._5nk5 p")
                if text_soup:
                    text = "\n".join([paragraph_soup.text for paragraph_soup in text_soup])
                # Search for the ids
                features = eval(article["data-ft"])
                post_id = features["top_level_post_id"]
                group_id = features["group_id"]
                user = article.select("h3 strong a")[0].text
                user_id = article.select("h3 strong a")[0].get("href").split("/")[1].split("&")[0].split("?groupid")[0]
                date = article.select("abbr")[0].text 
                posts.append({
                    "post_id": post_id,
                    "group_id": group_id,
                    "user": user,
                    "user_id": user_id,
                    "date": convert_date(date).isoformat(),
                    "text": text
                })
                raw_articles.append(article)
                # Break ?
                if topk > 0 and len(raw_articles) >= topk:
                    return posts, raw_articles
            except Exception:
                continue
        return posts[:topk], raw_articles[:topk]

    def get_posts(self, group_id, sleep=3, topk=-1, scroll_max=None):
        all_posts = []
        posts, _ = self._find_posts(group_id, sleep=sleep, scroll_max=scroll_max, topk=topk)
        for post in tqdm(posts, desc="Retrieving Data", leave=True, position=0, total=len(posts)):
            try:
                comments = self.get_comments(group_id, post["post_id"])
                # Get the reactions for the post
                reactions = self.get_reactions(post["post_id"])
                all_posts.append({
                    "post_id": post["post_id"],
                    "group_id": group_id,
                    "user": post["user"],
                    "user_id": post["user_id"],
                    "date": post["date"],
                    "text": post["text"],
                    "comments": comments,
                    "reactions": reactions
                })
            except Exception:
                continue
        return all_posts

    def publish_post(self, group_id, message):
        """Publish a post to a facebook group/page.

        Args:
            driver (selenium.webdriver.firefox.webdriver.WebDriver): WebDriver connected to the post page.
                The current supported driver is only limited to Firefox.
            message (str): Message to post.
        """
        self.driver.get(f"https://m.facebook.com/groups/{group_id}")
        self.driver.find_elements_by_class_name("_4g34._6ber._78cq._7cdk._5i2i._52we")[0].click()
        page = self.driver.page_source
        soup = BeautifulSoup(page, 'lxml')
        text_soup = soup.select("textarea")[-2]
        textarea = WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.XPATH, xpath_soup(text_soup))))
        textarea.send_keys(message)
        post_soup = soup.findAll("div", {"data-sigil": "upper_submit_composer"})[-1].select("button")[0]
        try:
            post_button = WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.XPATH, xpath_soup(post_soup))))
        except Exception as error:
            print(f"Could not publish. Retrying... {error}")
            return self.publish_post(group_id, message)
        post_button.click()
        # Wait for the message to be posted
        time.sleep(5)
        # Return the id of the last post (likely to be the published one)
        posts, _ = self._find_posts(group_id, sleep=0, scroll_max=1)
        return posts[0]["post_id"]

    def edit_post(self, group_id, post_id, message):
        """Edit a post to a facebook group/page.

        Args:
            driver (selenium.webdriver.firefox.webdriver.WebDriver): WebDriver connected to the post page.
                The current supported driver is only limited to Firefox.
            post_id: (str): ID of the post to edit. (e.g. `"745393222993590"`)
            message (str): New message.

        .. note::
            This function will erase the previous post's text, and rewrite it with the new message.
        """
        posts, raw_articles = self._find_posts(group_id, sleep=0, scroll_max=1)
        for post, raw_article in zip(posts, raw_articles):
            if str(post_id) == post["post_id"]:
                break
        # Click the option menu to edit the post
        options = raw_article.select("._4s19")[0]
        self.driver.find_element_by_xpath(xpath_soup(options)).click()
        time.sleep(2)
        page = self.driver.page_source
        soup = BeautifulSoup(page, 'lxml')
        option_buttons = soup.select("._56bz._54k8._55i1._58a0.touchable._53n6")
        edit_buttons = []
        for option in option_buttons:
            if "editPostButton" in option.get("data-sigil"):
                edit_buttons.append(option)
        edit_button = edit_buttons[-1]
        self.driver.find_element_by_xpath(xpath_soup(edit_button)).click()
        # Edit
        page = self.driver.page_source
        soup = BeautifulSoup(page, 'lxml')
        text_soup = soup.select("textarea")[-2]
        textarea = WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.XPATH, xpath_soup(text_soup))))  # id can change ! ex id="uniqid_1"
        textarea.clear()
        textarea.send_keys(message)
        # Save
        page = self.driver.page_source
        soup = BeautifulSoup(page, 'lxml')
        save_soup = soup.select("#modalDialogHeaderButtons button")[0]
        try:
            save_button = WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.XPATH, xpath_soup(save_soup))))
        except Exception as error:
            print(f"Could not edit. Retrying... {error}")
            return self.edit_post(group_id, post_id, message)
        save_button.click()

    def quit(self):
        self.driver.quit()

    def __repr__(self):
        return "<Facebook Hall-Of-Fame API>"
