#
# ################################################################### #
#                                                                     #
#  B3todiscord Plugin for BigBrotherBot(B3) (www.bigbrotherbot.com)   #
#  Copyright (c) 2019 Zwambro                                         #
#                                                                     #
#  This program is free software; you can redistribute it and/or      #
#  modify it under the terms of the GNU General Public License        #
#  as published by the Free Software Foundation; either version 2     #
#  of the License, or (at your option) any later version.             #
#                                                                     #
#  This program is distributed in the hope that it will be useful,    #
#  but WITHOUT ANY WARRANTY; without even the implied warranty of     #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the       #
#  GNU General Public License for more details.                       #
#                                                                     #
#  You should have received a copy of the GNU General Public License  #
#  along with this program; if not, write to the Free Software        #
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA      #
#  02110-1301, USA.                                                   #
#                                                                     #
# ################################################################### #
#
#  based on Watchmiltan discord plugin and all the credit to him
#  CHANGELOG:
#  03.11.2019 - v1.0 - Zwambro
#  - first release.
#
#  30.03.2021 - v1.1 - Zwambro
#  - cleaning the code.
#
#  17-04-2021 - v1.2 - Zwambro
#  - add t4 support
#  - integrate echelon website with b3todiscord plugin

__version__ = "1.2"
__author__ = 'Zwambro'


import b3
import b3.plugin
import b3.events
from b3 import functions
import requests
import json
import datetime
import time
import re
from collections import defaultdict
from b3.functions import minutesStr


class DiscordEmbed:  # discord embed formatting
    def __init__(self, url, **kwargs):
        self.url = url
        self.color = kwargs.get('color')
        self.gamename = kwargs.get('author')
        self.gamename_icon = kwargs.get('author_icon')
        self.thumbnail = kwargs.get('thumbnail')
        self.title = kwargs.get('title')
        self.desc = kwargs.get('desc')
        self.fields = kwargs.get('fields', [])
        self.footnote = kwargs.get('footer')

    def set_gamename(self, **kwargs):
        self.gamename = kwargs.get('name')
        self.gamename_icon = kwargs.get('icon')

    def set_title(self, title):
        self.title = title

    def set_desc(self, desc):
        self.desc = desc

    def set_thumbnail(self, url):
        self.thumbnail = url

    def textbox(self, **kwargs):
        name = kwargs.get('name')
        value = kwargs.get('value')
        inline = kwargs.get('inline')
        field = {'name': name, 'value': value, 'inline': inline}
        self.fields.append(field)

    def set_footnote(self, **kwargs):
        self.footnote = kwargs.get('text')
        self.ts = str(datetime.datetime.utcfromtimestamp(time.time()))

    @property
    def push(self, *arg):  # making ready to push
        data = {}
        data["embeds"] = []
        embed = defaultdict(dict)

        if self.gamename:
            embed["author"]["name"] = self.gamename
        if self.gamename_icon:
            embed["author"]["icon_url"] = self.gamename_icon
        if self.color:
            embed["color"] = self.color
        if self.title:
            embed["title"] = self.title
        if self.thumbnail:
            embed["thumbnail"]['url'] = self.thumbnail
        if self.desc:
            embed["description"] = self.desc
        if self.footnote:
            embed["footer"]['text'] = self.footnote
        if self.ts:
            embed["timestamp"] = self.ts

        if self.fields:
            embed["fields"] = []
            for field in self.fields:
                f = {}
                f["name"] = field['name']
                f["value"] = field['value']
                f["inline"] = field['inline']  # appear next to each other
                embed["fields"].append(f)

        data["embeds"].append(dict(embed))
        empty = all(not d for d in data["embeds"])
        if empty:
            data['embeds'] = []
        return json.dumps(data)

    def post(self):
        headers = {'Content-Type': 'application/json'}
        result = requests.post(self.url, data=self.push, headers=headers)


class B3TodiscordPlugin(b3.plugin.Plugin):
    _adminPlugin = None
    url = ""
    echelon = False
    gameId = ""
    echelonLink = ""

    def onLoadConfig(self):
        try:
            self.url= self.getSetting('settings', 'webhook', b3.STR, self.url)
            self.echelon= self.getSetting('settings', 'echelon', b3.BOOL, self.echelon)
            self.gameId= self.getSetting('settings', 'game_id', b3.INT, self.gameId)
            self.echelonLink= self.getSetting('settings', 'echelon_url', b3.STR, self.echelonLink)
        except Exception, err:
            self.error(err)

    def onStartup(self):
        # loading Admin plugin
        self._adminPlugin = self.console.getPlugin('admin')

        if not self._adminPlugin:
            self.error('Could not find admin plugin')
            return

        # Getting fucking events from fucking B3 events
        self.registerEvent(b3.events.EVT_CLIENT_BAN, self.onBan)
        self.registerEvent(b3.events.EVT_CLIENT_BAN_TEMP, self.onBan)
        self.registerEvent(b3.events.EVT_CLIENT_KICK, self.onKick)
        self.registerEvent(b3.events.EVT_CLIENT_UNBAN, self.onUnban)
        # to check if events started up
        self.debug('plugin started')

    def stripColors(self, s):
        return re.sub('\^[0-9]{1}', '', s)

    def onBan(self, event):
        admin = event.data['admin']
        dict = self.console.game.__dict__
        server = self.stripColors(str(dict['sv_hostname']))
        game = dict['gameName']
        reason = event.data['reason']
        client = event.client
        ip = str(client.ip)
        cid = str(client.id)
        hwid = str(client.guid)

        if admin == None:
            admin_name = "B3"
        else:
            admin_name = admin.name

        embed = DiscordEmbed(self.url, color=15466496)

        if "cod8" in game:
            embed.set_gamename(name='TeknoMW3', icon='https://orig00.deviantart.net/9af1/f/2011/310/2/1/modern_warfare_3_logo_by_wifsimster-d4f9ozd.png')
        if "iw5" in game:
            embed.set_gamename(name='PlutoIW5', icon='https://orig00.deviantart.net/9af1/f/2011/310/2/1/modern_warfare_3_logo_by_wifsimster-d4f9ozd.png')
        if "t6" in game:
            embed.set_gamename(name='PlutoT6', icon='https://i.pinimg.com/originals/5a/44/5c/5a445c5c733c698b32732550ec797e91.jpg')
        if "cod4" in game:
            embed.set_gamename(name='Cod4x', icon='http://orig05.deviantart.net/8749/f/2008/055/0/c/call_of_duty_4__dock_icon_by_watts240.png')
        if "cod6" in game:
            embed.set_gamename(name='Iw4x', icon='https://i.gyazo.com/758b6933287392106bfdddc24b09d502.png')
        if "t4" in game:
            embed.set_gamename(name='PlutoT4', icon='https://aux3.iconspalace.com/uploads/571650719715891032.png')

        if self.echelon:
            if not self.echelonLink.startswith("http"):
                self.debug("Echelon url must be something like 'http(s)://echelon.com'")
                return
            if self.echelonLink.endswith("/"):
                self.echelonLink = self.echelonLink[:-1]
            echeLon = "%s/clientdetails.php?id=%s&game=%s" % (self.echelonLink, cid, self.gameId)
            embed.set_desc('`%s` Banned [`%s` (@%s)](%s)' %(self.stripColors(admin_name), client.name, cid, echeLon))
        else:
            embed.set_desc('`%s` Banned `%s` (@%s)' %(self.stripColors(admin_name), client.name, cid))

        embed.textbox(name='Reason', value=self.stripColors(reason.replace(',', '')), inline=False)
        embed.textbox(name='Server', value=server, inline=True)

        if 'duration' in event.data:
            duration = minutesStr(event.data['duration'])
            embed.textbox(name='Duration', value=duration, inline=True)
        if not 'duration' in event.data:
            embed.textbox(name='Duration', value='Permanent', inline=True)

        embed.textbox(name='PlayerIP', value=ip, inline=True)
        embed.set_footnote(text="Guid: " + hwid)
        embed.post()

    def onKick(self, event):

        admin = event.data['admin']
        dict = self.console.game.__dict__
        server = self.stripColors(str(dict['sv_hostname']))
        game = dict['gameName']
        reason = event.data['reason']
        client = event.client
        ip = str(client.ip)
        cid = str(client.id)
        hwid = str(client.guid)

        if admin == None:
            admin_name = "B3"
        else:
            admin_name = admin.name

        embed = DiscordEmbed(self.url, color=15466496)

        if "cod8" in game:
            embed.set_gamename(name='TeknoMW3', icon='https://orig00.deviantart.net/9af1/f/2011/310/2/1/modern_warfare_3_logo_by_wifsimster-d4f9ozd.png')
        if "cod8_pluto" in game:
            embed.set_gamename(name='PlutoIW5', icon='https://orig00.deviantart.net/9af1/f/2011/310/2/1/modern_warfare_3_logo_by_wifsimster-d4f9ozd.png')
        if "t6" in game:
            embed.set_gamename(name='PlutoT6', icon='https://i.pinimg.com/originals/5a/44/5c/5a445c5c733c698b32732550ec797e91.jpg')
        if "cod4" in game:
            embed.set_gamename(name='Cod4x', icon='http://orig05.deviantart.net/8749/f/2008/055/0/c/call_of_duty_4__dock_icon_by_watts240.png')
        if "cod6" in game:
            embed.set_gamename(name='Iw4x', icon='https://i.gyazo.com/758b6933287392106bfdddc24b09d502.png')
        if "t4" in game:
            embed.set_gamename(name='PlutoT4', icon='https://aux3.iconspalace.com/uploads/571650719715891032.png')

        if self.echelon:
            if not self.echelonLink.startswith("http"):
                self.debug("Echelon url must be something like 'http(s)://echelon.com'")
                return
            if self.echelonLink.endswith("/"):
                self.echelonLink = self.echelonLink[:-1]
            echeLon = "%s/clientdetails.php?id=%s&game=%s" % (self.echelonLink, cid, self.gameId)
            embed.set_desc('`%s` Kicked [`%s` (@%s)](%s)' %(self.stripColors(admin_name), client.name, cid, echeLon))

        else:
            embed.set_desc('`%s` Kicked `%s` (@%s)' %(self.stripColors(admin_name), client.name, cid))

        embed.textbox(name='Reason', value=self.stripColors(reason.replace(',', '')), inline=False)
        embed.textbox(name='Server', value=server, inline=True)
        embed.textbox(name='PlayerIP', value=ip, inline=True)
        embed.set_footnote(text="Guid: " + hwid)
        embed.post()

    def onUnban(self, event):

        admin = event.data['admin']
        client = event.client

        if admin == None:
            admin_name = "B3"
        else:
            admin_name = admin.name

        embed = DiscordEmbed(self.url, color=0xCCCCCC)
        embed.set_thumbnail('https://www.iconsdb.com/icons/download/green/checkmark-16.png')
        embed.set_desc('`%s` has been unbanned by `%s`' % (client.name, self.stripColors(admin_name)))
        embed.set_footnote()
        embed.post()
