from logger import get_logger


class RuleBase:
    def __init__(self, rulename, affected_groups, template, groups):
        self.m_rulename = rulename
        self.m_violators = set()
        self.m_affected_groups = affected_groups
        self.m_template = template
        self.m_groups = groups


    def affected_user(self, user):
        for group in self.m_affected_groups:
            if self.m_groups.in_group(group, user):
                return True
        return False


    def update_violators(self, violators):
        new_violators = violators.difference(self.m_violators)
        stopped_violators = self.m_violators.difference(violators)
        self.m_violators = violators

        logger = get_logger()
        for user in new_violators:
            logger.msg('user "{}" is violating rule "{}"'.format(user,
                self.m_rulename))

        for user in stopped_violators:
            logger.msg('user "{}" stopped violating rule "{}"'.format(user,
                self.m_rulename))


    def is_violating(self, user):
        return user in self.m_violators


    def get_template(self):
        return self.m_template

