# FreshRSS to Wordpress Digest

This script will take the RSS output feed URL from Fresh RSS and produce a post on a Wordpress blog on whatever Schedule is set by Cron.  It can handle multiple endpoint blogs and provides some CSS elements that can be used to format the links.

A sample of what the final output looks like can be found here:  
[Blogging Intensifies Link List](https://bloggingintensifies.com/category/feeds/link-list/)

## How to Use this Script

* The Script is designed to be run on a regular schedule using cron or whatever time based script system you would like to use.
* The script should work with any RSS feed from Fresh RSS formatted feeds.  IE, the way I use it, is the Tag based feeds, for each of my two blogs.
* You will need to enable XMLRCP if not enabled, i believe this si enabled by default.
* You will need a user to post as on your blog.  This can simply be your normal user log in if you want.
* By default the posts will go into {'category': ['Link List'], 'post_tag': ['links', 'FreshRSS']} on line 45 or so.  This can be changed if desired, just follow the formatting.
* You will need to create a file called auth.py, which is formatted like the following.  You can reduce it to one blog or add more, just adjust the list containing the blogs at the bottom.
```
blog1 = {
    "blogtitle": "YOUR_BLOG_TITLE",
    "url": "FRESH_RSS_FEED_FOR_BLOG",
    "wp_user": "YOUR_USER_NAME",
    "wp_pass": "YOUR_PASSWORD",
    "wp_url": "WORDPRESS URL", # Just the url.com no https or slashes
    "placeholder_image": "", # Full URL
}

blog2 = {
    "blogtitle": "YOUR_BLOG_TITLE",
    "url": "FRESH_RSS_FEED_FOR_BLOG", # The hours number is how far back it will pull
    "wp_user": "YOUR_USER_NAME",
    "wp_pass": "YOUR_PASSWORD",
    "wp_url": "WORDPRESS URL", # Just the url.com no https or slashes
    "placeholder_image": "", # Full URL
}

blogs = [blog1, blog2]  # Continue the list for more blogs
```

* For a daily post, change the "hours" part fo the feed URL to "24"
* To format the cards you can add custom CSS to your Wordpress file, a simple sample is below
```
.link_list_card {
border-style: solid;
margin: 20px;
padding: 10px;
background-color: lightgray;
}

.link_list_summary_title {
font-style: italic;
}

.link_list_date {
font-style: italic;
font-weight: bold;
}

.link_list_link {
font-weight: bold;
}

.link_card_image {

}

.link_card_image_thumb {

}
```

