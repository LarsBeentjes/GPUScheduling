import json

from vd_exception import VDException


CONFIG = None


def init_config(configfile):
    global CONFIG
    if CONFIG is not None:
        raise VDException('Config can only be initialised once')

    CONFIG = Config(configfile)


def get_config():
    if CONFIG is None:
        raise VDException('Config is not initialised')

    return CONFIG


class Config:
    def __init__(self, configfile):
        self.m_config = {
            'groupfile':            'groups.txt',
            'logfile':              'mailer.log',
            'dup_log_to_stdout':    True,
            'template_dir':         'mailtemplates',
            'rulefile':             'rules.txt',
            'mail_cooldown_file':   'mailcooldown.json',
            'mail_cooldown_time':   24 * 3600,
            'mail_dry_run':         True,
            'mail_from_addr':       'unkown@liacs.leidenuniv.nl'
        }

        try:
            overwrites = json.load(open(configfile, 'r'))
        except Exception as e:
            msg = 'Error while reading config file "{}"'.format(str(e))
            raise VDException(msg)

        for key in overwrites:
            if key not in self.m_config:
                msg = 'Setting illegal key "{}" to value "{}"'.format(key,
                        overwrites[key])
                raise VDException(msg)

            self.m_config[key] = overwrites[key]

        self.__validate()


    def __test_string(self, key):
        if not isinstance(self.m_config[key], str):
            msg = 'key "{}" is expected to be of type string'.format(key)
            raise VDException(msg)


    def __test_boolean(self, key):
        if not isinstance(self.m_config[key], bool):
            msg = 'key "{}" is expected to be of type boolean'.format(key)
            raise VDException(msg)


    def __test_integer(self, key):
        if not isinstance(self.m_config[key], int):
            msg = 'key "{}" is expected to be of type integer'.format(key)
            raise VDException(msg)


    def __validate(self):
        self.__test_string('groupfile')
        self.__test_string('logfile')
        self.__test_boolean('dup_log_to_stdout')
        self.__test_string('template_dir')
        self.__test_string('rulefile')
        self.__test_string('mail_cooldown_file')
        self.__test_integer('mail_cooldown_time')
        self.__test_boolean('mail_dry_run')
        self.__test_string('mail_from_addr')


    def get(self, key):
        if key not in self.m_config:
            raise VDException('Config key "{}" does not exists'.format(key))

        return self.m_config[key]

