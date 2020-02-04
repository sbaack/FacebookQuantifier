# FacebookQuantifier

Facebook allows users to get a copy of their own data, which provides an overview of their activities on the platform: postings, photo uploads, 'Likes' and more. While you can download this data in a structured, machine readable format (JSON), it does not allow you to easily gain an aggregated, birds-eye view of your Facebook activity over time.

This is a problem because Facebook itself and advertisers that target us are usually not interested in us as a person and won't necessarily look into our individual actions. They are interested in our aggregated 'data double': an assemblage of data points about us that allow others to classify us in order to [predict and influence our future behavior](https://www.theguardian.com/technology/2019/jan/20/shoshana-zuboff-age-of-surveillance-capitalism-google-facebook). Not knowing how we are being classified [undermines informed consent and our agency as individuals and collectives](http://eprints.lse.ac.uk/89511/1/Couldry_Data-colonialism_Accepted.pdf).

FacebookQuantifier gives you a small glimpse of your data double on Facebook. It scans the data provided by Facebook and counts your activities over time, e.g. when and how often you 'liked' something. It creates a spreadsheet (CSV format) that is easy to analyze and/or visualize. Here is a truncated preview:

| date       | friend_added | profile_update | message_sent | message_received | ... |
|:-----------|:-------------|:---------------|:-------------|:-----------------|:----|
| 2009-05-31 | 3            |                |              |                  | ... |
| 2009-07-05 |              | 4              |              | 1                | ... |
| 2010-11-12 |              |                | 15           | 13               | ... |
| ...        | ...          | ...            | ...          | ...              | ... |

The overview you gain with FacebookQuantifier will help you understand how your usage of Facebook changed over time, but it also illustrates how little Facebook is willing to give away to empower its users. The information you can download by no means [contains everything Facebook knows about you](https://www.wired.com/story/whats-not-included-in-facebooks-download-your-data/), nor does it show you what information Facebook and others might gain by linking your profile information with other data points. In short, Facebook shows you what you did on its platform, but reveals almost no information that would help you understand how your data is being used.

This project is inspired by [Hang Do Thi Duc's work](https://22-8miles.com/), especially [me and my facebook data](http://myfbdata.schloss-post.com/), [Fuzzify.me](https://chupadados.codingrights.org/en/fuzzifyme/) and [Data Selfie](https://dataselfie.it/#/about). I highly recommended to take a closer look at these projects.

**This tool does not share your Facebook data with anyone! FacebookQuantifier reads your downloaded Facebook data locally, it does not rely on submitting any information to online services.**

## How to use

#### 1. Download your data from Facebook

On [Facebook.com](https://www.facebook.com/), go to Settings -> Your Facebook Information -> Download Your Information. Choose 'JSON' as the format and click 'Create File'. Facebook will then start preparing your download and informs you when it is ready. The data is provided as a zip file.

#### 2. Install FacebookQuantifier

You'll need [Python](https://www.python.org/) 3.5 or newer. Once Python is ready, clone this repository:

```sh
> git clone https://github.com/sbaack/FacebookQuantifier
```

[Pandas](https://pandas.pydata.org/) is required. Install this dependency from the `requirements.txt` file (preferably in a virtual environment):

```sh
> pip install -r requirements.txt
```

#### 3. Run FacebookQuantifier

The easiest way to use this tool is to extract the zip file provided by Facebook into the cloned repository and run `python -m facebook_quantifier`, which will give you an output similar to this:

```sh
❯ python -m facebook_quantifier
Checking data in folder 'facebook-exampleuser' for 'exampleuser'

	- Number of dates found for added_friend: 65
	- Number of dates found for received_friend_request: 8
	- Number of dates found for rejected_friend_reject: 65
	- Number of dates found for removed_friend: 120
	- Number of dates found for installed_app: 4
	- Number of dates found for apps_posts: 13
	- Number of dates found for commented: 666
	- Number of dates found for reactions: 3000
	- Number of dates found for liked_page: 54
	- Number of dates found for liked_external_pages: 8
	- Number of dates found for others_posts_timeline: 454
	- Number of dates found for notes: 6
	- Number of dates found for responded_events: 44
	- Number of dates found for event_invitations: 139
	- Number of dates found for group_membership_activity: 14
	- Number of dates found for group_posts: 81
	- Number of dates found for profile_updated: 66
	- Number of dates found for searches: 5
	- Number of dates found for ad_interaction: 1
	- Number of dates found for poke: 9
	- Number of dates found for saved_item: 77
	- Number of dates found for addressbook_entry: 11
	- Number of dates found for own_posts_all: 3000
	- Number of dates found for own_posts_media: 1000
	- Number of dates found for own_posts_text_only: 1000
	- Number of dates found for own_posts_links: 1000
	- Number of dates found for message_sent: 7647
	- Number of dates found for message_received: 8979

No dates found for the following attributes:
	 - created_page, followed_sb_st
Usually this means that Facebook claims to have no record of them.

- Saved file: facebook_data_exampleuser.csv
```

As you can see, FacebookQuantifier will produce a report detailing what activities were found and how often. It will also create a new CSV file named `facebook_data_<your user name>` which you can use for analysis/data visualization.

If you encounter problems, you might have to specify the location of the data folder and your user name:

```sh
python -m facebook_quantifier --folder="/path/to/facebook-<user name>" --user="your user name"
```

## What exactly is FacebookQuantifier doing? What does it need the Facebook user name for?

Inside the JSON data provided by Facebook, each activity has its own timestamp (i.e. date) to document when a user posted or 'liked' something, joined a group and more. FacebookQuantifier scans a list of pre-defined files for those timestamps and aggregates them by day. For example, if it found three different Facebook 'Likes' made on January 20, 2020, those three Likes will be shown in the final CSV spreadsheet as previewed above.

The Facebook user name is used to distinguish between messages sent versus messages received in Facebook Messenger. For each message, Facebook mentions the 'sender name'. If this name matches the name provided to FacebookQuantifier, the message is counted as a sent message. If you don't provide a user name manually (with the `--user` argument), FacebookQuantifier automatically tries to use the name contained in the name of the Facebook data folder, which is named `facebook-<user name>` by default.

If the user name cannot be found in any message, FacebookQuantifier will just return a count of all messages (named 'message_received_or_sent' in the spreadsheet). If that happens, make sure the user name provided to FacebookQuantifier is identical to how it appears in the 'message_1.json' files inside the 'messages' subfolder.

## What data is captured?

The following activities are captured. For an overview of the data Facebook provides, see <https://www.facebook.com/help/930396167085762>.

| Item                      | Description                                                             |
|:--------------------------|:------------------------------------------------------------------------|
| ad_interaction            | User clicked on an ad                                                   |
| added_friend              | User connected with someone on Facebook                                 |
| received_friend_request   | User received pending friend request                                    |
| rejected_friend_reject    | User rejected friend request                                            |
| removed_friend            | User removed friend                                                     |
| apps_posts                | Installed Facebook app posted on the user's timeline                    |
| commented                 | User commented on posts from friends. Note: Includes photos             |
| event_invitation          | User received event invitation                                          |
| group_membership_activity | User interacted with group (e.g. by joining them)                       |
| group_posts               | User posted in group                                                    |
| installed_app             | User installed a Facebook app                                           |
| liked_external_pages      | User clicked the 'Like' button on external site                         |
| liked_page                | User liked a Facebook page                                              |
| created_page              | User created a Facebook page                                            |
| created_note              | User created a note (similar to pinned posts on timeline)               |
| others_posts_timeline     | Others posted on the user's timeline                                    |
| profile_updated           | User updated profile                                                    |
| reactions                 | User 'reacted' with 'Like' or other similar action                      |
| responded_event           | User responded to event (e.g. 'going')                                  |
| searched                  | User searched something on Facebook                                     |
| poked                     | User 'poked' someone                                                    |
| saved_item                | User 'saved' a post or other item                                       |
| followed_sb_st            | User followed somebody or something                                     |
| addressbook_entry         | User added someone to Facebook address book                             |
| own_posts                 | User posted on own timeline. Distinguishes between:                     |
|                           | - 'own_posts_all' (total count)                                         |
|                           | - 'own_posts_media' (photos and videos only)                            |
|                           | - 'own_posts_text_only' (no links or media)                             |
|                           | - 'own_posts_links' (links or links + text)                             |
| messages                  | Distinguishes between:                                                  |
|                           | - 'sent_message'                                                        |
|                           | - 'received_message'                                                    |
|                           | When user name wasn't found, 'message_received_or_sent' is used instead |

## What is not captured?

I developed this tool using two different data sets: my own Facebook data and that of someone else who kindly allowed me to use it for development. Because neither me, nor the other person used all of Facebook's features, I don't have a copy of all the data points Facebook might provide. The following is missing (and I might miss some more I'm unaware of):

- location
- marketplace
- payment_history
- portal
- stories
- your_places

If you have a copy often this data, feel free to submit a pull request. Alternatively, you can also share a copy of these files with me - preferably only a section of it with fake information. I only need to see how the data is structured.

Beside that, some details are deliberately excluded, but might be added later:

- FacebookQuantifier currently does not collect instances where users updated their posts, notes or other items. Only creation dates are captured
- The date when the user registered her Facebook account is not captured separately
- 'Security and login information' are ignored. For an analysis of that, check out [me and my facebook data](http://myfbdata.schloss-post.com/)