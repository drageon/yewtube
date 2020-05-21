###
# Copyright (c) 2015, Daniel Rageon
# Originally Copyrighted (c) 2009, James Scott
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###
import datetime
import re
import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser
from urlparse import *

class Youtube(callbacks.Plugin):
    """Add the help for "@plugin help Youtube" here
    This should describe *how* to use this plugin."""
    threaded = True
    def __init__(self, irc):
        self.__parent = super(Youtube, self)
        self.__parent.__init__(irc)
        self.service = build('youtube', 'v3', developerKey=self.registryValue('developer_key'), cache_discovery=False)

    def _video_id(self, url):
        """
        Examples:
        - http://youtu.be/SA2iWivDJiE
        - http://www.youtube.com/watch?v=_oPAwA_Udwc&feature=feedu
        - http://www.youtube.com/embed/SA2iWivDJiE
        - http://www.youtube.com/v/SA2iWivDJiE?version=3&amp;hl=en_US
        """
        self._logInfo('%s %s' % (url.path, url.netloc))
        if ('/v/' in url.path):
          vidid = url.path.strip('/v/')
        elif ('/embed/' in url.path):
          vidid = url.path.strip('/embed/').strip('?')
        else:
          vidid = url.path.replace('/', '')

        if ('watch' in vidid and url.netloc != 'youtu.be'):
          self._logInfo('watch blah')
          vidid = url.query.split('v=')[1].split('&')[0]

        self._logInfo('video id: %s' % (vidid))

        return vidid

    def _logInfo(self, msg):
      self.log.info('youtube: %s', msg)

    def _lookUpYouTube(self, irc, msg):
        self._logInfo("{0}".format(msg))
        (recipients, text) = msg.args
        yt_service = self.service
        url = urlparse(text.strip())
        url_time = None
        for i in url.query.split('&'):
          if 't=' in i:
            self._logInfo('time marker: %s' % (i))
            url_time = i
        for i in url.query.split('?'):
          if 't=' in i:
            self._logInfo('time marker: %s' % (i))
            url_time = i
        vid_id = self._video_id(url).split(' ')[0]
        length = ""
        title = ""
        rating = ""
        chantitle = ""
        uploaded_date = ""
        views = 0
        likes = ""
        dislikes = ""
        #self._logInfo('query: yt_service.videos().list(id=%s,part=snippet,statistics,contentDetails' % (vid_id))
        yt_query = yt_service.videos().list(id=vid_id,part='snippet,statistics,contentDetails')
        yt_result = yt_query.execute()
        #self._logInfo('query: %s' % (yt_result))
        try:
          yt_snippet = yt_result['items'][0]['snippet']
          yt_stats = yt_result['items'][0]['statistics']
          yt_cdetails = yt_result['items'][0]['contentDetails']
        except:
          self._logInfo('error loading url info for: %s' % (url.geturl()))
          return 1

        try:
            title = yt_snippet['title']
            title = ircutils.bold(title)
        except:
            pass
        try:
            views = int(yt_stats['viewCount'])
            views = "{:,}".format(views)
            views = ircutils.bold(views)
        except:
            views = ircutils.bold("UNKNOWN")
            pass
        try:
            chantitle = yt_snippet['channelTitle']
            chantitle = ircutils.bold(chantitle)
        except:
            chantitle = ircutils.bold("UNKNOWN")
        try:
            length = yt_cdetails['duration'].split('PT')[1].lower()
            length = ircutils.bold(length)
        except:
            length = ircutils.bold("n/a")
        try:
           uploaded_date = yt_snippet['publishedAt']
           uploaded_date = datetime.datetime.strptime(uploaded_date, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%m/%d/%Y")
           uploaded_date = ircutils.bold(uploaded_date)
        except:
           uploaded_date = ircutils.bold("n/a")
        try:
           likes = yt_stats['likeCount']
           likes = ircutils.bold(likes)
        except:
           likes = ircutils.bold("n/a")
        try:
           dislikes = yt_stats['dislikeCount']
           dislikes = ircutils.bold(dislikes)
        except:
           dislikes = ircutils.bold("n/a")
        irc.reply('1,0You0,5Tube %s [len:%s|ch:%s|views:%s|date:%s]'  % (title, length, chantitle, views, uploaded_date),prefixNick=False)

    def doPrivmsg(self, irc, msg):
        (recipients, text) = msg.args
        if ("youtube.com" in text) or ("youtu.be" in text):
            self._lookUpYouTube(irc, msg)
        else:
            pass
    
Class = Youtube


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
