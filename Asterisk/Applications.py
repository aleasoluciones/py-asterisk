'''
Asterisk/Applications.py: Classes providing Python syntax for Asterisk
applications.

This module may be used for constructing a configuration file writer for
extensions.conf, or with the Dialplan module to remotely configure and
synchronise live Asterisk servers.
'''

import Asterisk




class Error(Asterisk.BaseException):
    'Raised when there is a problem with an application instance.'
    _prefix = 'dialplan application error'




class BaseApplication(object):
    '''
    Base for all application classes, currently it acts as a grouping for these
    classes only, no common services are provided yet.
    '''




class Dial(Application):
    '''
    The standard Dial() application. Accepts the following options:
    
    t  callee_forward      Allow called user to transfer call.
    T  caller_forward      Allow calling user to transfer call.

    x  callee_attended     Allow called user to attended transfer call.
    X  caller_attended     Allow calling user to attended transfer call.

    h  callee_hangup       Allow called user to hangup call.
    H  caller_hangup       Allow calling user to hangup call.

    P  privacy             Enable privacy mode.
    P  privacy_db          Database to use in privacy mode.

    f  force_callerid      Force CallerID to that of extension making call.
    r  indicate_ring       Provide ringing indicator to calling party.
    m  indicate_music      Provide on-hold music to calling party.
    M  connect_exec        Execute named macro upon connection.
    C  reset_cdr           Reset the CDR for this call.
    g  hangup_continue     Continue on in context if destination hangs up.
    A  announce            Play the named file to the callee on connection.
    S  connect_secs        Maximum connection time.
    D  send_dtmf           Send given DTMFs to callee before final connection.
       timeout             Maximum seconds to wait for a connection.
       url                 URL to be sent to callee.
    '''

    # callee_attended and caller_attended are provided by anthm's patch:
    # http://bugs.digium.com/bug_view_page.php?bug_id=0002460


    option_map = {
        'callee_forward':   't',    'caller_forward':   'T',
        'callee_attended':  'x',    'caller_attended':  'X',
        'callee_hangup':    'h',    'caller_hangup':    'H',
        'force_callerid':   'f',    'indicate_ring':    'r',
        'indicate_music':   'm',    'reset_cdr':        'C',
        'hangup_continue':  'g',
    }


    def __init__(self, channels, **options):
        self.channels = channels
        self.options = options

    def set_option(option, value):
        self.options[option] = value

    def __repr__(self):
        return '%s.%s(%r, **%r)' % (
            self.__class__.__module__,
            self.__class__.__name__,
            self.channels,
            self.options
        )

    def __str__(self):
        options = []
        option_map = self.option_map
        timeout = url = ''

        for key, value in self.options.iteritems():
            if key in option_map:
                options.append(option_map[key])
            elif key == 'privacy_db':
                pass
            elif key == 'privacy':
                if 'privacy_db' in options:
                    options.append('P(%s)' % (options[privacy_db],))
                else:
                    options.append('P')
            elif key == 'connect_exec':
                options.append('M(%s)' % (value,))
            elif key == 'announce':
                options.append('A(%s)' % (value,))
            elif key == 'connect_secs':
                options.append('S(%s)' % (value,))
            elif key == 'send_dtmf':
                options.append('D(%s)' % (value,))
            elif key == 'timeout':
                timeout = '|' + str(value)
            elif key == 'url':
                url = '|' + str(value)
            else:
                raise Error('Dial(): unknown option %r', (key,))


        return 'Dial(%s%s|%s%s)' %( \
            '&'.join(map(str, self.channels)),
            timeout,
            ''.join(options),
            url
        )


# >>> print Dial([ 'sip/101', 'sip/102' ],
# >>>     connect_exec = 'fpo',
# >>>     timeout = 60,
# >>>     announce = '/etc/asterisk/sounds/connected'
# >>> )
# Dial(sip/101&sip/102|60|A(/etc/asterisk/sounds/connected)M(fpo))
