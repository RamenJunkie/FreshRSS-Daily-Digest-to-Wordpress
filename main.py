from auth import *
import feedparser
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost
from wordpress_xmlrpc.methods import posts
import datetime
from io import StringIO
from html.parser import HTMLParser

cur_date = datetime.datetime.now().strftime(('%A %Y-%m-%d'))

### HTML Stripper from https://stackoverflow.com/questions/753052/strip-html-from-strings-in-python
class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.text = StringIO()
    def handle_data(self, d):
        self.text.write(d)
    def get_data(self):
        return self.text.getvalue()

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

# Get News Feed
def get_feed(feed_url):
    NewsFeed = feedparser.parse(feed_url)
    return NewsFeed

# Create the post text
def make_post(NewsFeed, cur_blog):
    # Wordpress API Point
    build_url = f'https://{cur_blog["wp_url"]}/xmlrpc.php'
    #print(build_url)
    wp = Client(build_url, cur_blog["wp_user"], cur_blog["wp_pass"])

    # Create the Basic Post Info, Title, Tags, etc  This can be edited to customize the formatting if you know what you are doing
    post = WordPressPost()
    post.title = f"{cur_date} - Link List"
    post.terms_names = {'category': ['Link List'], 'post_tag': ['links', 'FreshRSS']}
    post.content = f"<p>{cur_blog['blogtitle']} Link List for {cur_date}</p>"
    # Insert Each Feed item into the post with it's posted date, headline, and link to the item.  And a brief summary from the RSS
    for each in NewsFeed.entries:
        try:
            each.media_thumbnail
        except:
            post_thumbnail = cur_blog["placeholder_image"]
        else:
            post_thumbnail = each.media_thumbnail[0]['url']
        #print(post_thumbnail)

        if len(strip_tags(each.summary)) > 100:
            post_summary = strip_tags(each.summary)[0:100]
        else:
            post_summary = strip_tags(each.summary)
        post.content += f'<div class="link_list_card">' \
                        f'<div class="link_card_image"><img src="{post_thumbnail}" class="link_card_image_thumb" height="150" alt="link image"></div>' \
                        f'<span class="link_list_date">{each.published[5:-15].replace(" ", "-")}</span> - <a class="link_list_link" href="{each.links[0].href}">{each.title}</a></p>' \
                        f'<p><span class="link_list_summary_title">Brief Summary:</span> <span class="link_list_summary">"{post_summary}"</span></p>' \
                        f'</div>'
        # print(each.summary_detail.value)
        #print(each)

    # Create the actual post.
    post.post_status = 'publish'
    #print(post.content)
    # For Troubleshooting and reworking, uncomment the above then comment out the below, this will print results instead of posting
    post.id = wp.call(NewPost(post))

    try:
        if post.id:
            post.post_status = 'publish'
            call(posts.EditPost(post.id, post))
    except:
        pass
        #print("Error creating post.")

#Get the news feed
for each in blogs:
    newsfeed = get_feed(each["url"])
# If there are posts, make them.
    if len(newsfeed.entries) > 0:
        make_post(newsfeed, each)
        #print(NewsFeed.entries)

