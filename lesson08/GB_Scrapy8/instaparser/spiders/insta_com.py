""" Методы сбора и обработки данных из сети Интернет
Урок 8. "Фреймворк Scrapy. Реализация механизмов клиент-серверного взаимодействия."

1) Написать приложение, которое будет проходиться по указанному списку двух и/или
более пользователей и собирать данные об их подписчиках и подписках.
2) По каждому пользователю, который является подписчиком или на которого подписан
исследуемый объект нужно извлечь имя, id, фото (остальные данные по желанию).
Фото можно дополнительно скачать.
3) Собранные данные необходимо сложить в базу данных. Структуру данных нужно заранее
продумать, чтобы:
- Написать запрос к базе, который вернёт список подписчиков только указанного пользователя.
- Написать запрос к базе, который вернёт список профилей, на кого подписан указанный пользователь.

Для выполнения данной работы необходимо делать запросы в API instagram с указанием
заголовка User-Agent : 'Instagram 155.0.0.37.107'"""

import scrapy
import re
import json
from scrapy.http import HtmlResponse
from urllib.parse import urlencode
from copy import deepcopy
from instaparser.items import InstaparserItem


class InstacomSpider(scrapy.Spider):
    name = 'insta_com'
    allowed_domains = ['instagram.com']
    start_urls = ['http://instagram.com/']
    inst_login_link = 'https://www.instagram.com/accounts/login/ajax/'

    """Необходимо ввести логин, пароль и страницу для парсинга"""

    inst_login = ''
    inst_pwd = ''
    users_parse = ['']

    mobile_user_agent = {'User-Agent': 'Instagram 155.0.0.37.107'}

    def parse(self, response: HtmlResponse, **kwargs):
        csrf = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(
            self.inst_login_link,
            method='POST',
            callback=self.login,
            formdata={'username': self.inst_login,
                      'enc_password': self.inst_pwd},
            headers={'x-csrftoken': csrf})

    def login(self, response: HtmlResponse):
        j_data = response.json()
        if j_data.get('authenticated'):
            for user in self.users_parse:
                yield response.follow(
                    f'/{user}/',
                    callback=self.user_parsing,
                    cb_kwargs={'username': user})

    def user_parsing(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)
        variables = {'count': 12}
        link_parse = [
            f'https://i.instagram.com/api/v1/friendships/{user_id}/followers/?{urlencode(variables)}'
            f'&search_surface=follow_list_page',
            f'https://i.instagram.com/api/v1/friendships/{user_id}/following/?{urlencode(variables)}']

        cb_kwargs_dict = {'username': username, 'user_id': user_id, 'variables': deepcopy(variables)}
        for link in link_parse:
            if 'followers' in link:
                yield response.follow(
                    link,
                    callback=self.followers_parse,
                    cb_kwargs=cb_kwargs_dict,
                    headers=self.mobile_user_agent)
            elif 'following' in link:
                yield response.follow(
                    link,
                    callback=self.following_parse,
                    cb_kwargs=cb_kwargs_dict,
                    headers=self.mobile_user_agent)

    def followers_parse(self, response: HtmlResponse, username, user_id, variables):
        j_data = response.json()
        if j_data.get('big_list'):
            variables['max_id'] = j_data.get('next_max_id')
            url_followers = f'https://i.instagram.com/api/v1/friendships/{user_id}/followers/?{urlencode(variables)}' \
                            f'&search_surface=follow_list_page'

            yield response.follow(
                url_followers,
                callback=self.followers_parse,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'variables': deepcopy(variables)},
                headers=self.mobile_user_agent)

        users = j_data.get('users')
        for user in users:
            item = InstaparserItem(
                user_parser_name=username,
                user_id=user.get('pk'),
                username=user.get('username'),
                photo=user.get('profile_pic_url'),
                user_type='follower')
            yield item

    def following_parse(self, response: HtmlResponse, username, user_id, variables):
        j_data = response.json()
        if j_data.get('big_list'):
            variables['max_id'] = j_data.get('next_max_id')
            url_followers = f'https://i.instagram.com/api/v1/friendships/{user_id}/following/?{urlencode(variables)}'

            yield response.follow(
                url_followers,
                callback=self.following_parse,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'variables': deepcopy(variables)},
                headers=self.mobile_user_agent)

        users = j_data.get('users')
        for user in users:
            item = InstaparserItem(
                user_parser_name=username,
                user_id=user.get('pk'),
                username=user.get('username'),
                photo=user.get('profile_pic_url'),
                user_type='following')
            yield item

    def fetch_csrf_token(self, text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    def fetch_user_id(self, text, username):
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text).group()
        return json.loads(matched).get('id')
