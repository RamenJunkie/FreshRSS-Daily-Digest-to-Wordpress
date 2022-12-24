from auth import *
import feedparser
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost
from wordpress_xmlrpc.methods import posts
import datetime
from io import StringIO
from html.parser import HTMLParser

blogtitle = "Blogging Intensifies"
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
def make_post(NewsFeed):
    # Wordpress API Point
    wp = Client(f'https://{wp_url}/xmlrpc.php', wp_user, wp_pass)

    # Create the Basic Post Info, Title, Tags, etc  This can be edited to customize the formatting if you know what you are doing
    post = WordPressPost()
    post.title = f"{cur_date} - Link List"
    post.terms_names = {'category': ['Link List'], 'post_tag': ['links', 'FreshRSS']}
    post.content = f"<p>{blogtitle} Link List for {cur_date}</p>"
    # Insert Each Feed item into the post with it's posted date, headline, and link to the item.  And a brief summary from the RSS
    for each in NewsFeed.entries:
        post_summary = strip_tags(each.summary)
        post.content += f'{each.published[5:-15].replace(" ", "-")} - <a href="{each.links[0].href}">{each.title}</a></p>' \
                        f'<p>Brief Summary: "{post_summary}"</p>'
        # print(each.summary_detail.value)

    # Create the actual post.
    post.post_status = 'publish'
    #print(post.content)
    # For Troubleshooting and reworking, uncomment the above then comment out the below, this will print results instead of posting
    post.id = wp.call(NewPost(post))
    # print(post.content)

    # try:
    #     if post.id:
    #         post.post_status = 'publish'
    #         call(posts.EditPost(post.id, post))
    # except:
    #     print("Error creating post.")

#Get the news feed
NewsFeed = get_feed(freshrss_url)
# If there are posts, make them.
if len(NewsFeed.entries) > 0:
    make_post(NewsFeed)
    #print(NewsFeed.entries)