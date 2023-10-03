
import appdaemon.plugins.hass.hassapi as hass
from appdaemon.exceptions import ServiceException
import re

class Notifier(hass.Hass):

    def initialize(self):

        self.groups = self.args.get('groups')

        self.zone_by_person_state = { v.get('attributes').get('friendly_name'): k.replace('zone.', '') for k, v in self.get_state('zone').items() }
        self.zone_by_person_state['home'] = 'home'
        self.zone_by_person_state['not_home'] = 'not_home'

        self.register_event_listener()


    def group_from_event_name(self, event_name):
        """
        Return the group value from an event name.

        :param event_name: the event name to extract from.
        :returns: the group as a string if present, otherwise None.
        """
        match = re.search('^notify\\.(.+?)(?:@.*)?$', event_name)
        if match:
            return match.group(1)

        return None


    def notify(self, group, zone_filter, data):
        """
        Notify a group with an optional zone filter applied.

        :param group: the group of notify targets to notify.
        :param zone_filter: the optional zone filter.
        :param data: the notify data to forward to the notify service.
        :returns: None
        """   

        targets = self.targets_in_zone(group, zone_filter)
        for target in targets:
            self.log('call_service \'notify/{target}\''.format(target=target))     
            try:
                self.call_service('notify/' + target, **data)
            except:
                self.log('failed to call_service \'notify/{target}\' - unknown target?'.format(target=target))

        return


    def notify_event_callback(self, event_name, data, kvargs=None):
        """
        Event callback for notify events.

        :param event_name: name of the notify event.
        :param data: notify data to forward to the notify service.
        :param kvargs: zero or more keyword arguments.
        :returns: None
        """
        group = self.group_from_event_name(event_name)
        zone = self.zone_from_event_name(event_name)
        notify_data = self.sanitize_event_data(data)

        self.notify(group, zone, notify_data)


    def register_event_listener(self):
        """
        Registers a callback for notify events based on existing zones.

        :returns: None.
        """        
        zones = { zone.replace('zone.', '') for zone in self.get_state('zone') }

        # even if 'home' should always exist, we add it just to be sure.
        zones.add('home')

        # 'not_home' is not a zone but a possible person state, so we add it.
        zones.add('not_home')

        event_names = []
        for group in self.groups:
            event_names.append('notify.' + group)
            for zone in zones:
                event_names.append('notify.' + group + '@' + zone)

        self.listen_event(self.notify_event_callback, event_names)
        self.log('listening for events: {events}'.format(events=event_names))


    def sanitize_event_data(self, data):
        """
        Return a sanitized notification dictionary from the event data.

        :param data: the dictionary to sanitize.
        :returns: the sanitized dictionary.
        """ 
        if isinstance(data, dict) == False:
            return None

        data.pop('metadata', None)
        return data


    def targets_in_zone(self, group, zone_filter):
        """
        Return the notify targets in the given group filtered by zone.

        :param group: the group containing notify targets.
        :param zone_filter: the optional zone filter.
        :returns: the list of filtered notify targets.
        """ 
        candidates = self.groups.get(group)

        if isinstance(candidates, list) == False:
            return []

        result = []
        for candidate in candidates:
            notify = candidate.get('notify')

            if zone_filter == None:
                # include all members if no zone filter is specified
                result.append(notify)
            else: 
                always_include_in = candidate.get('always_include_in')
                if isinstance(always_include_in, list) and any(zone_filter.lower() == v.lower() for v in always_include_in):
                    result.append(notify)              
                else:
                    person_state = self.get_state(candidate.get('person'))
                    if isinstance(person_state, str) == False:
                        continue

                    person_zone = self.zone_by_person_state[person_state]
                    if isinstance(person_zone, str) == False:
                        continue

                    if zone_filter.lower() == person_zone.lower():
                        result.append(notify)

        return result


    def zone_from_event_name(self, event_name):
        """
        Return the optional zone filter value from an event name.

        :param event: the event name to extract from.
        :returns: the zone as a string if present, otherwise None.
        """
        match = re.search('^notify\\.(?:.+?)@(.*)?$', event_name)
        if match:
            return match.group(1)

        return None


