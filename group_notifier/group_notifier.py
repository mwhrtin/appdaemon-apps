
import appdaemon.plugins.hass.hassapi as hass
from appdaemon.exceptions import ServiceException
import re
import json

class GroupNotifier(hass.Hass):

    def initialize(self):

        self.cached_zones = self.sanitized_zones()
        self.cached_zones_by_friendly_name = self.sanitized_zones_by_friendly_name()
        self.event_listener_handlers = []
        self.groups = self.args.get('groups')

        self.update_group_notifier_entities()
        self.listen_state(self.zone_is_changed, 'zone', attribute = 'all')
        self.register_event_listener()        

        self.zone_by_person_state = { v.get('attributes').get('friendly_name'): k.replace('zone.', '') for k, v in self.get_state('zone').items() }
        self.zone_by_person_state['home'] = 'home'
        self.zone_by_person_state['not_home'] = 'not_home'


    def event_names(self):
        """
        Return a sorted list of all event names.

        :returns: a list containing all event names.
        """
        event_names = []
        for group in self.groups:
            event_names.append('notify.' + group)
            for zone in self.cached_zones:
                event_names.append('notify.' + group + '@' + zone)

        event_names.sort()

        return event_names


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
        self.log('notify.data: {}'.format(data))
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
        notify_data = self.sanitized_event_data(data)

        self.notify(group, zone, notify_data)


    def register_event_listener(self):
        """
        Registers a callback for notify events based on existing zones.

        Any previous event listeners are first removed before registering
        the new callbacks.

        :returns: None.
        """ 
        for event_listener_handler in self.event_listener_handlers:
            self.cancel_listen_event(event_listener_handler)
        self.event_listener_handlers = []

        event_names = self.event_names()
        self.event_listener_handlers = self.listen_event(self.notify_event_callback, event_names)


    def sanitized_event_data(self, data):
        """
        Return a sanitized notification dictionary from the event data.

        :param data: the dictionary to sanitize.
        :returns: the sanitized dictionary.
        """ 
        if isinstance(data, dict) == False:
            return None

        sanitized = dict()
        sanitized['title'] = data.get('title', '')
        sanitized['message'] = data.get('message', '')

        if isinstance(data.get('data'), dict) == True:
            sanitized['data'] = data.get('data')

        return sanitized

    def sanitized_zones(self):
        """
        Return a list of the zones available at Home Assistant startup.

        Home Assistant doesn't update the list of zones if a zone is removed
        or added. The list of zones available during startup is all we get.

        :returns: a list containing the available zones as strings.
        """
        zones = { zone.replace('zone.', '') for zone in self.get_state('zone') }

        # even if 'home' should always exist, we add it just to be sure.
        zones.add('home')

        # 'not_home' is not a zone but a possible person state, so we add it.
        zones.add('not_home')

        return zones


    def sanitized_zones_by_friendly_name(self):
        """
        Return a dictionary of the zones available at Home Assistant startup.

        Home Assistant doesn't update the list of zones if a zone is removed
        or added. The list of zones available during startup is all we get.

        :returns: a dictionary containing the available zones.
        """
        dictionary = dict()
        for k,v in self.get_state('zone').items():
            key = v.get('attributes', dict()).get('friendly_name', '')
            dictionary[key] = k.replace('zone.', '')

        # even if 'home' should always exist, we add it just to be sure.
        if 'home' not in dictionary:
            dictionary['home'] = 'home'

        # 'not_home' is not a zone but a possible person state, so we add it.
        if 'not_home' not in dictionary:
            dictionary['not_home'] = 'not_home'

        return dictionary


    def update_group_notifier_entities(self):
        """
        Updates the group notifiers custom entities.

        This method creates these two entites:
        - group_notifier.groups
        - group_notifier.zones

        The entites have the available groups and zones as attributes.
        This to enable selecting group and zone from a blueprint. 

        :returns: None.
        """ 

        self.log('event_names: {}'.format(self.event_names()))
        self.set_state('group_notifier.events', state = 'ready', attributes = dict(map(lambda x: (x, x), self.event_names())))
        

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

                    person_zone = self.zone_for_person_state(person_state)
                    if isinstance(person_zone, str) == False:
                        continue

                    if zone_filter.lower() == person_zone.lower():
                        result.append(notify)

        return result


    def zone_is_changed(self, entity, attribute, old, new=None, kwargs=None):
        """
        Handle when a new zone is added.

        Home Assistant does notify us if zones are removed, only if they are 
        added. If a zone is reported as changed (added), we'll add it to our
        list of zones and register for event listening again with the update
        values.

        :returns: None
        """
        zone = entity.replace('zone.', '')
        friendly_name = new.get('attributes', dict()).get('friendly_name', '')

        if zone not in self.cached_zones:
            self.cached_zones.add(zone)

        if friendly_name not in self.cached_zones_by_friendly_name:
            self.cached_zones_by_friendly_name[friendly_name] = zone

        self.register_event_listener()
        self.update_group_notifier_entities()


    def zone_for_person_state(self, person_state):
        """
        Return the zone for the given person state.

        :param person_state: the person state to lookup zone for.
        :returns: the zone as string if found, otherwise None.
        """
        if isinstance(person_state, str) == False:
            return None

        
        #zone_by_person_state = { v.get('attributes').get('friendly_name'): self.cached_zones }
        zone_by_person_state = { v.get('attributes').get('friendly_name'): k.replace('zone.', '') for k, v in self.get_state('zone').items() }
        zone_by_person_state['home'] = 'home'
        zone_by_person_state['not_home'] = 'not_home'

        return zone_by_person_state.get(person_state)


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
