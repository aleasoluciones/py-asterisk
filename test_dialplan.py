#!/usr/bin/env python2.3

from Asterisk import Manager, Config, Util


class MyManager(Manager.Manager):
    def ContextDump(self, context):
        id = self._write_action('ContextDump', {
            'Context': context
        })

        context = {}

        def ExtensionInfo(self, event):
            context[event.Exten] = {}

        def ExtensionPriorityInfo(self, event):
            e = self.strip_evinfo(event)
            e.pop('Registrar')
            e.pop('Context')

            context[e.pop('Exten')][e.pop('Priority')] = e

        def ContextDump(self, event):
            pass

        def ContextDumpComplete(self, event):
            stop_flag[0] = True


        events = Util.EventCollection([
            ExtensionInfo, ExtensionPriorityInfo,
            ContextDump, ContextDumpComplete
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

import pprint
pbx = MyManager(*Config.Config().get_connection())
Util.dump_human(pbx.ContextDump('local_extensions'))
