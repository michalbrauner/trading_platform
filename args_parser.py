import getopt, os, re, datetime


DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S'
REG_SYMBOLS_SEPARATED_BY_COMA = r'^([a-zA-Z]{6})([,]{1}[a-zA-Z]{6})*$'
REG_NUMBER = r'^[0-9]+$'

REG_DATETIME_DATE_PART = r'[0-9]{4}[-]{1}[0-9]{2}[-]{1}[0-9]{2}'
REG_DATETIME_TIME_PART = r'[0-9]{2}[:]{1}[0-9]{2}[:]{1}[0-9]{2}'
REG_DATETIME = r'^{}T{}$'.format(REG_DATETIME_DATE_PART, REG_DATETIME_TIME_PART)

BASIC_ARGS = 'hd:s:c:b:o:'


def get_basic_settings(argv, long_opts):
    settings = dict(
        print_help=False,
        data_directory=None,
        symbols=None,
        initial_capital_usd=None,
        start_date=None,
        output_directory=None
    )

    opts, args = getopt.getopt(argv, BASIC_ARGS, long_opts)

    for opt, arg in opts:

        if opt == '-h':
            settings['print_help'] = True
            return settings
        elif opt == '-d':
            settings['data_directory'] = arg
        elif opt == '-s':
            settings['symbols'] = arg
        elif opt == '-c':
            settings['initial_capital_usd'] = arg
        elif opt == '-b':
            settings['start_date'] = arg
        elif opt == '-o':
            settings['output_directory'] = arg

    validate_settings(settings)

    return settings


def validate_settings(settings):
    required_items = ['data_directory', 'symbols', 'start_date', 'output_directory']
    for required_item in required_items:
        settings = validate_settings_exists(settings, required_item)

    if os.path.isdir(settings['data_directory']) is False:
        raise Exception('data_directory does not exist')

    if re.match(REG_SYMBOLS_SEPARATED_BY_COMA, settings['symbols']) is None:
        raise Exception('symbols needs to be list of symbols separated by coma')
    else:
        settings['symbols'] = settings['symbols'].split(',')

    validate_settings_is_number_and_set_to_int(settings, 'initial_capital_usd')
    validate_settings_is_datetime_and_set_to_datetime_object(settings, 'start_date')

    if os.path.isdir(settings['output_directory']) is False:
        raise Exception('output_directory does not exist')


def validate_settings_is_number_and_set_to_int(settings, settings_item, is_required=True):
    if is_required:
        validate_settings_exists(settings, settings_item)

    if settings[settings_item] is None:
        return settings

    if re.match(REG_NUMBER, settings[settings_item]) is None:
        raise Exception('{} needs to be a number'.format(settings_item))
    else:
        settings[settings_item] = int(settings[settings_item])

    return settings


def validate_settings_is_datetime_and_set_to_datetime_object(settings, settings_item, is_required=True):
    if is_required:
        validate_settings_exists(settings, settings_item)

    if settings[settings_item] is None:
        return settings

    if re.match(REG_DATETIME, settings[settings_item]) is None:
        raise Exception('{} needs to be in \'yyyy-mm-ddThh:mm:ss\' format'.format(settings_item))
    else:
        settings[settings_item] = datetime.datetime.strptime(settings[settings_item], DATETIME_FORMAT)

    return settings


def validate_settings_exists(settings, settings_item):
    if settings[settings_item] is None:
        raise Exception('Missing value - {} is required'.format(settings_item))

    return settings
