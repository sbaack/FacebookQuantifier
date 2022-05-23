# FacebookQuantifier

FacebookQuantifier scans the data provided by Facebook under Settings -> Your Facebook Information -> Download Your Information and counts your activities over time, e.g. when and how often you 'liked' something. It creates a spreadsheet (CSV format) that is easy to analyze and/or visualize. Here is a truncated preview:

| date       | friend_added | profile_update | message_sent | message_received | ... |
|:-----------|:-------------|:---------------|:-------------|:-----------------|:----|
| 2009-05-31 | 3            |                |              |                  | ... |
| 2009-07-05 |              | 4              |              | 1                | ... |
| 2010-11-12 |              |                | 15           | 13               | ... |
| ...        | ...          | ...            | ...          | ...              | ... |

The purpose of FacebookQuantifier is twofold:

1. Document and understand what data Facebook allows its users to see and, more importantly, what it withholds. The data you can download by no means [contains everything Facebook knows about you](https://www.wired.com/story/whats-not-included-in-facebooks-download-your-data/), nor does it show you what information Facebook and others might gain by linking your profile information with other data points. Facebook itself and advertisers that target us are usually not interested in us individually. The value of data is "social-relational and not individual" ([Singh and Vipra 2019](https://link.springer.com/article/10.1057/s41301-019-00212-5)). In short, Facebook shows us what we did on its platform, but the value of this information is questionable as it reveals almost nothing that would help us understand how our data is being used. This project tries to better understand the limitations of how Facebook provides users their own data.

2. At the same time, FacebookQuantifier give users an aggregated, birds-eye view of their own Facebook usage over time. While you can download your Facebook data in a structured, machine readable format (JSON), it is organized in such a way that you cannot easily get an overview of your activities on the platform. I believe that this is helpful because Facebook and other data-driven companies are constantly trying to manipulate their users to do more on their platforms by inducing [feelings of missing out](https://theconversation.com/redesigning-social-media-platforms-to-reduce-fomo-124228) and designing for more and more engagement. In contrast, the overview gained with FacebookQuantifier can give some agency back to users and help them question what they really need Facebook for. For example, you might see that you have very few conversations with friends and mostly just view videos or click articles posted on pages you follow - perhaps you can drop Facebook altogether and visit the websites of these pages instead?

This project is inspired by [Hang Do Thi Duc's work](https://22-8miles.com/), especially [me and my facebook data](http://myfbdata.schloss-post.com/), [Fuzzify.me](https://chupadados.codingrights.org/en/fuzzifyme/) and [Data Selfie](https://dataselfie.it/#/about). I highly recommended to take a closer look at these projects.

**FacebookQuantifier only reads your downloaded Facebook data locally and does not rely on submitting any information to online services.**

## How to use

#### 1. Download your data from Facebook

On [Facebook.com](https://www.facebook.com/), go to Settings -> Your Facebook Information -> Download Your Information. Choose 'JSON' as the format and click 'Create File'. Facebook will then start preparing your download and informs you when it is ready. The data is provided as a zip file.

#### 2. Install FacebookQuantifier

You'll need [Python](https://www.python.org/) 3.9 or newer. Once Python is ready, clone this repository:

```bash
> git clone https://github.com/sbaack/FacebookQuantifier
```

#### 3. Run FacebookQuantifier

The easiest way to use this tool is to extract the zip file provided by Facebook into the cloned repository and run `python -m facebook_quantifier`. FacebookQuantifier will automatically search for directories named `facebook-<username>`, which is how Facebook names the downloadable archives. If you want to get a quick overview of the information that was gathered you can add the `--verbose` or `-v` flag, which gives you an output similar to this:

```bash
> python -m facebook_quantifier -v
Checking data in folder 'facebook-exampleuser' for 'exampleuser'
Saved file: facebook_data_exampleuser.csv
Found the following number of activities:

- added_friend: 65
- received_friend_request: 8
- rejected_friend_reject: 65
- removed_friend: 120
- installed_app: 4
- apps_posts: 13
- commented: 666
- reactions: 3000
- liked_page: 54
- liked_external_pages: 8
- notes: 6
- responded_events: 44
- event_invitations: 139
- group_membership_activity: 14
- group_posts: 81
- profile_updated: 66
- searches: 5
- ad_interaction: 1
- poke: 9
- saved_item: 77
- addressbook_entry: 11
- own_posts_all: 3000
- own_posts_media: 1000
- own_posts_text_only: 1000
- own_posts_links: 1000
- message_sent: 7647
- message_received: 8979
- viewed_video: 9
- viewed_article: 56
- viewed_marketplace_item: 3
- visited_profile: 21
- visited_page: 13
- visited_event_page: 204
- visited_group_page: 8
- clicked_menu_items: 27
```

A new CSV file named `facebook_data_<your user name>.csv` will be created that can be used for further analysis or data visualizations.

You can also specify the location of the data folder and your user name:

```bash
> python -m facebook_quantifier --folder "/path/to/facebook-<user name>" --user "your user name"
```

## What exactly is FacebookQuantifier doing? What does it need the Facebook user name for?

Inside the JSON data provided by Facebook, each activity has its own timestamp (i.e. date) to document when a user posted or 'liked' something, joined a group and more. FacebookQuantifier scans a list of pre-defined files for those timestamps and aggregates them by day. For example, if it finds three different Facebook 'Likes' made on January 20, 2020, those three Likes are listed in the final CSV spreadsheet as previewed above.

The Facebook user name is used to distinguish between messages sent versus messages received in Facebook Messenger. For each message, Facebook mentions the 'sender name'. If this sender name matches the name used by FacebookQuantifier, the message is counted as a sent message. If you don't provide a user name manually (with the `--user` argument), FacebookQuantifier automatically tries to use the name contained in the name of the Facebook data folder, which is named `facebook-<user name>` by default. 

If the user name cannot be found in any message, FacebookQuantifier will just return a count of all messages (named 'message_received_or_sent' in the spreadsheet). If that happens, make sure the user name provided to FacebookQuantifier is identical to how it appears in the 'message_1.json' files inside the 'messages' subfolder.

## What data is captured?

Facebook is constantly changing what information is included in the downloadable archive and how it is structured. Since the first publication of the FacebookQuantifier, [several data points have been changed or removed](#changes-to-the-data-provided-by-facebook). For an overview of the data Facebook provides, see <https://www.facebook.com/help/930396167085762>. At the moment, FacebookQuantifier scans for the following data points, some of which are only available in older versions of the downloadable archive:

| Item                      | Description                                                                |
|:--------------------------|:---------------------------------------------------------------------------|
| ad_interaction            | User clicked on an ad                                                      |
| added_friend              | User connected with someone on Facebook                                    |
| received_friend_request   | User received pending friend request                                       |
| rejected_friend_reject    | User rejected friend request                                               |
| removed_friend            | User removed friend                                                        |
| apps_posts                | Installed Facebook app posted on the user's timeline                       |
| commented                 | User commented on posts from friends. Note: Includes photos                |
| event_invitation          | User received event invitation                                             |
| group_membership_activity | User interacted with group (e.g. by joining them)                          |
| group_posts               | User posted in group                                                       |
| installed_app             | User installed a Facebook app                                              |
| liked_external_pages      | User clicked the 'Like' button on external site                            |
| liked_page                | User liked a Facebook page                                                 |
| created_page              | User created a Facebook page                                               |
| created_note              | User created a note (similar to pinned posts on timeline)                  |
| others_posts_timeline     | Others posted on the user's timeline                                       |
| profile_updated           | User updated profile                                                       |
| reactions                 | User 'reacted' with 'Like' or other similar action                         |
| responded_event           | User responded to event (e.g. 'going')                                     |
| searched                  | User searched something on Facebook                                        |
| poked                     | User 'poked' someone                                                       |
| saved_item                | User 'saved' a post or other item                                          |
| followed_sb_st            | User followed somebody or something                                        |
| addressbook_entry         | User added someone to Facebook address book                                |
| own_posts                 | User posted on own timeline. Distinguishes between:                        |
|                           | - 'own_posts_all' (total count)                                            |
|                           | - 'own_posts_media' (photos and videos only)                               |
|                           | - 'own_posts_text_only' (no links or media)                                |
|                           | - 'own_posts_links' (links or links + text)                                |
| messages                  | Distinguishes between:                                                     |
|                           | - 'sent_message'                                                           |
|                           | - 'received_message'                                                       |
|                           | When user name wasn't found, 'message_received_or_sent' is used instead    |
| viewed                    | Various items viewed on Facebook. Distinguishes between:                   |
|                           | - viewed_video                                                             |
|                           | - viewed_article                                                           |
|                           | - viewed_marketplace_item                                                  |
| visited                   | Various user profiles or pages visited by the user. Distinguishes between: |
|                           | - visited_profile                                                          |
|                           | - visited_page                                                             |
|                           | - visited_event_page                                                       |
|                           | - visited_group_page                                                       |
| menu_items                | User clicked an item in the user interface                                 |

## Changes to the data provided by Facebook

### Update May 2020

At some point after January 2020, Facebook removed the file 'other_people's_posts_to_your_timeline.json', which contained information about other people's post on your own timeline from the downloadable archive. This information is now only available online in [Facebook's Activity Log](https://www.facebook.com/me/allactivity). If you're lucky enough to have a copy of your data from January 2020 or earlier, make sure to keep this data. I decided to keep the code to parse this information.

On the other hand, Facebook added new data. Relevant for this tool are:

- 'Recent' interactions with people
- Clicked menu items
- Viewed videos, articles, marketplace items
- Visited profiles and pages

Unfortunately, the list of recent interactions with people is no replacement for the removed data. Indeed, it is so unclear what it means that I decided not to parse it (see 'What is not captured?' below). The new data about clicked menu items and visited profiles and pages is confusing as well. Some of the items listed in clicked menu items are Facebook pages or group pages, but their timestamps cannot be found in my visited.json file. Did I click the item without visiting the page? What counts as 'visited' when clicking a menu item to open a Facebook page does not automatically count as a visit? I added the timestamps in those files to the spreadsheet, but more research is needed to really understand what it means.

## What is not captured?

**Deliberately excluded**

- 'Security and login information' are ignored. For an analysis of that, check out [me and my facebook data](http://myfbdata.schloss-post.com/).
- FacebookQuantifier currently does not collect instances where users updated their posts, notes or other items. Only creation dates are captured. Might be added later.
- People 'interactions': It is unclear what exactly is captured in the file interactions/people.json. Facebook describes it as "People and friends you've interacted with recently, including comments and reactions.". However, it is unclear what interactions are included beside comments and reactions and what is missing. Moreover, I found that some of this information is duplicated in comments.json. Because of these uncertainties and the fact that at least in my own data, this list was very short, I decided not to parse it.
- The date when the user registered her Facebook account is not captured separately.

**Missing data in my sample**

Due to privacy reasons, I developed this tool using only a handful of data sets (including my own Facebook data). Because neither me, nor the other data sets I used contain of all the data points Facebook might provide, the following is missing (and I might miss some more I'm unaware of):

- location
- marketplace
- payment_history
- portal
- stories
- your_places

If you have a copy often this data, feel free to submit a pull request. Alternatively, you can also share a copy of these files with me - preferably only a section of it with fake information. I only need to see how the data is structured.
