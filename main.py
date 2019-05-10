import json
import logging
import pprint

import os

import time
from jinja2 import Template

import settings
from database_repository.db_repository import DBRepository
from deputes_club import deputes_club
from gosduma_api.api import GosDumaApi, Limit
from gosduma_screen import GosDumaScreen
from graphs import Graph
from settings import TJ_API_KEY, GD_TOKEN_APP, GD_TOKEN
from tjornal_api.api import TjApi


logging.basicConfig(filename="sample.log", level=logging.INFO)


class Vote(object):
    def __init__(self, vote_info):
        self.vote_info = vote_info

        self.subject = vote_info['subject']
        self.law_number = vote_info['lawNumber']
        self.resolution = vote_info['resolution']
        self.for_vote = vote_info['for']
        self.against = vote_info['against']
        self.abstain = vote_info['abstain']
        self.absent = vote_info['absent']
        self.vote_date = vote_info['date']

        self.results_by_faction = vote_info['resultsByFaction']
        self.results_by_deputy = vote_info['resultsByDeputy']

        self.factions = None

    def get_fractions_with_deputies(self):
        self.factions = self._factions_parse()
        deputies = self._deputies_parse()

        for faction in self.factions:
            faction.deputies = list(filter(lambda x: x.faction_code == faction.code, deputies))

        return self.factions

    def get_total_quantity_deputies(self):
        if self.factions is None:
            raise Exception('Call get_fractions_with_deputies first.')

        total = 0
        for faction in self.factions:
            total += int(faction.total)

        return total

    def _factions_parse(self):
        factions = []
        for result_by_faction in self.results_by_faction:
            factions.append(Faction(result_by_faction))
        return factions

    def _deputies_parse(self):
        deputies = []
        for result_by_deputy in self.results_by_deputy:
            deputies.append(Deputy(result_by_deputy))
        return deputies


class Faction(object):
    def __init__(self, result_by_faction_dict):
        self.code = result_by_faction_dict.get('code', None)
        self.total = result_by_faction_dict.get('total', None)
        self.abbr = result_by_faction_dict.get('abbr', None)
        self.name = result_by_faction_dict.get('name', None)

        self.for_vote_faction = result_by_faction_dict.get('for', None)
        self.against_faction = result_by_faction_dict.get('against', None)
        self.abstain_faction = result_by_faction_dict.get('abstain', None)
        self.absent_faction = result_by_faction_dict.get('absent', None)

        self.deputies = []


class Deputy(object):
    def __init__(self, result_by_deputy_dict):
        self.code = result_by_deputy_dict.get('code', None)
        self.result = result_by_deputy_dict.get('result', None)
        self.faction_code = result_by_deputy_dict.get('factionCode', None)
        self.family = result_by_deputy_dict.get('family', None)
        self.name = result_by_deputy_dict.get('name', None)
        self.patronymic = result_by_deputy_dict.get('patronymic', None)

        self.url = None
        self.kpd = None

        deputes_club_filter_list = list(filter(lambda x: x[0] in self.get_fio(), deputes_club))

        if deputes_club_filter_list:
            try:
                self.url = deputes_club_filter_list[0][1]
            except:
                self.url = ''

            try:
                self.kpd = deputes_club_filter_list[0][2]
            except:
                self.kpd = ''

    def get_fio(self):

        return '{0} {1} {2}'.format(self.family, self.name, self.get_patronomic())

    def get_info(self):
        if self.url and self.kpd:
            return '<a href="{0}">{1}</a> (КПД: {2}%)'.format(self.url, self.get_fio(), self.kpd)
        return '{0}'.format(self.get_fio())

    def get_patronomic(self):
        patronymic = self.patronymic
        if patronymic is None:
            patronymic = ''
        return patronymic

    def get_result(self):
        if self.result == 'for':
            return 'за'
        elif self.result == 'against':
            return 'против'
        elif self.result == 'abstain':
            return 'воздержался'
        elif self.result == 'absent':
            return 'не голосовал'

    def get_smile(self):
        if self.result == 'for':
            return '📗'
        elif self.result == 'against':
            return '📕'
        elif self.result == 'abstain':
            return '📒'
        elif self.result == 'absent':
            return '📘'


def start_move_articles():
    tj_api = TJ_API_KEY
    gd = GosDumaApi(GD_TOKEN, GD_TOKEN_APP)
    tj_api = TjApi(tj_api)
    # deputes_club_list = DeputatClubParser().get_deputates()
    current_path = os.path.dirname(os.path.abspath(__file__))

    db = DBRepository()
    db.connect()

    result = gd.get_vote_search(limit=Limit.QUANTITY_100)
    votes = result.get('votes', None)

    if votes is not None:
        for vote in votes:
            result = vote['result']
            vote_id = vote['id']

            vote_info = gd.vote(vote_id)
            vote_obj = Vote(vote_info)
            factions = vote_obj.get_fractions_with_deputies()
            total_quantity_deputies = vote_obj.get_total_quantity_deputies()

            vote_in_db = db.get_vote(vote_id=vote_id, vote_date=vote_obj.vote_date)

            if vote_in_db is not None:
                continue

            gd_screen = GosDumaScreen(vote_obj.vote_date,
                                      vote_obj.for_vote,
                                      vote_obj.against,
                                      vote_obj.abstain,
                                      result)

            image_screen_name = 'gd_screen'
            screen_file_name = gd_screen.save_png(image_screen_name)

            labels = [
                'За',
                'Против',
                'Воздержались',
                'Не голосовали',
            ]
            fig_names = []
            for i, faction in enumerate(factions):
                sizes = [
                    int(faction.for_vote_faction),
                    int(faction.against_faction),
                    int(faction.abstain_faction),
                    int(faction.absent_faction)
                ]
                buf_labels = []
                buf_sizes = []
                for idx, size in enumerate(sizes):
                    if size != 0:
                        buf_sizes.append(size)
                        buf_labels.append(labels[idx])

                if buf_labels:
                    fig_name = 'fig_{0}.png'.format(i)
                    fig_names.append(fig_name)
                    pie_image_name = Graph().pie('Количество участников голосования ({0})'.format(faction.abbr), buf_labels, buf_sizes, name=fig_name)

            with open('article.template', 'rb') as f:
                content_template = f.read().decode("utf-8")

            template = Template(content_template)

            render_template = template.render(factions=factions)

            time.sleep(1)
            upload_result = tj_api.uploader_upload(os.path.join(current_path, screen_file_name))
            blocks = [tj_api.get_image_block("Количественное голосование ГД", "", upload_result['result'][0], cover=True)]
            for file_name in fig_names:
                time.sleep(1)
                upload_result = tj_api.uploader_upload(os.path.join(current_path, file_name))
                blocks.append(tj_api.get_image_block("", "", upload_result['result'][0]))

            time.sleep(1)
            entry = {
                'blocks': [
                    {
                        "type": "text",
                        "data": {
                            "text": "<p>{0}</p>".format(vote_obj.subject),
                            "text_truncated": ""
                        },
                        "cover": True,
                        "anchor": ""
                    },
                ] + blocks + [
                    {
                        "type": "text",
                        "data": {
                            "text": render_template,
                            "text_truncated": ""
                        },
                        "cover": False,
                        "anchor": ""
                    },
                ]
            }
            file_json = json.dumps(entry)
            result = tj_api.create_entry('Результат голосования депутатов Госдумы {0}'.format(vote_obj.vote_date), render_template, settings.SUBSITE_ID, entry=file_json)
            if 'error' in result:
                print(result)
                logging.error(result['message'])
                break
            else:
                print('Success add.')
                db.create_vote_history(vote_id=vote_id, vote_date=vote_obj.vote_date)
            time.sleep(120)


if __name__ == '__main__':
    try:
        start_move_articles()
        logging.info("Success")
    except Exception as ex:
        print(str(ex))
        logging.error(str(ex))
