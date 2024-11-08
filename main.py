from auth import *
import feedparser
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost
from wordpress_xmlrpc.methods import posts
import datetime
from io import StringIO
from html.parser import HTMLParser

# Toggle True/false to enable posting to blogs for testing.  Will Still Output to files
runmode = False

cur_date = datetime.datetime.now().strftime(('%A %Y-%m-%d'))
current_time = datetime.datetime.now()

try:
    with open('lastrun.md', 'r') as file:
        last_time = datetime.datetime.strptime(file.read(), "%d-%b-%Y (%H:%M:%S.%f)")
        hours_diff = int((current_time - last_time).total_seconds() / 3600.0)
except:
    hours_diff = 0

if hours_diff < 1:
    hours_diff = 1

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
    #print(feed_url+str(hours_diff))
    NewsFeed = feedparser.parse(feed_url+str(hours_diff))
    return NewsFeed

# Create the post text
def make_post(NewsFeed, cur_blog):
    markdown_output = ""
    # Wordpress API Point
    build_url = f'https://{cur_blog["wp_url"]}/xmlrpc.php'
    #print(build_url)
    wp = Client(build_url, cur_blog["wp_user"], cur_blog["wp_pass"])

    # Create the Basic Post Info, Title, Tags, etc  This can be edited to customize the formatting if you know what you are doing
    post = WordPressPost()
    post.title = f"{cur_date} - Link List"
    post.terms_names = {'category': ['Link List'], 'post_tag': ['links', 'FreshRSS']}
    post.content = f"<p>{cur_blog['blogtitle']} Link List for {cur_date}</p>"
    markdown_output = f"------------------------------------------------------------\n{cur_blog['blogtitle']} Link List for {cur_date}\n------------------------------------------------------------\n\n"
    # Insert Each Feed item into the post with it's posted date, headline, and link to the item.  And a brief summary from the RSS
    for each in NewsFeed.entries:
        try:
            each.media_thumbnail
        except:
            post_thumbnail = cur_blog["placeholder_image"]
        else:
            post_thumbnail = each.media_thumbnail[0]['url']
        #print(post_thumbnail)

        post_content = strip_tags(each.summary)

        if len(post_content) > 100:
            post_summary = post_content[0:100]
        else:
            post_summary = post_content
        post.content += f'<div class="link_list_card">' \
                        f'<div class="link_card_image"><img src="{post_thumbnail}" class="link_card_image_thumb" height="150" alt="link image"></div>' \
                        f'<span class="link_list_date">{each.published[5:-15].replace(" ", "-")}</span> - <a class="link_list_link" href="{each.links[0].href}">{each.title}</a></p>' \
                        f'<p><span class="link_list_summary_title">Brief Summary:</span> <span class="link_list_summary">"{post_summary}"</span></p>' \
                        f'</div>'
        markdown_output += f'{each.published[5:-15].replace(" ", "-")} - [{each.title}]({each.links[0].href})\n\n{post_content}\n\n------------------------------------------------------------\n\n' 
        # print(each.summary_detail.value)
        #print(each)

    if runmode:
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

    with open(f"archive/{cur_date.split(" ")[1]}-Saved_Stories.md", 'a') as filewrite:
        filewrite.write(markdown_output)
        filewrite.write("\n\n\n")


#Get the news feed
for each in blogs:
    newsfeed = get_feed(each["url"])
# If there are posts, make them.
    if len(newsfeed.entries) > 0:
        make_post(newsfeed, each)
        #print(NewsFeed.entries)

if runmode:
    with open('lastrun.md', 'w') as file:
        file.write(current_time.strftime("%d-%b-%Y (%H:%M:%S.%f)"))
