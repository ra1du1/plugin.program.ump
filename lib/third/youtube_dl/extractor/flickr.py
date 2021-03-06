from __future__ import unicode_literals

from .common import InfoExtractor
from ..compat import compat_urllib_parse_urlencode
from ..utils import (
    ExtractorError,
    int_or_none,
    qualities,
)


class FlickrIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.|secure\.)?flickr\.com/photos/[\w\-_@]+/(?P<id>\d+)'
    _TEST = {
        'url': 'http://www.flickr.com/photos/forestwander-nature-pictures/5645318632/in/photostream/',
        'md5': '164fe3fa6c22e18d448d4d5af2330f31',
        'info_dict': {
            'id': '5645318632',
            'ext': 'mpg',
            'description': 'Waterfalls in the Springtime at Dark Hollow Waterfalls. These are located just off of Skyline Drive in Virginia. They are only about 6/10 of a mile hike but it is a pretty steep hill and a good climb back up.',
            'title': 'Dark Hollow Waterfalls',
            'duration': 19,
            'timestamp': 1303528740,
            'upload_date': '20110423',
            'uploader_id': '10922353@N03',
            'uploader': 'Forest Wander',
            'comment_count': int,
            'view_count': int,
            'tags': list,
        }
    }

    _API_BASE_URL = 'https://api.flickr.com/services/rest?'

    def _call_api(self, method, video_id, api_key, note, secret=None):
        query = {
            'photo_id': video_id,
            'method': 'flickr.%s' % method,
            'api_key': api_key,
            'format': 'json',
            'nojsoncallback': 1,
        }
        if secret:
            query['secret'] = secret
        data = self._download_json(self._API_BASE_URL + compat_urllib_parse_urlencode(query), video_id, note)
        if data['stat'] != 'ok':
            raise ExtractorError(data['message'])
        return data

    def _real_extract(self, url):
        video_id = self._match_id(url)

        api_key = self._download_json(
            'https://www.flickr.com/hermes_error_beacon.gne', video_id,
            'Downloading api key')['site_key']

        video_info = self._call_api(
            'photos.getInfo', video_id, api_key, 'Downloading video info')['photo']
        if video_info['media'] == 'video':
            streams = self._call_api(
                'video.getStreamInfo', video_id, api_key,
                'Downloading streams info', video_info['secret'])['streams']

            preference = qualities(
                ['288p', 'iphone_wifi', '100', '300', '700', '360p', 'appletv', '720p', '1080p', 'orig'])

            formats = []
            for stream in streams['stream']:
                stream_type = str(stream.get('type'))
                formats.append({
                    'format_id': stream_type,
                    'url': stream['_content'],
                    'preference': preference(stream_type),
                })
            self._sort_formats(formats)

            owner = video_info.get('owner', {})

            return {
                'id': video_id,
                'title': video_info['title']['_content'],
                'description': video_info.get('description', {}).get('_content'),
                'formats': formats,
                'timestamp': int_or_none(video_info.get('dateuploaded')),
                'duration': int_or_none(video_info.get('video', {}).get('duration')),
                'uploader_id': owner.get('nsid'),
                'uploader': owner.get('realname'),
                'comment_count': int_or_none(video_info.get('comments', {}).get('_content')),
                'view_count': int_or_none(video_info.get('views')),
                'tags': [tag.get('_content') for tag in video_info.get('tags', {}).get('tag', [])]
            }
        else:
            raise ExtractorError('not a video', expected=True)
