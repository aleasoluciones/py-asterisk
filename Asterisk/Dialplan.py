'''
Asterisk/Dialplan.py: Asterisk dialplan manager, with support for
pbx_config_mgr.
'''

__author__ = 'David M. Wilson <dw@botanicus.net>'
__id__ = '$Id$'

import re
import Asterisk




class PbxConfigActions(object):
    '''
    Provide methods for Manager API actions exposed by the pbx_config_mgr
    module available from <http://botanicus.net/dw/>.
    '''

    def SetGlobalVar(self, variable, value):
        'Set global <variable> to <value>.'

        id = self._write_action('SetGlobalVar', {
            'Variable': variable,
            'Value': value
        })

        return self._translate_response(self.read_response(id))


    def GetGlobalVar(self, variable, default = Asterisk.Util.Unspecified):
        '''
        Return the value of the global <variable>, or <default> if <variable>
        is not set.
        '''

        id = self._write_action('GetGlobalVar', { 'Variable': variable })

        try:
            response = self._translate_response(self.read_response(id))

        except Asterisk.Manager.ActionFailed:
            if default is Asterisk.Util.Unspecified:
                raise

            return default

        return response[variable]


    def ContextCreate(self, context, registrar = None):
        '''
        Create a new context named <context>.
        '''

        id = self._write_action('ContextCreate', {
            'Context': context,
            'Registrar': registrar
        })

        return self._translate_response(self.read_response(id))


    def ContextDestroy(self, context, registrar = None):
        '''
        Destroy the named <context>.
        '''

        id = self._write_action('ContextDestroy', {
            'Context': context,
            'Registrar': registrar
        })

        return self._translate_response(self.read_response(id))




class Error(Asterisk.BaseException):
    'This exception is raised when there is a problem with a dialplan instance.'
    _prefix = 'dialplan error'





class Context(object):
    'Representation of an Asterisk dialplan context.'

    def __init__(self):
        self.extens = {}


    def add_extension(self, exten):
        if exten.pattern in self.extens:
            raise KeyError, 'extension with that pattern already exists.'


    def remove_extension(self, exten):
        del self.extens[exten.pattern]



class Dialplan(object):
    '''
    Representation of the Asterisk dialplan, including methods for
    manipulating, merging, synchronising, and deleting contexts.
    '''

    def __init__(self):
        self.contexts = {}


    def add_context(self, context):
        if context.name in self.contexts:
            raise KeyError, 'context with that name already exists.'

        self.contexts[context.name] = context



class Extension(object):
    'Representation of an Asterisk dialplan extension.'

    pattern_re = re.compile('^([0-9a-z]+|_[0-9a-zX])$')


    def pattern_legal(cls, pattern):
        'Return truth if <pattern> is a legal dialplan pattern.'
        return cls.pattern_re.match(pattern) is not None

    pattern_legal = classmethod(pattern_legal)


    def __init__(self, pattern, actions = None):
        pattern = str(pattern)

        if not self.pattern_legal(pattern):
            raise Error('pattern %r is not legal.' % pattern)

        self.pattern = pattern
        self.priorities = []


    def add_action(self, action, priority = None):
        self.priorities.append((priority, action))







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
            VoicemailMain('${CALLERID}',
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
