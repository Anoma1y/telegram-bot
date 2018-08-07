import requests
from datetime import datetime
import time

url = 'https://yande.re/'
LIMIT_FILE_SIZE = 5000000


def pull_tags(page, limit, order, name):
    params = {
        'page': page,
        'limit': limit,
        'order': order,
        'name': name
    }

    response = requests.get(url + 'tag.json', params=params)
    return response.json()


def pull_images(page, page_limit, tags):
    params = {
        'page': page,
        'limit': page_limit,
    }
    if tags is not None:
        params.update({
            'tags': tags.strip().replace(' ', '+')

        })

    params_fix = "&".join("%s=%s" % (k, v) for k, v in params.items())

    response = requests.get(url + 'post.json', params=params_fix)
    return response.json()


def get_available_tags(tag_name):
    tags_str = ''
    tags = pull_tags(page=1, limit=100, order='count', name=tag_name)
    index = 0

    while index < len(tags):
        if index == (len(tags) - 1):
            tags_str += tags[index]['name']
            break
        tags_str += tags[index]['name'] + ', '
        index = index + 1

    return tags_str.strip()


# ________
# ( lolei? )
#  --------
#         o   ^__^
#          o  (oo)\_______
#             (__)\       )\/\
#                 ||----w |
#                 ||     ||
def get_images(page_limit=10, tags=None, period_time=86400, limit=10):
    current_limit = limit
    unix_secs = time.mktime(datetime.now().timetuple())  # current unix-time
    is_find = True
    page = 1
    images = []

    while is_find:
        json = pull_images(page, page_limit=page_limit, tags=tags)

        if len(json) == 0:
            break

        for item in json:
            item_time = int(unix_secs) - int(item['created_at'])

            if item_time > int(period_time):
                is_find = False
                break

            if item['file_size'] > LIMIT_FILE_SIZE:
                continue

            images.append(item)

            if len(images) >= current_limit:

                print(len(images))
                return images

        page = page + 1
    return images

