'''
Asterisk/Dialplan.py: Asterisk dialplan manager.
'''

import Asterisk




class Error(Asterisk.BaseException):
    'This exception is raised when there is a problem with a dialplan instance.'
    _prefix = 'dialplan error'





class Context(object):
    'Representation of an Asterisk dialplan context.'

    def __init__(self):
        self.extensions = []



class Dialplan(object):
    '''
    Representation of the Asterisk dialplan, including methods for
    manipulating, merging, synchronising, and deleting contexts.
    '''

    def __init__(self):
        self.contexts = {}



class Extension(object):
    'Representation of an Asterisk dialplan extension.'

    def __init__(self):
        self.priorities = []

    def add_priority(self):
        pass







class Foo:
    pass





'''
D = Dialplan([
    Context(name = 'local_extensions', extensions = [
        Extension(100, actions = [
            Dial('Zap/G1', on_fail = [
                Congestion(),
                Hangup() ]
            )
        ],

        Extension(101, actions = [
            Dial('VoicemailMain', '${CALLERID}@${CONTEXT}',
                skip = True,
                on_fail = [
                    Playback('voicemail-unavail'),
                    Hangup()
                ]
            ),
            Hangup()
        ])
            

    ])

])
'''
