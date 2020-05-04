"""Quantify Facebook user activity over time.

Facebook allows users to download a copy of their own data in a
machine readable format. This program extracts and quantifies
information about user activity from the data Facebook provides to
give users an aggregated, birds-eye overview of their Facebook
activity over time.

The program will produce a CSV file with dates as the index and
events (e.g. 'message_set' or 'commented') as columns. The data is
provided in a format that makes it easy to analyze.
"""

import argparse
import json
from datetime import date, datetime
from pathlib import Path
from re import findall
from sys import exit
from typing import Dict, List, Optional

import pandas as pd


class FacebookQuantifier():
    """Extract and quantify events in user data provided by Facebook.

    To count user activity, this class extracts timestamps found in a pre-
    defined list of files contained in the Facebook data, marking the date
    of varies user activities. See the list of data attributes below for
    a full overview.

    Attributes (required to instantiate object):
        folder : Path
            Folder that contains the data provided by Facebook
        user : str
            Name of the Facebook user

    Data Attributes (automatically generated upon instantiation):
        ad_interaction: List[date]
            User clicked on an ad
        added_friend : List[date]
            User connected with someone on Facebook
        received_friend_request : List[date]
            User received friend request
            Note: Only pending requests which have not been accepted
        rejected_friend_reject : List[date]
            User rejected friend request
        removed_friend : List[date]
            User removed friend
        apps_posts : List[date]
            Installed Facebook app posted on the user's timeline
        commented : List[date]
            User commented on posts from friends
            Note: 'posts' includes photos
        event_invitation : List[date]
            User received event invitation
        group_membership_activity (List[date]):
            User interacted with group (e.g. by joining them)
        group_posts : List[date]
            User posted in group
        installed_app : List[date]
            User installed Facebook apps
        liked_external_pages : List[date]
            User clicked the 'Like' button on external site
        liked_page : List[date]
            User liked a Facebook page
        created_page : List[date]
            User created a Facebook page
        created_note : List[date]
            User created a note (similar to pinned posts on timeline)
        others_posts_timeline : List[date]
            Others posted on the user's timeline
        profile_updated : List[date]
            User updated her profile
        reactions : List[date]
            User 'reacted' with 'Like' or other similar action
        responded_event : List[date]
            User reacted to events (e.g. 'going')
        searched : List[date]
            User searched something on Facebook
        poked : List[date]
            User poked someone
        voted : List[date]
            User voted in a poll
        saved_item : List[date]
            User 'saved' a post or other item
        followed_sb_st : List[date]
            User followed somebody or something
        addressbook_entry : List[date]
            User added someone to Facebook address book
        own_posts : Dict[str, List[date]]
            User posted on own timeline. Dict keys are:
                - 'own_posts_all' (anything posted)
                - 'own_posts_media' (photos and videos only)
                - 'own_posts_text_only' (no links or media)
                - 'own_posts_links' (links or links + text)
        messages : Dict[str, List[date]]
            Timestamps when user received or sent a message in Facebook messenger.
            Keys are 'sent_message' and 'received_message' unless no sent messages
            could be identified (due to user name not found). If that happens, dict
            has only one key named 'send_or_received'
    """

    def __init__(self, folder: Path, user: str) -> None:
        """Scan the data provided by Facebook and extracts timestamps of activities.

        Parameters
        ----------
        folder : Path
            The folder holding the data provided by Facebook, usually named
            'facebook-<user name>'
        user : str
            The name of the user the Facebook data belongs to. Whitespace is
            removed and string is lowercased. This makes sure the user name
            always has the same format, regardless of whether it was provided
            as an argument or extracted from the Facebook data folder.
        """
        self.folder = folder
        self.user = user.replace(" ", "").lower()

        files = {
            "file_friend_added":
                Path(self.folder, "friends", "friends.json"),
            "file_received_friend_request":
                Path(self.folder, "friends", "received_friend_requests.json"),
            "file_rejected_friend_reject":
                Path(self.folder, "friends", "rejected_friend_requests.json"),
            "file_friend_removed":
                Path(self.folder, "friends", "removed_friends.json"),
            "file_app_installs":
                Path(self.folder, "apps_and_websites", "apps_and_websites.json"),
            "file_comments":
                Path(self.folder, "comments", "comments.json"),
            "file_reactions":
                Path(self.folder, "likes_and_reactions", "posts_and_comments.json"),
            "file_own_posts":
                Path(self.folder, "posts", "your_posts_1.json"),
            "file_others_posts":
                Path(self.folder, "posts", "other_people's_posts_to_your_timeline.json"),
            "file_notes":
                Path(self.folder, "posts", "notes.json"),
            "file_eventresponse":
                Path(self.folder, "events", "your_event_responses.json"),
            "file_group_membership":
                Path(self.folder, "groups", "your_group_membership_activity.json"),
            "file_group_posts":
                Path(self.folder, "groups", "your_posts_and_comments_in_groups.json"),
            "file_posts_apps":
                Path(self.folder, "apps_and_websites", "posts_from_apps_and_websites.json"),
            "file_event_invites":
                Path(self.folder, "events", "event_invitations.json"),
            "file_liked_pages":
                Path(self.folder, "likes_and_reactions", "pages.json"),
            "file_created_page":
                Path(self.folder, "pages", "your_pages.json"),
            "file_liked_external":
                Path(self.folder, "likes_and_reactions", "likes_on_external_sites.json"),
            "file_profile_update":
                Path(self.folder, "profile_information", "profile_update_history.json"),
            "file_searches":
                Path(self.folder, "search_history", "your_search_history.json"),
            "file_ad_interaction":
                Path(self.folder, "ads", "advertisers_you've_interacted_with.json"),
            "file_poke":
                Path(self.folder, "other_activity", "pokes.json"),
            "file_polls":
                Path(self.folder, "other_activity", "polls_you_voted_on.json"),
            "file_saved_items":
                Path(self.folder, "saved_items_and_collections", "saved_items_and_collections.json"),
            "file_following":
                Path(self.folder, "following_and_followers", "following.json"),
            "file_addressbook":
                Path(self.folder, "about_you", "your_address_books.json"),
            "file_viewed":
                Path(self.folder, "about_you", "viewed.json"),
            "file_visited":
                Path(self.folder, "about_you", "visited.json")
        }

        self.added_friend = self.get_timestamps(files["file_friend_added"])
        self.received_friend_request = self.get_timestamps(files["file_received_friend_request"])
        self.rejected_friend_reject = self.get_timestamps(files["file_rejected_friend_reject"])
        self.removed_friend = self.get_timestamps(files["file_friend_removed"])
        self.installed_app = self.get_timestamps(files["file_app_installs"], "added_timestamp")
        self.apps_posts = self.get_timestamps(files["file_posts_apps"])
        self.commented = self.get_timestamps(files["file_comments"])
        self.reactions = self.get_timestamps(files["file_reactions"])
        self.liked_page = self.get_timestamps(files["file_liked_pages"])
        self.created_page = self.get_timestamps(files["file_created_page"])
        self.liked_external_pages = self.get_timestamps(files["file_liked_external"])
        self.others_posts_timeline = self.get_timestamps(files["file_others_posts"])
        self.created_note = self.get_timestamps(files["file_notes"], "created_timestamp")
        self.responded_event = self.get_timestamps(files["file_eventresponse"], "start_timestamp")
        self.event_invitation = self.get_timestamps(files["file_event_invites"], "start_timestamp")
        self.group_membership_activity = self.get_timestamps(files["file_group_membership"])
        self.group_posts = self.get_timestamps(files["file_group_posts"])
        self.profile_updated = self.get_timestamps(files["file_profile_update"])
        self.searched = self.get_timestamps(files["file_searches"])
        self.ad_interaction = self.get_timestamps(files["file_ad_interaction"])
        self.poked = self.get_timestamps(files["file_poke"])
        self.voted = self.get_timestamps(files["file_polls"])
        self.saved_item = self.get_timestamps(files["file_saved_items"])
        self.followed_sb_st = self.get_timestamps(files["file_following"])
        self.addressbook_entry = self.get_timestamps(files["file_addressbook"], "created_timestamp")

        # These files contain various types of events and require dedicated
        # functions in order to distinguish between those different types
        self.own_posts = self.get_own_posts(files["file_own_posts"])
        self.messages = self.get_messages()
        self.viewed = self.get_viewed(files["file_viewed"])
        self.visited = self.get_visited(files["file_visited"])

    def get_timestamps(self, file_path: Path,
                       timestr: str = "timestamp"
                       ) -> Optional[List[date]]:
        """Extract timestamps from files.

        First, try to get timestamps assuming that they are inside a
        Dict[List[Dict]] structure. This is how most of the files provided
        by Facebook are structured. If that returns an empty list, try again
        assuming a deeper nesting.

        Args:
            filepath (Path): Path to JSON file.
            timestr (str, optional):
                The name of the JSON field with the event timestamps
                varies across the data Facebook provides. Most often
                it is simply "timestamp", but sometimes "crated_timestamp"
                for example. This arg makes sure the right term is used.

        Returns:
            Optional[List[date]]: Lists of timestamps found in the data.
        """
        json_file = self.load_file(file_path)
        if not json_file:
            return None

        # JSON file is a dict structured as:
        # Dict[List[Dict[str, str]]]
        timestamps = [
            datetime.fromtimestamp(item[timestr]).date()
            for value in json_file.values()
            # Unpack list in: Dict[List]
            for item in value
            # Check nested dict in: Dict[List[Dict]]
            if timestr in item
        ]

        if not timestamps:
            # JSON file is a dict structured as:
            # Dict[Dict[List[Dict[str, str]]]]
            timestamps = [
                datetime.fromtimestamp(item[timestr]).date()
                for key in json_file
                for inner_key in json_file.get(key).values()
                for item in inner_key
                if timestr in item
            ]

        if not timestamps:
            print(f"\t-No timestamps found in: {file_path}")
            return None
        return timestamps

    def load_file(self, file_path: Path):  # -> JSON
        """Load data into JSON.

        Returns None is file is not found.

        Args:
            file_path (Path): Path to JSON file.

        Returns:
            JSON: The input file loaded as JSON.
        """
        if not file_path.is_file():
            return None
        with open(file_path) as data_file:
            json_file = json.load(data_file)
        return json_file

    def get_messages(self) -> Optional[Dict[str, List[date]]]:
        """Get timestamps from message files.

        Loops through files in messages folder and collects timestamps
        of each file in a list, categorizing them as "sent" or "received"
        by checking whether self.user matches the field "sender_name"
        inside each JSON file.

        Returns:
            Optional[Dict[str, List[date]]]:
                Dict with lists of timestamps; keys are 'sent'
                and 'received' messages
        """
        # Get list of all message files using rglob. Turn into
        # list to be able to check if empty
        files_messages = list(
            Path(self.folder, "messages").rglob("*.json")
        )
        if not files_messages:
            return None

        messages: Dict[str, List[date]] = {
            "message_sent": [],
            "message_received": []
        }

        for file in files_messages:
            json_file = self.load_file(file)

            messages["message_sent"].extend(
                [
                    datetime.fromtimestamp(message["timestamp_ms"] / 1000).date()
                    for message in json_file["messages"]
                    # Format sender name so it is written just like in the folder
                    if message["sender_name"].replace(" ", "").lower() == self.user
                ]
            )

            messages["message_received"].extend(
                [
                    datetime.fromtimestamp(message["timestamp_ms"] / 1000).date()
                    for message in json_file["messages"]
                    if message["sender_name"].replace(" ", "").lower() != self.user
                ]
            )

        if not messages["message_sent"]:
            # If no sent messages could be detected, it means that the user name wasn't
            # found in message files. If that happens, rename 'message_received' to
            # 'message_received_or_sent' to indicate lack of distinction
            print(
                "No sent messages found, verify if the provided user name is "
                "identical to the name used in Facebook Messenger.\n"
            )
            del messages["message_sent"]
            messages["message_received_or_sent"] = messages.pop("message_received")

        return messages

    def get_own_posts(self, file_path: Path) -> Optional[Dict[str, List[date]]]:
        """Get timestamps for own posts, separated by type of post.

        To determine different types of posts (media, text only, link), turn
        the values of each item inside the JSON file into a string and check
        if the relevant field that identifies the type of post is in that string.
        We do this because the metadata for each post is endlessly nested into
        lists of dicts, so turning that into a string makes it much easier to
        simply detect if a certain field is present.

        Args:
            file_path (Path): Path to JSON file

        Returns:
            Optional[Dict[str, List[date]]]:
                Dict with lists of timestamps, keys are types of posts.
        """
        json_file = self.load_file(file_path)
        if not json_file:
            return None

        posts: Dict[str, List[date]] = {
            "own_posts_all": [],
            "own_posts_media": [],
            "own_posts_text_only": [],
            "own_posts_links": []
        }

        posts["own_posts_all"].extend(
            [
                datetime.fromtimestamp(item["timestamp"]).date()
                for item in json_file
            ]
        )

        posts["own_posts_media"].extend(
            [
                datetime.fromtimestamp(item["timestamp"]).date()
                for item in json_file
                if "media" in str(item.values())
            ]
        )

        posts["own_posts_text_only"].extend(
            [
                datetime.fromtimestamp(item["timestamp"]).date()
                for item in json_file
                if "external_context" not in str(item.values())
                if "media" not in str(item.values())
            ]
        )

        posts["own_posts_links"].extend(
            [
                datetime.fromtimestamp(item["timestamp"]).date()
                for item in json_file
                if "external_context" in str(item.values())
                if "media" not in str(item.values())
            ]
        )

        return posts

    def get_viewed(self, file_path: Path) -> Optional[Dict[str, List[date]]]:
        json_file = self.load_file(file_path)
        if not json_file:
            return None

        views: Dict[str, List[date]] = {
            "viewed_video": [],
            "viewed_article": [],
            "viewed_marketplace_item": []
        }

        # Each video is listed three times in the data: 'time spend', 'shows'
        # and and 'time viewed'. Here we only take the latter as it seems
        # most complete. Moreover, videos are put into categories (e.g.
        # 'Children'). To loop through all categories, we check if the key in
        # the json_file is a list - if is is, it's a category where we pull
        # timestamps from each video using 'time viewed' (at index 2)
        for key in json_file["viewed_things"][0]:  # Videos are at index 0
            if isinstance(json_file["viewed_things"][0][key], list):
                views["viewed_video"].extend(
                    [
                        datetime.fromtimestamp(item["timestamp"]).date()
                        for item in json_file["viewed_things"][0][key][2]["entries"]
                    ]
                )

        # Viewed articles are listed at index 1
        views['viewed_article'].extend(
            [
                datetime.fromtimestamp(item["timestamp"]).date()
                for item in json_file["viewed_things"][1]["entries"]
            ]
        )

        # File structured similar to viewed videos and are at index 2
        # Only difference is that marketplace items are only listed once
        for key in json_file["viewed_things"][2]:  # Videos are at index 0
            if isinstance(json_file["viewed_things"][2][key], list):
                views["viewed_marketplace_item"].extend(
                    [
                        datetime.fromtimestamp(item["timestamp"]).date()
                        for item in json_file["viewed_things"][2][key][0]["entries"]
                    ]
                )

        # Remove keys with no entries
        for key in views:
            if not views[key]:
                del views[key]

        return views

    def get_visited(self, file_path: Path) -> Optional[Dict[str, List[date]]]:
        json_file = self.load_file(file_path)
        if not json_file:
            return None

        visited: Dict[str, List[date]] = {
            "visited_profile": [],
            "visited_page": [],
            "visited_event_page": [],
            "visited_group_page": []
        }

        # Visited profiles are at index 0, pages 1 and so forth
        visited["visited_profile"].extend(
            [
                datetime.fromtimestamp(item["timestamp"]).date()
                for item in json_file["visited_things"][0]["entries"]
            ]
        )

        visited["visited_page"].extend(
            [
                datetime.fromtimestamp(item["timestamp"]).date()
                for item in json_file["visited_things"][1]["entries"]
            ]
        )

        visited["visited_event_page"].extend(
            [
                datetime.fromtimestamp(item["timestamp"]).date()
                for item in json_file["visited_things"][2]["entries"]
            ]
        )

        visited["visited_group_page"].extend(
            [
                datetime.fromtimestamp(item["timestamp"]).date()
                for item in json_file["visited_things"][3]["entries"]
            ]
        )

        # Remove keys with no entries
        for key in visited:
            if not visited[key]:
                del visited[key]

        return visited

    def create_dataframe(self):
        """Combine and count detected events in a Pandas DataFrame.

        Loop through all the relevant attributes of the FacebookQuantifier
        object and build a Pandas DataFrame. Will create a temporary
        DataFrame (df_item) based on the value counts of each data attribute
        and merges them with the main DataFrame df_complete using join(how="outer").

        Returns:
            DataFrame: Pandas DataFrame with dates as index and activities as
                       columns to show how often user did what per day.
        """
        # Create an empty DataFrame which we will expand in each loop
        df_complete = pd.DataFrame()

        # Make a list of the data attributes of the FacebookQuantifier class
        exclude = ["folder", "user"]
        data_points = [
            attribute for attribute in self.__dict__
            if attribute not in exclude
        ]

        for data in data_points:
            attribute = getattr(self, data)
            if attribute:
                if not isinstance(attribute, dict):
                    # If attribute is list, turn into Pandas series, count values
                    # (i.e. how often an event occurred) and use attribute name
                    # as label for column
                    df_item = pd.DataFrame(
                        pd.Series(attribute).value_counts(), columns=[data]
                    )
                    df_item.index.name = "date"
                    df_item = df_item.sort_index()
                    df_complete = df_complete.join(df_item, how="outer")
                else:
                    # If attribute is Dict, add values of each key individually
                    # and use Dict key as label for column
                    for key, value in attribute.items():
                        df_item = pd.DataFrame(
                            pd.Series(value).value_counts(), columns=[key]
                        )
                        df_item.index.name = "date"
                        df_item = df_item.sort_index()
                        df_complete = df_complete.join(df_item, how="outer")

        return df_complete

    def write_csv(self, dataframe=None) -> None:
        """Take Pandas DataFrame and create CSV file.

        Expects a DataFrame based on the object's data.

        Args:
            dataframe (None, optional): A Pandas DataFrame.
        """
        if dataframe is None:
            print("Need a Pandas Dataframe to write data, no CSV file written.")
        else:
            dataframe.to_csv(f"facebook_data_{self.user}.csv")
            print(f"\n- Saved file: facebook_data_{self.user}.csv\n")

    def summarize_data(self) -> None:
        """Report how often each activity was found.

        Loop through data attributes, check if attribute exists.
        If it does, count the number of items in 'data_points'
        list. If it is None, add attribute to 'missing_data' list.
        Print results to give user an overview.
        """
        exclude = ["folder", "user"]
        data_points = [
            data for data in self.__dict__
            if data not in exclude
            if getattr(self, data)
        ]

        missing_data = [
            data for data in self.__dict__
            if data not in exclude
            if not getattr(self, data)
            if not isinstance(getattr(self, data), dict)
        ]

        for data in data_points:
            if not isinstance(getattr(self, data), dict):
                print(
                    f"\t- Number of dates found for {data}: {len(getattr(self, data))}"
                )
            else:
                # If attribute is a dict, length of values
                for item, value in getattr(self, data).items():
                    print(
                        f"\t- Number of dates found for {item}: {len(value)}"
                    )
        if missing_data:
            print(
                "\nNo dates found for the following attributes:\n"
                f"\t - {', '.join(missing_data)}"
                "\nUsually this means that Facebook claims to have no record of them."
            )


def setup():
    """Set up a FacebookQuantifier instance.

    If user input is provided, check it and pass to a FacebookQuantifier
    instance. If no input is provided, scan current directory
    for folders named "facebook-<username>", which is naming scheme
    Facebook uses by default. For each folder detected, use Regex to find
    the user name included in the folder name.

    For each pair of folder + user name, create a FacebookQuantifier
    instance, create a Pandas DataFrame, print out a summary of findings
    and write a CSV file.
    """
    argparser = argparse.ArgumentParser(
        description="""Extracts and quantifies user activity based on the data
        Facebook provides using 'Download Your Information'. If no arguments
        are provided, scans current directory for folders named facebook-<username>.""",
    )
    argparser.add_argument(
        "--folder", help="Path to folder containing Facebook data."
    )
    argparser.add_argument(
        "--user", help="Name of the Facebook user. Used to "
        "distinguish sent and received messages in Facebook messenger."
    )
    args = argparser.parse_args()

    # Check folder(s)
    if args.folder:
        if Path(args.folder).expanduser().is_dir():
            base_folders = [Path(args.folder).expanduser()]
        else:
            print("Specified path is not a folder, please verify.")
            exit()
    else:
        # If no folder provided, scan current directory
        base_folders = [
            folder for folder in Path().iterdir()
            if folder.name.startswith("facebook-")
            if folder.is_dir()
        ]
    if not base_folders:
        print(
            "Could not find folder(s). Either provide path to folder using "
            "--folder='/path/to/folder' or make sure the Facebook data is in "
            "the same folder as the script and named 'facebook-<user name>'."
        )
        exit()

    # Check user name(s)
    if args.user and len(base_folders) > 1:
        print(
            "Multiple data folders found but only one user name provided. "
            "Please specify folder using --folder."
        )
        exit()
    elif args.user and len(base_folders) == 1:
        usernames = [args.user]
    else:
        try:
            # When no user name was provided, try find it in folder name with Regex
            usernames = [
                findall(r"-(.*)", subfolder.name)[0]
                for subfolder in base_folders
            ]
        except IndexError:
            print(
                "Could not find user name in folder name. Please provide "
                "a user name using the --user argument or make sure the folder "
                "is named facebook-<user name> for automatic detection."
            )
            exit()

    # Instantiate FacebookQuantifier, summarize the data found and create CSV
    for folder, user_name in zip(base_folders, usernames):
        print(f"Checking data in folder '{folder}' for '{user_name}'\n")
        facebook_data = FacebookQuantifier(folder, user_name)
        facebook_data.summarize_data()
        df_facebook_data = facebook_data.create_dataframe()
        facebook_data.write_csv(df_facebook_data)


if __name__ == "__main__":
    setup()
