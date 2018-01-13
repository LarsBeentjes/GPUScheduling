import re

from config import get_config
from logger import get_logger
from utility import is_student
from vd_exception import VDException


NO_ONE = 'NO_ONE'
EVERYONE = 'EVERYONE'
STUDENTS = 'STUDENTS'
NOT_STUDENTS = 'NOT_STUDENTS'

RESERVED_GROUPS = [NO_ONE, EVERYONE, STUDENTS, NOT_STUDENTS]


def strip_whitespaces(text):
    whitespaces_re = re.compile('\s+')

    result = ''
    for line in text:
        result += re.sub(whitespaces_re, '', line)
    return result

class Groups:
    def __init__(self):
        self.m_groups = dict()
        groupfile = get_config().get('groupfile')
        try:
            with open(groupfile, 'r') as group_fp:
                text = strip_whitespaces(group_fp.read())
        except Exception as e:
            raise VDException('Failed to load group file: "{}"'.format(str(e)))

        # matches groups with one or more users
        # eg. 'NW_2018:s000000;'
        # eg. 'NW_2018:s000000,s111111,s22222;'
        group_re = re.compile(
                '([a-zA-Z0-9\_]*)\:([a-z0-9]+)((?:\,(?:[a-z0-9]+))*)\;')
        while text != '':
            match = group_re.match(text)
            if match is None:
                raise VDException('Syntax error in group file')

            group_name = match.group(1)
            group_users = {match.group(2)}
            if match.group(3):
                additional_users = match.group(3).split(',')[1:]
                group_users.update(additional_users)

            if group_name in RESERVED_GROUPS:
                msg = 'group "{}" can not be redefined'.format(group_name)
                raise VDException(msg)
            if group_name in self.m_groups:
                msg = 'Group "{}" defined multiple times'.format(group_name)
                raise VDException(msg)
            text = text[match.end():]

            log_msg = 'Loaded group "{}" with {} users'.format(group_name,
                    len(group_users))
            get_logger().msg(log_msg)
            self.m_groups[group_name] = group_users


    def group_exists(self, group):
        if group in self.m_groups or group in RESERVED_GROUPS:
            return True
        return False


    def in_group(self, group, username):
        if group == NO_ONE:
            return False
        elif group == EVERYONE:
            return True
        elif group == STUDENTS:
            return is_student(username)
        elif group == NOT_STUDENTS:
            return not is_student(username)
        else:
            return username in self.m_groups[group]

