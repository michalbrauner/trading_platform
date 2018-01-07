import getopt, os, re


REG_SYMBOLS_SEPARATED_BY_COMA = r'^([a-zA-Z]{6})([,]{1}[a-zA-Z]{6})*$'
REG_NUMBER = r'^[0-9]+$'

BASIC_ARGS = 'hs:o:'


def get_basic_settings(argv, long_opts):
    settings = dict(
        print_help=False,
        symbols=None,
        output_directory=None
    )

    opts, args = getopt.getopt(argv, BASIC_ARGS, long_opts)

    for opt, arg in opts:

        if opt == '-h':
            settings['print_help'] = True
            return settings
        elif opt == '-s':
            settings['symbols'] = arg
        elif opt == '-o':
            settings['output_directory'] = arg

    validate_settings(settings)

    return settings


def validate_settings(settings):
    required_items = ['symbols', 'output_directory']

    for required_item in required_items:
        settings = validate_settings_exists(settings, required_item)

    if re.match(REG_SYMBOLS_SEPARATED_BY_COMA, settings['symbols']) is None:
        raise Exception('symbols needs to be list of symbols separated by coma')
    else:
        settings['symbols'] = settings['symbols'].split(',')

    if os.path.isdir(settings['output_directory']) is False:
        raise Exception('output_directory does not exist')


def validate_settings_exists(settings, settings_item):
    if settings[settings_item] is None:
        raise Exception('Missing value - {} is required'.format(settings_item))

    return settings


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
