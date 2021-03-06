# !/usr/bin/python
# -*- coding: utf-8 -*-


import sys
import requests
import logging
import simplejson as json
from  datetime import date

class BehavioralCohortsApi(object):
    """ BehaivioralCohortsApi class.

    The Behavioral Cohorts API can be used to list all your cohorts in Amplitude,
    export a cohort in Amplitude, or upload a cohort.

    For more information please read:
    https://amplitude.zendesk.com/hc/en-us/articles/206214068- \
    Behavioral-Cohorts-API

    """

    ERROR_CODES = ['401','400','429','500']

    def __init__(self, projects_handler, show_logs=False):

        self.logger = self._logger_config(show_logs)
        self.projects_handler = projects_handler
        self.api_url = 'https://amplitude.com/api/3/cohorts'
        self.auth = (self.projects_handler.api_key,
                     self.projects_handler.secret_key)

    @staticmethod
    def _logger_config(show_logs):
        """A static method configuring logs"""

        if show_logs:
            logger = logging.getLogger()
            logger.setLevel(logging.DEBUG)
            logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            logger.disabled = False
            return logger
        else:
            logger = logging.getLogger()
            logger.disable  = True
            logger.propagate = False

        return logger

    def get_cohort(self, cohort_id, props=0, propKeys=[]):
        """ Get a discoverable cohort using its string ID.

           Args:
                param1: (optional) Set to 1 to include user properties in the
                response object in addition to Amplitude IDs and user IDs.
                param1type: int
                param2: One or more user properties to include in the response.
                If left undefined, then props=1 will return ALL available user
                properties.
                param2type: str[]

            Returns:
                A json format object with the cohort information.

            Raises:
                Raises an exception if parameters are wrong or cohort
                does not exists.
        """
        if props == 0 and propKeys !=[]:
            self.logger.warn('Pyamplitude:BehavioralCohortsApi.check_created_cohort: \
            no propKeys defined')
        else:
            try:
                url = self.api_url + '/{}?props={}'.format(cohort_id, props)
                if props == 1 and propKeys != []:
                    propKeys = [''] + propKeys
                    url +=  '&propKeys='.join(propKeys)
                response = requests.get(url, auth=self.auth)
                cohort = json.loads(response.text)

                return cohort

            except:
                self.logger.exception('Pyamplitude:BehavioralCohortsApi.check_created_cohort')

                return None

    def list_all_cohorts(self):
        """ Get all cohorts for specific app.

        Returns:
            A list with all created cohorts.
        """
        try:
            response = requests.get(self.api_url, auth=self.auth)
            cohorts = json.loads(response.text)

            return cohorts['cohorts']

        except:
            self.logger.exception('Pyamplitude:BehavioralCohortsApi.list_cohorts')

            return None

    def upload_cohort_from_ids(self, name='', app_id='', id_type='', ids='',
                               owner='', published=True):
        """ A cohort can be generated by uploading a set of User IDs or Amplitude
           IDs.The type of id being sent in the ids field.

          Args:
               param1: name (required)
               response object in addition to Amplitude IDs and user IDs.A string
               name to be used for the cohort.
               param1type: string
               param2: app_id (required) - The project identifier for the
               Amplitude project containing the cohort.
               param2type: int
               param3: id_type (required) - BY_AMP_ID | BY_USER_ID
               param3type:
               param4: ids (required)  One or more user or Amplitude IDs to
               include in the cohort.The type of the IDs should be specified in
               the id_type field.
               param4type:
               param5: owner (required) The login email of the cohort's owner
               in Amplitude.
               param5type: string
               param6: published (required) Whether the cohort is discoverable
               or hidden.
               param5type: boolean

           Returns:
               True if cohort is properly created.

           Raises:
               Raises an exception if any problem happens while the cohort is
               beign created or any individual parameters has not been properly
               set.
        """

        if name == '' and owner == '':
            error_message = 'Pyamplitude:PyAmplitude:BehavioralCohortsApi.upload_cohort_from_ids: Cohort name and owner must be defined'
            self.logger.error(error_message)

            raise ValueError(error_message)

        if ids == []:
            error_message = 'Pyamplitude:BehavioralCohortsApi.upload_cohort_from_ids: A list of ids must be defined'
            self.logger.error(error_message)

            raise ValueError(error_message)

        if id_type != 'BY_AMP_ID' and 'BY_USER_ID':
            error_message = 'Pyamplitude:BehavioralCohortsApi.upload_cohort_from_ids: id_type options are: BY_AMP_ID or BY_USER_ID'
            self.logger.error(error_message)

            raise ValueError(error_message)

        if published != True and False:
            error_message = 'Pyamplitude:BehavioralCohortsApi.upload_cohort_from_ids: published can only take True or false values'
            self.logger.error(error_message)

            raise ValueError(error_message)

        url = self.api_url + '/' + 'upload'

        data = {"name":      name,
                "app_id":    app_id,
                "id_type":   id_type,
                "ids":       ids,
                "owner":     owner,
                "published": published}

        data = json.dumps(data)

        headers = {"Content-Type": "application/json"}

        new_cohort = requests.post(url
                                   ,data=data
                                   ,auth=self.auth,
                                   headers=headers)
        confirmation = new_cohort.text

        if str(new_cohort.status_code) in BehavioralCohortsApi.ERROR_CODES:
            error_message = 'Pyamplitude:BehavioralCohortsApi.upload_cohort_from_ids:' + confirmation
            self.logger.warn(error_message)

            return False

        else:
            self.logger.info('Pyamplitude:BehavioralCohortsApi.upload_cohort_from_ids:  \
            Cohort created OK' + confirmation)

            return True
