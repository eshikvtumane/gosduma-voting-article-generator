import requests


class Entry(object):
    def __init__(self, api):
        self._api = api

    def create(self, title, text, subsite_id, attachments):
        headers = self._api.generate_headers({'Content-Type': 'multipart/form-data'})
        requests.post('', data={}, headers=headers)


class TjApi(object):
    def __init__(self, token):
        self._token = token
        self.API_VERSION = '1.6'

    @property
    def url(self):
        return 'https://api.tjournal.ru/v%s/' % self.API_VERSION

    def generate_headers(self, headers={}):
        headers['X-Device-Token'] = self._token
        return headers

    def get_request(self, url, headers={}):
        headers = self.generate_headers(headers)
        requests.get(url, headers=headers)

    def account_info(self):
        url = self.url + 'account/info'
        headers = self.generate_headers()
        print(requests.get(url, headers=headers, params={'user_id': 1}).json())

    def subsites_list(self):
        url = self.url + 'subsites_list/sections'
        headers = self.generate_headers()
        return requests.get(url, headers=headers).json()

    def user_subsite(self):
        url = self.url + 'user/me/subscriptions/subscribed'
        headers = self.generate_headers()
        return requests.get(url, headers=headers).json()

    def subsite(self, subsite_id):
        url = self.url + 'subsite/%s' % subsite_id
        headers = self.generate_headers()
        return requests.get(url, headers=headers).json()

    def create_entry(self, title, content, subsite_id, attachments=None, entry=None):
        url = self.url + 'entry/create'
        headers = self.generate_headers()
        # headers['Content-Type'] = 'multipart/form-data'
        if attachments:
            return requests.post(url, data={'title': title, 'text': content, 'subsite_id': subsite_id, 'attachments': attachments}, headers=headers).json()
        else:
            return requests.post(url, data={'title': title, 'text': content, 'subsite_id': subsite_id, 'entry': entry}, headers=headers).json()

    def uploader_upload(self, file_path):
        url = self.url + 'uploader/upload'
        headers = self.generate_headers()
        return requests.post(url, files={'file': open(file_path, 'rb')}, headers=headers).json()

    def get_image_block(self, title, author, image, cover=False):
        return {
            "type": "media",
            "data": {
                "items": [
                    {
                        "title": title,
                        "author": author,
                        "image": image,
                    }
                ],
                "with_background": False,
                "with_border": False
            },
            "cover": cover,
            "anchor": "",
        }

