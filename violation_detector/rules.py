import re

from config import get_config
from vd_exception import VDException
from rule import RuleReserve
from rule import RuleProcRuntime
from rule import RuleIdleTime
from rule import RuleCalimedGpus


class Rules:
    def __init__(self, groups, templates, mailer):
        self.m_groups = groups
        self.m_templates = templates
        self.m_mailer = mailer

        self.m_rules = []
        self.__load_rules()


    def __check_groups(self, groups, lineno):
        for group in groups:
            if not self.m_groups.group_exists(group):
                msg = 'Group "{}" at line {} does not exist'.format(group,
                        lineno)
                raise VDException(msg)


    def __check_template(self, template, lineno):
        if not self.m_templates.template_exits(template):
            msg = 'Template "{}" at line {} does not exists'.format(template,
                    lineno)
            raise VDException(msg)


    def __add_rule_reserve(self, args, lineno):
        if len(args) != 2:
            msg = 'at line {}, RESERVE requires 2 arguments'.format(lineno)
            raise VDException(msg)

        groups = args[0].strip().split(',')
        template = args[1]

        self.__check_groups(groups, lineno)
        self.__check_template(template, lineno)

        self.m_rules.append(RuleReserve(lineno, groups, template,
            self.m_groups))


    def __add_rule_proc_time(self, args, lineno):
        if len(args) != 3:
            msg = 'at line {}, PROC_TIME requires 3 arguments'.format(lineno)
            raise VDException(msg)

        groups = args[0].strip().split(',')
        template = args[1]
        try:
            proc_time = int(args[2])
        except:
            msg = 'at line {}, PROC_TIME requires integer'.format(lineno)
            raise VDException(msg)

        self.__check_groups(groups, lineno)
        self.__check_template(template, lineno)

        self.m_rules.append(RuleProcRuntime(lineno, groups, template,
            proc_time, self.m_groups))


    def __add_rule_idle_time(self, args, lineno):
        if len(args) != 3:
            msg = 'at line {}, IDLE_TIME requires 3 arguments'.format(lineno)
            raise VDException(msg)

        groups = args[0].strip().split(',')
        template = args[1]
        try:
            proc_time = int(args[2])
        except:
            msg = 'at line {}, IDLE_TIME requires integer'.format(lineno)
            raise VDException(msg)

        self.__check_groups(groups, lineno)
        self.__check_template(template, lineno)

        self.m_rules.append(RuleIdleTime(lineno, groups, template,
            proc_time, self.m_groups))


    def __add_rule_max_claimed_gpus(self, args, lineno):
        if len(args) != 3:
            msg = 'at line {}, MAX_CLAIMED_GPUS requires 3 arguments'.format(
                    lineno)
            raise VDException(msg)

        groups = args[0].strip().split(',')
        template = args[1]
        try:
            proc_time = int(args[2])
        except:
            msg = 'at line {}, MAX_CLAIMED_GPUS requires integer'.format(lineno)
            raise VDException(msg)

        self.__check_groups(groups, lineno)
        self.__check_template(template, lineno)

        self.m_rules.append(RuleCalimedGpus(lineno, groups, template,
            proc_time, self.m_groups))


    def __load_rules(self):
        config = get_config()
        try:
            with open(config.get('rulefile'), 'r') as fp:
                rules = fp.read().splitlines()
        except Exception as e:
            msg = 'Failed to load read rulefile "{}"'.format(str(e))
            raise VDException(msg)

        generic_rule_re = re.compile('^([A-Z\_]+)((?:\s+(?:[^\s]+))+)$')

        lineno = 0
        for rule in rules:
            lineno += 1

            if rule == '' or rule.startswith('#'):
                continue

            rule = rule.strip() #  strip heading and tialing whitespaces
            match = generic_rule_re.match(rule)
            if match:
                rule_type = match.group(1)
                args = match.group(2).split()
                if rule_type == 'RESERVE':
                    self.__add_rule_reserve(args, lineno)
                elif rule_type == 'PROC_TIME':
                    self.__add_rule_proc_time(args, lineno)
                elif rule_type == 'IDLE_TIME':
                    self.__add_rule_idle_time(args, lineno)
                elif rule_type == 'MAX_CLAIMED_GPUS':
                    self.__add_rule_max_claimed_gpus(args, lineno)
                else:
                    msg = 'Invalid rule type "{}" at line {}'.format(
                            rule_type, lineno)
                    raise VDException(msg)
            else:
                raise VDException('Syntax error on line {}'.format(lineno))


    def update(self, gpu_data, proc_data):
        for rule in self.m_rules:
            rule.update(gpu_data, proc_data)

        for proc in proc_data:
            user = proc['username']
            fullname = proc['fullname']
            for rule in self.m_rules:
                if rule.is_violating(user):
                    template = rule.get_template()
                    self.m_mailer.try_send_mail(user, fullname, template)
                    break

