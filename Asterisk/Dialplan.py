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
        'Create a new context named <context>.'

        id = self._write_action('ContextCreate', {
            'Context': context,
            'Registrar': registrar
        })

        return self._translate_response(self.read_response(id))


    def ContextDestroy(self, context, registrar = None):
        'Destroy the named <context>.'

        id = self._write_action('ContextDestroy', {
            'Context': context,
            'Registrar': registrar
        })

        return self._translate_response(self.read_response(id))


    def ContextDump(self, context):
        'Return a complex nested mapping representing <context>.'

        id = self._write_action('ContextDump', { 'Context': context })
        self._translate_response(self.read_response(id))
        context = {}


        def ExtensionInfo(self, event):
            if event.Actionid == id:
                context[event.Exten] = {}

        def ExtensionPriorityInfo(self, event):
            if event.Actionid != id:
                return

            e = self.strip_evinfo(event)
            e.pop('Registrar')
            e.pop('Context')

            context[e.pop('Exten')][e.pop('Priority')] = e

        def ContextDumpComplete(self, event):
            if event.Actionid == id:
                stop_flag[0] = True


        events = Util.EventCollection([
            ExtensionInfo, ExtensionPriorityInfo, ContextDumpComplete
        ])

        self.events += events

        try:
            stop_flag = [ False ]

            while stop_flag[0] == False:
                packet = self._read_packet()
                self._dispatch_packet(packet)

        finally:
            self.events -= events

        return context


    def ContextExtensionDump(self, context, extension):
        '''
        Return a list of (<priority>, <application>, <data>) 3-tuples for the
        given <extension> in <context>.
        '''

        id = self._write_action('ContextExtensionDump', {
            'Context': context,
            'Exten': extension
        })

        self._translate_response(self.read_response(id))
        priorities = []


        def ExtensionPriorityInfo(self, event):
            if event.Actionid == id:
                priorities.append(
                    (int(event.Priority), event.Application, event.AppData)
                ) 

        def ExtensionInfoComplete(self, event):
            if event.Actionid == id:
                stop_flag[0] = True


        events = Util.EventCollection([
            ExtensionPriorityInfo, ExtensionInfoComplete
        ])

        self.events += events

        try:
            stop_flag = [ False ]

            while stop_flag[0] == False:
                packet = self._read_packet()
                self._dispatch_packet(packet)

        finally:
            self.events -= events

        return context


    def ContextAddSwitch(self, context, switch, data = None):
        'Add <switch> to <context>, optionally with <data>.'

        id = self._write_action('ContextAddSwitch', {
            'Context': context,
            'Switch': switch,
            'Data': data
        })

        return self._translate_response(self.read_response(id))


    def ContextRemoveSwitch(self, context, switch, data = None):
        'Remove <switch> from <context>, optionally with <data>.'

        id = self._write_action('ContextRemoveSwitch', {
            'Context': context,
            'Switch': switch,
            'Data': data
        })

        return self._translate_response(self.read_response(id))


    def ContextAddExtension(self, context, extension, priority, application,
    args = [], caller_id = None, replace = False):
        '''
        Add a new <priority> to a non-existent or already-existing <extension>
        in <context>. Cause <priority> to call <application>, optionally with
        the argument list in <args>.
        
        Optionally only match if the incoming CallerID is equal to <caller_id>.
        Optionally <replace> any existing priority.
        '''

        id = self._write_action('ContextAddExtension', {
            'Context': context,
            'Exten': extension,
            'Priority': int(priority),
            'Application': application,
            'AppData': '|'.join(map(str, args)),
            'CallerID': caller_id,
            'Replace': replace and 'yes' or None
        })

        return self._translate_response(self.read_response(id))


    def ContextRemoveExtension(self, context, extension, priority = None):
        'Remove <extension> from <context>, optionally with <priority>.'

        id = self._write_action('ContextRemoveExtension', {
            'Context': context,
            'Exten': extension,
            'Priority': priority
        })

        return self._translate_response(self.read_response(id))


    def ContextAddInclude(self, context, include):
        'Include the context named in <include> to <context>.'

        id = self._write_action('ContextAddInclude', {
            'Context': context,
            'Include': include
        )}

        return self._translate_response(self.read_response(id))


    def ContextRemoveInclude(self, context, include):
        'Remove the included context named <include> from <context>.'

        id = self._write_action('ContextRemoveInclude', {
            'Context': context,
            'Include': include
        })

        return self._translate_response(self.read_response(id))


    def ContextAddIgnorePat(self, context, pattern):
        'Add ignorepat <pattern> to <context>.'

        id = self._write_action('ContextAddIgnorePat', {
            'Context': context,
            'Pattern': pattern
        })

        return self._translate_response(self.read_response(id))


    def ContextRemoveIgnorePat(self, context, pattern):
        'Remove ignorepat <pattern> from <context>.'

        id = self._write_action('ContextRemoveIgnorePat', {
            'Context': context,
            'Pattern': pattern
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
