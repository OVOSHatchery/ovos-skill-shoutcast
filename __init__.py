from os.path import join, dirname

import requests
from ovos_utils.parse import fuzzy_match, MatchStrategy
from ovos_workshop.skills.common_play import OVOSCommonPlaybackSkill, \
    MediaType, PlaybackType, ocp_search, ocp_featured_media
from shoutcast_api import get_stations_keywords, get_top_500


class ShoutCastSkill(OVOSCommonPlaybackSkill):
    def __init__(self):
        super().__init__("ShoutCast")
        self.supported_media = [MediaType.GENERIC,
                                MediaType.MUSIC,
                                MediaType.RADIO]
        self.skill_icon = join(dirname(__file__), "ui", "logo.png")
        if "api_key" not in self.settings:
            # pretend you didn't see this totally legit key and get your own
            # instead!
            self.settings["api_key"] = "sh1t7hyn3Kh0jhlV"

    def search_shoutcast(self, query, limit=100):
        response = get_stations_keywords(self.settings["api_key"],
                                         search=query,
                                         limit=limit, br=128)
        for s in response.station:
            data = s.__dict__
            data["uri"] = f'http://yp.shoutcast.com/sbin/tunein-station.m3u?id={s.id}'
            yield data

    def get_featured_stations(self):
        response = get_top_500(self.settings["api_key"])
        for s in response.station:
            data = s.__dict__
            data["uri"] = f'http://yp.shoutcast.com/sbin/tunein-station.m3u?id={s.id}'
            yield data

    def calc_score(self, phrase, match, idx=0, base_score=0):
        # idx represents the order from search
        score = base_score - idx  # - 1% as we go down the results list
        score += 100 * fuzzy_match(phrase.lower(), match['name'].lower(),
                                   strategy=MatchStrategy.TOKEN_SET_RATIO)
        return min(100, score)

    def validate_uri(self, uri):
        # verify if the stream is available, this is absolutely
        # necessary because A LOT of them are dead
        try:
            r = requests.get(uri, verify=False, timeout=0.5)
            if r.status_code == 200:
                # get the real stream from the playlist,
                # mycroft-gui cant handle playlists
                if ".pls" in uri or ".m3u" in uri:
                    for l in r.text.split("\n"):
                        if l.startswith("http"):
                            return l
                else:
                    return uri
        except:
            pass

    @ocp_featured_media()
    def featured_media(self):
        return [{
            "media_type": MediaType.RADIO,
            "uri": ch["uri"],
            "playback": PlaybackType.AUDIO,
            "image": ch.get("logo_url") or self.skill_icon,
            "bg_image": ch.get("logo_url") or self.skill_icon,
            "skill_icon": self.skill_icon,
            "title": ch["name"],
            "author": "Shoutcast",
            "length": 0
        } for ch in self.get_featured_stations() if ch.get("uri")]

    @ocp_search()
    def ocp_shoutcast_playlist(self, phrase):
        phrase = self.remove_voc(phrase, "radio")
        if self.voc_match(phrase, "shoutcast", exact=True):
            yield {
                "match_confidence": 100,
                "media_type": MediaType.RADIO,
                "playlist": self.featured_media(),
                "playback": PlaybackType.AUDIO,
                "skill_icon": self.skill_icon,
                "image": self.skill_icon,
                "bg_image": self.skill_icon,
                "title": "Shoutcast (Top 500)",
                "author": "Shoutcast"
            }

    @ocp_search()
    def search_radios(self, phrase, media_type):
        base_score = 0

        if media_type == MediaType.RADIO or self.voc_match(phrase, "radio"):
            base_score += 30

        if self.voc_match(phrase, "shoutcast"):
            base_score += 50  # explicit request
            phrase = self.remove_voc(phrase, "shoutcast")

        phrase = self.remove_voc(phrase, "radio")

        for ch in self.search_shoutcast(phrase):
            uri = self.validate_uri(ch['uri'])
            if not uri:
                continue
            score = base_score + self.calc_score(phrase, ch)
            yield {
                "match_confidence": min(100, score),
                "media_type": MediaType.RADIO,
                "uri": uri,
                "playback": PlaybackType.AUDIO,
                "image": ch.get('logo_url') or self.skill_icon,
                "bg_image": ch.get('logo_url') or self.skill_icon,
                "skill_icon": self.skill_icon,
                "title": ch["name"],
                "length": 0
            }


def create_skill():
    return ShoutCastSkill()
