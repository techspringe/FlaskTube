import math
from concurrent.futures.thread import ThreadPoolExecutor
import pytube
from flask import Blueprint, request, jsonify, abort
from urllib import parse

api = Blueprint("api", __name__)
workers = 10


@api.route('/single', methods=["GET"])
def accept_single_video():
    """
    Get request from user and checks for missing key values
    :return: json data of request (object)
    """
    if request.method == 'GET':
        url = request.args.get('url')
        if url is None:
            return jsonify(error="Youtube Link Not Found")
        else:
            if "list" in url:
                return jsonify(
                    error="Only Single Videos Are Allowed In This Section. So Please Goto The Playlist Section")
            if "v" not in url:
                return jsonify(error="Youtube Link You Inserted Is Incorrect")

            # threading workers for faster response on server
            with ThreadPoolExecutor(max_workers=workers) as executor:
                future = executor.submit(_process_single_video, url)
            return jsonify(future.result())
    abort(status=403)


def _process_video_size(video_size):
    num_bytes_in_megabyte = math.pow(10, 6)
    file_size_in_megabyte = math.ceil(video_size / num_bytes_in_megabyte)
    return file_size_in_megabyte


def _populate_playlist_urls(url):
    """
    populating [ ] with youtube individual links
    :param url: provide url for request to be made for list of links
    :return: list
    """
    res = pytube.Playlist(url)
    res.populate_video_urls()
    return res.video_urls


def _process_single_video(url):
    try:
        # push init request for single url for youtube download link
        res = pytube.YouTube(url)
        # video quality
        videos = res.streams.filter(file_extension='mp4', progressive=True).order_by('resolution').asc().all()
        meta = []
        for video in videos:
            # calculate size
            mb_size = _process_video_size(video.filesize)
            # get the mime_type
            mime_type = video.mime_type
            list_video_data = {
                'url': f'{video.url}&title={parse.quote(res.title + "downloaded from @FlaskTube by JudeApana")}',
                'mime_type': mime_type,
                'resolution': video.resolution,
                'size': mb_size}
            meta.append(list_video_data)
        return {'meta': meta, 'title': res.title,
                'thumbnail_url': res.thumbnail_url,
                'length': math.ceil(int(res.length) / 60),
                'descp': res.description,
                'views': res.views,
                'rating': res.rating}
    except Exception as e:
        if "regex" in e.__str__():
            return {'error': "Youtube Url doesnt not match any known format"}
        elif "unavailable" in e.__str__():
            return {'error': "No Youtube video found. Please check URL"}
        else:
            return {'error': e.__str__()}


@api.route('/multiple', methods=["GET"])
def accept_multiple_video():
    """
    processes multiple video link
    :return: json
    """
    if request.method == 'GET':
        # get playlist key
        url_playlist = request.args.get('playlist')
        # get list key
        url_list = request.args.get('list')
        # check
        if request.args.get('start') is None:
            return jsonify(error='Start Key is missing')
        start_num_urls = int(request.args.get('start'))

        if request.args.get('stop') is None:
            return jsonify(error='Stop key is missing')

        end_num_urls = int(request.args.get('stop'))
        url = f'{url_playlist}&list={url_list}'
        print(url)
        if url is None:
            return jsonify(error="Youtube Link Not Found")
        if "&list" not in url and "?v" not in url:
            return jsonify(error="You have inserted a wrong playlist url")

        with ThreadPoolExecutor(max_workers=workers) as executor:
            """
            loops through and populates every url as fast as possible
            """
            futures = []
            # populate video links
            list_of_urls = _populate_playlist_urls(url)

            # liter every link from list_of_urls  => obtain data then next (CORE)
            for single_url in list_of_urls[start_num_urls:end_num_urls]:
                future = executor.submit(_process_single_video, single_url)
                # foreach a future is created
                futures.append(future)

        with ThreadPoolExecutor(max_workers=workers) as executor2:
            def get_all_url_datum():
                """
                loops through every youtube url generates meta data and releases a future
                :return: future
                """
                all_data = []
                _720p_320p_urls = []
                _320p_urls = []
                _320p_item = []
                _720_item = []
                # now append every future results to (all_data)
                for single_future in futures:
                    all_data.append(single_future.result())
                # getting to know how many items are in list
                for i in range(0, len(all_data)):
                    try:
                        _720_item = all_data[i]['meta'][1]['url']
                        _720p_320p_urls.append(_720_item)
                        _320p_item = all_data[i]['meta'][0]['url']
                    except KeyError as e:
                        # if exception hit append 320p_item to 720p_320p_url
                        _720p_320p_urls.append(_320p_item)

                all_data.append({'720p_320p_links': _720p_320p_urls, 'number of urls': len(list_of_urls)})
                return all_data

            future1 = executor2.submit(get_all_url_datum)
        return jsonify(future1.result())
    abort(status=403)

#
# @api.errorhandler(429)
# def report_429(error):
#     response = jsonify({'error': error.description['Sorry you cant load more than 15 links at a time']})
