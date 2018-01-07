import getopt, os, re, datetime


DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S'

REG_DATETIME_DATE_PART = r'[0-9]{4}[-]{1}[0-9]{2}[-]{1}[0-9]{2}'
REG_DATETIME_TIME_PART = r'[0-9]{2}[:]{1}[0-9]{2}[:]{1}[0-9]{2}'
REG_DATETIME = r'^{}T{}$'.format(REG_DATETIME_DATE_PART, REG_DATETIME_TIME_PART)

REG_SYMBOLS_SEPARATED_BY_COMA = r'^([a-zA-Z]{6})([,]{1}[a-zA-Z]{6})*$'
REG_NUMBER = r'^[0-9]+$'


class BasicArgsParser(object):

    def validate_settings_is_number_and_set_to_int(self, settings, settings_item, is_required=True):
        """

        :type settings: {}
        :type settings_item: str
        :type is_required: bool
        :return {}
        """

        if is_required:
            self.validate_settings_exists(settings, settings_item)

        if settings[settings_item] is None:
            return settings

        if re.match(REG_NUMBER, settings[settings_item]) is None:
            raise Exception('{} needs to be a number'.format(settings_item))
        else:
            settings[settings_item] = int(settings[settings_item])

        return settings

    def validate_settings_is_datetime_and_set_to_datetime_object(self, settings, settings_item, is_required=True):
        """

        :type settings: {}
        :type settings_item: str
        :type is_required: bool
        :return {}
        """
        if is_required:
            self.validate_settings_exists(settings, settings_item)

        if settings[settings_item] is None:
            return settings

        if re.match(REG_DATETIME, settings[settings_item]) is None:
            raise Exception('{} needs to be in \'yyyy-mm-ddThh:mm:ss\' format'.format(settings_item))
        else:
            settings[settings_item] = datetime.datetime.strptime(settings[settings_item], DATETIME_FORMAT)

        return settings

    def validate_settings_exists(self, settings, settings_item):
        """

        :type settings: {}
        :type settings_item: str
        :return {}
        """
        if settings[settings_item] is None:
            raise Exception('Missing value - {} is required'.format(settings_item))

        return settings
