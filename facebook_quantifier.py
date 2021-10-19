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
import sys
from datetime import date, datetime  # 'date' used for type hints only
from pathlib import Path
from re import findall
from typing import Optional

import pandas as pd


class FacebookQuantifier():
    """Extract and quantify events in user data provided by Facebook.

    To count user activity, this class extracts timestamps found in a pre-
    defined list of files contained in the Facebook data, marking the date
    of varies user activities. See the list of data attributes below for
    a full overview. Note that Facebook is continuously changing what
    information is available in the downloadable archive and some of these
    data attributes are only available in older versions of the archive.

    Attributes (required to instantiate object):
        folder : Path
            Folder that contains the data provided by Facebook
        user : str
            Name of the Facebook user

    Possible data attributes (automatically generated upon instantiation):
        ad_interaction: list[date]
            User clicked on an ad
        added_friend : list[date]
            User connected with someone on Facebook
        received_friend_request : list[date]
            User received friend request
            Note: Only pending requests which have not been accepted
        rejected_friend_reject : list[date]
            User rejected friend request
        removed_friend : list[date]
            User removed friend
        apps_posts : list[date]
            Installed Facebook app posted on the user's timeline
        commented : list[date]
            User commented on posts from friends
            Note: 'posts' includes photos
        event_invitation : list[date]
            User received event invitation
        group_membership_activity (list[date]):
            User interacted with group (e.g. by joining them)
        group_posts : list[date]
            User posted in group
        installed_app : list[date]
            User installed Facebook apps
        liked_external_pages : list[date]
            User clicked the 'Like' button on external site
        liked_page : list[date]
            User liked a Facebook page
        created_page : list[date]
            User created a Facebook page
        created_note : list[date]
            User created a note (similar to pinned posts on timeline)
        others_posts_timeline : list[date]
            Others posted on the user's timeline
        profile_updated : list[date]
            User updated her profile
        reactions : list[date]
            User 'reacted' with 'Like' or other similar action
        responded_event : list[date]
            User reacted to events (e.g. 'going')
        searched : list[date]
            User searched something on Facebook
        poked : list[date]
            User poked someone
        voted : list[date]
            User voted in a poll
        saved_item : list[date]
            User 'saved' a post or other item
        followed_sb_st : list[date]
            User followed somebody or something
        addressbook_entry : list[date]
            User added someone to Facebook address book
        own_posts : dict[str, list[date]]
            User posted on own timeline. Dict keys are:
                - 'own_posts_all' (anything posted)
                - 'own_posts_media' (photos and videos only)
                - 'own_posts_text_only' (no links or media)
                - 'own_posts_links' (links or links + text)
        messages : dict[str, list[date]]
            Timestamps when user received or sent a message in Facebook messenger.
            Keys are 'sent_message' and 'received_message' unless no sent messages
            could be identified (due to user name not found). If that happens, dict
            has only one key named 'send_or_received'
        viewed : dict[str, list[date]]
            Timestamps when user viewed various items. Possible keys:
                - 'viewed_video'
                - 'viewed_article'
                - 'viewed_marketplace_item'
        visited : dict[str, list[date]]
            Timestamps when user visited other people's profiles or various pages.
            Possible keys:
                - 'visited_profile'
                - 'visited_page'
                - 'visited_event_page'
                - 'visited_group_page'
                - 'visited_marketplace'
        menu_items : list[date]
            Timestamps when user clicked an item in the user interface
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

        self.json_files = list(Path(self.folder).rglob("*.json"))

        for file in self.json_files:
            if file.name == "friends.json":
                self.added_friend = self.get_timestamps(file)
            # File named differently in different versions of the archive
            elif file.name in ["received_friend_requests.json",
                               "friend_requests_received.json"]:
                self.received_friend_request = self.get_timestamps(file)
            elif file.name == "rejected_friend_requests.json":
                self.rejected_friend_reject = self.get_timestamps(file)
            elif file.name == "removed_friends.json":
                self.removed_friend = self.get_timestamps(file)
            elif file.name == "apps_and_websites.json":
                self.installed_app = self.get_timestamps(file, "added_timestamp")
            elif file.name == "comments.json":
                self.commented = self.get_timestamps(file)
            elif file.name == "posts_and_comments.json":
                self.reactions = self.get_timestamps(file)
            elif file.name == "other_people's_posts_to_your_timeline.json":
                self.others_posts_timeline = self.get_timestamps(file)
            # Only available in older versions of the downloaded archive
            elif file.name == "notes.json":
                self.created_note = self.get_timestamps(file, "created_timestamp")
            elif file.name == "your_event_responses.json":
                self.responded_event = self.get_timestamps(file, "start_timestamp")
            elif file.name == "your_group_membership_activity.json":
                self.group_membership_activity = self.get_timestamps(file)
            elif file.name == "your_posts_and_comments_in_groups.json":
                self.group_posts = self.get_timestamps(file)
            elif file.name == "posts_from_apps_and_websites.json":
                self.apps_posts = self.get_timestamps(file)
            elif file.name == "event_invitations.json":
                self.event_invitation = self.get_timestamps(file, "start_timestamp")
            # File named differently in different versions of the archive
            elif file.name in ["pages.json", "pages_you've_liked.json"]:
                self.liked_page = self.get_timestamps(file)
            elif file.name == "your_pages.json":
                self.created_page = self.get_timestamps(file)
            # Only available in older versions of the downloaded archive
            elif file.name == "likes_on_external_sites.json":
                self.liked_external_pages = self.get_timestamps(file)
            elif file.name == "profile_update_history.json":
                self.profile_updated = self.get_timestamps(file)
            elif file.name == "your_search_history.json":
                self.searched = self.get_timestamps(file)
            # Only available in older versions of the downloaded archive
            elif file.name == "advertisers_you've_interacted_with.json":
                self.ad_interaction = self.get_timestamps(file)
            elif file.name == "pokes.json":
                self.poked = self.get_timestamps(file)
            elif file.name == "polls_you_voted_on.json":
                self.voted = self.get_timestamps(file)
            elif file.name == "saved_items_and_collections.json":
                self.saved_item = self.get_timestamps(file)
            # File named differently in different versions of the archive
            elif file.name in ["following.json", "who_you_follow.json"]:
                self.followed_sb_st = self.get_timestamps(file)
            # Only available in older versions of the downloaded archive
            elif file.name == "your_address_books.json":
                self.addressbook_entry = self.get_timestamps(file, "created_timestamp")

            # These files contain various types of events and require dedicated
            # functions in order to distinguish between those different types
            elif file.name == "your_posts_1.json":
                posts = self.get_own_posts(file)
                for post_type, dates in posts.items():
                    if post_type == "own_posts_all":
                        self.own_posts_all = dates
                    if post_type == "own_posts_media":
                        self.own_posts_media = dates
                    if post_type == "own_posts_text_only":
                        self.own_posts_text_only = dates
                    if post_type == "own_posts_links":
                        self.own_posts_links = dates
            # File named differently in different versions of the archive
            elif file.name in ["viewed.json", "recently_viewed.json"]:
                views = self.get_viewed(file)
                for view_type, dates in views.items():
                    if view_type == "viewed_video":
                        self.viewed_video = dates
                    if view_type == "viewed_article":
                        self.viewed_article = dates
                    if view_type == "viewed_marketplace_item":
                        self.viewed_marketplace_item = dates
            # File named differently in different version of the archive
            elif file.name in ["visited.json", "recently_visited.json"]:
                visited = self.get_visited(file)
                for visited_type, dates in visited.items():
                    if visited_type == "visited_profile":
                        self.visited_profile = dates
                    if visited_type == "visted_page":
                        self.visited_page = dates
                    if visited_type == "visited_event_page":
                        self.visited_event_page = dates
                    if visited_type == "visited_group_page":
                        self.visited_group_page = dates
                    if visited_type == "visited_marketplace":
                        self.visited_marketplace = dates
            # Only available in older versions of the downloaded archive
            elif file.name == "menu_items.json":
                self.clicked_menu_items = self.get_menu_items(file)
        # Messages are analyzed separately
        messages = self.get_messages()
        if messages:
            for message_type, dates in messages.items():
                if message_type == "message_sent":
                    self.message_sent = dates
                if message_type == "message_received":
                    self.message_received = dates
                if message_type == "message_received_or_sent":
                    self.message_received_or_sent = dates
        self.write_csv_new()

    def get_timestamps(self, file_path: Path,
                       timestr: str = "timestamp"
                       ) -> Optional[list[date]]:
        """Extract timestamps from files.

        First, try to get timestamps assuming that they are inside a
        dict[list[dict]] structure. This is how most of the files provided
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
            Optional[list[date]]: Lists of timestamps found in the data.
        """
        json_file = self.load_file(file_path)

        # JSON file is a dict structured as:
        # dict[str, list[dict[str, int]]]
        timestamps = [
            datetime.fromtimestamp(item[timestr]).date()
            for value in json_file.values()
            # Unpack list in: dict[str, list]
            for item in value
            # Check nested dict in: dict[str, list[dict]]
            if timestr in item
        ]

        if not timestamps:
            # JSON file is a dict structured as:
            # dict[str, dict[str, list[dict[str, int]]]]
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

    def load_file(self, file_path: Path):
        """Load data into JSON.

        Args:
            file_path (Path): Path to JSON file.

        Returns:
            JSON: The input file loaded as JSON.
        """
        with open(file_path) as data_file:
            return json.load(data_file)

    def get_messages(self) -> Optional[dict[str, list[date]]]:
        """Get timestamps from message files.

        Loops through files in messages folder and collects timestamps
        of each file in a list, categorizing them as "sent" or "received"
        by checking whether self.user matches the field "sender_name"
        inside each JSON file.

        Returns:
            Optional[dict[str, list[date]]]:
                Dict with lists of timestamps; keys are 'sent'
                and 'received' messages
        """
        # Newer versions of downloadable archive include extra files that
        # don't contain information relevant here
        exclude: list[str] = ["autofill_information.json", "secret_groups.json"]
        files_messages: list[Path] = [
            dir for dir in self.json_files
            if Path(self.folder, 'messages') in dir.parents
            if dir.name not in exclude
        ]
        if not files_messages:
            return None

        # To collect items across multiple files, create lists of dict directly
        # and extend them with each file
        messages: dict[str, list[date]] = {
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
            # 'message_received_or_sent' and remove 'messages_sent' to indicate lack
            # of distinction
            print(
                "No sent messages found, verify if the provided user name is "
                "identical to the name used in Facebook Messenger.\n"
            )
            del messages["message_sent"]
            messages["message_received_or_sent"] = messages.pop("message_received")

        return messages

    def get_own_posts(self, file_path: Path) -> dict[str, list[date]]:
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
            dict[str, list[date]]:
                Dict with lists of timestamps, keys are types of posts.
        """
        json_file = self.load_file(file_path)

        posts: dict[str, list[date]] = {}

        posts["own_posts_all"] = [
            datetime.fromtimestamp(item["timestamp"]).date()
            for item in json_file
        ]

        posts["own_posts_media"] = [
            datetime.fromtimestamp(item["timestamp"]).date()
            for item in json_file
            if "media" in str(item.values())
        ]

        posts["own_posts_text_only"] = [
            datetime.fromtimestamp(item["timestamp"]).date()
            for item in json_file
            if "external_context" not in str(item.values())
            if "media" not in str(item.values())
        ]

        posts["own_posts_links"] = [
            datetime.fromtimestamp(item["timestamp"]).date()
            for item in json_file
            if "external_context" in str(item.values())
            if "media" not in str(item.values())
        ]

        return posts

    def get_viewed(self, file_path: Path) -> dict[str, list[date]]:
        """Get timestamps for viewed items, separated by type of item.

        Captures when user viewed a video, an article or marketplace items.
        Note that each video viewed is listed three times in the data: 'time spend',
        'shows' and 'time viewed'. Here we only take the latter as it seems most
        complete. Moreover, videos and marketplace items are put into categories
        (e.g. 'Children'). To loop through all categories, we check if the key in
        the json_file is a list - if is is, it's a category where we pull
        timestamps.

        Args:
            file_path (Path): Path to JSON file

        Returns:
            dict[str, list[date]]:
                Dict with lists of timestamps, keys are types of item viewed.
        """
        json_file = self.load_file(file_path)

        views: dict[str, list[date]] = {}

        # Older versions of the personal data archive used a different key.
        # First check if old key available, otherwise use new key
        if not json_file.get("viewed_things"):
            json_key: str = "recently_viewed"
        else:
            json_key = "viewed_things"

        for category in json_file[json_key]:
            if category['name'] == "Facebook Watch Videos and Shows":
                for watchtype in category['children']:
                    if watchtype['name'] == "Time Viewed":
                        views["viewed_video"] = [
                            datetime.fromtimestamp(item["timestamp"]).date()
                            for item in watchtype['entries']
                        ]
            if category['name'] == "Articles":
                views['viewed_article'] = [
                    datetime.fromtimestamp(item["timestamp"]).date()
                    for item in category["entries"]
                ]
            # "Marketplace" entry only available in older versions of the
            # downloadable archive. Includes views of marketplace items.
            # In newer versions, this information is available in 'recently
            # visted'. Newer versions of the 'viewed' overview also show
            # when a marketplace item was shown on Facebook, regardless of
            # whether the user interacted with it.
            if category['name'] == "Marketplace":
                for market_view in category['children']:
                    views["viewed_marketplace_item"] = [
                        datetime.fromtimestamp(item["timestamp"]).date()
                        for item in market_view['entries']
                    ]
        return views

    def get_visited(self, file_path: Path) -> dict[str, list[date]]:
        """Get timestamps for viewed profiles or page, separated by type of page.

        Args:
            file_path (Path): Path to JSON file

        Returns:
            dict[str, list[date]]:
                Dict with lists of timestamps, keys are types of pages viewed.
        """
        json_file = self.load_file(file_path)

        # Older versions of the personal data archive used a different key.
        # First check if old key available, otherwise use new key
        if not json_file.get("visited_things"):
            json_key: str = "visited_things_v2"
        else:
            json_key = "visited_things"

        visited: dict[str, list[date]] = {}

        for category in json_file[json_key]:
            if category['name'] == "Profile visits":
                visited["visited_profile"] = [
                    datetime.fromtimestamp(item["timestamp"]).date()
                    for item in category["entries"]
                ]
            if category['name'] == "Page visits":
                visited["visited_page"] = [
                    datetime.fromtimestamp(item["timestamp"]).date()
                    for item in category["entries"]
                ]
            if category['name'] == "Events visited":
                visited["visited_event_page"] = [
                    datetime.fromtimestamp(item["timestamp"]).date()
                    for item in category["entries"]
                ]
            if category['name'] == "Groups visited":
                visited["visited_group_page"] = [
                    datetime.fromtimestamp(item["timestamp"]).date()
                    for item in category["entries"]
                ]
            # This information is only available in newer versions of the downloadable
            # archive. Different to other data points, the date is represented as a
            # string formatted as 'Sep 20, 2014', which we're converting here
            if category['name'] == "Marketplace Visits":
                visited["visited_marketplace"] = [
                    datetime.strptime(item['data']['value'], '%b %d, %Y').date()
                    for item in category["entries"]
                ]
        return visited

    def get_menu_items(self, file_path: Path) -> list[date]:
        """Get timestamps for clicked menu items.

        Args:
            file_path (Path): Path to JSON file

        Returns:
            list[date]:
                List of timestamps
        """
        json_file = self.load_file(file_path)

        return [
            datetime.fromtimestamp(item["timestamp"]).date()
            for item in json_file['menu_items'][0]['entries']
        ]

    def create_dataframe(self) -> pd.DataFrame:
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
        exclude: list[str] = ["folder", "user", "json_files"]
        data_points: list[str] = [
            attribute for attribute in self.__dict__
            if attribute not in exclude
        ]

        for data in data_points:
            attribute = getattr(self, data)
            if attribute:
                # Turn each list into Pandas series, count values (i.e. how often
                # an event occurred) and use attribute name as label for column
                df_item = pd.DataFrame(
                    pd.Series(attribute).value_counts(), columns=[data]
                )
                df_item.index.name = "date"
                df_item = df_item.sort_index()
                df_complete = df_complete.join(df_item, how="outer")

        return df_complete

    def write_csv(self, dataframe: pd.DataFrame = None) -> None:
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
        exclude = ["folder", "user", "json_files"]
        data_points = [
            data for data in self.__dict__
            if data not in exclude
            if getattr(self, data)
        ]

        for data in data_points:
            print(
                f"\t- Number of dates found for {data}: {len(getattr(self, data))}"
            )


def setup() -> None:
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
            sys.exit()
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
        sys.exit()

    # Check user name(s)
    if args.user and len(base_folders) > 1:
        print(
            "Multiple data folders found but only one user name provided. "
            "Please specify folder using --folder."
        )
        sys.exit()
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
            sys.exit()

    # Instantiate FacebookQuantifier, summarize the data found and create CSV
    for folder, user_name in zip(base_folders, usernames):
        print(f"Checking data in folder '{folder}' for '{user_name}'\n")
        facebook_data = FacebookQuantifier(folder, user_name)
        facebook_data.summarize_data()
        df_facebook_data = facebook_data.create_dataframe()
        facebook_data.write_csv(df_facebook_data)


if __name__ == "__main__":
    setup()
