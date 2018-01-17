import time

from rule_base import RuleBase


def find_gpu(gpu_data, gpu_id):
    for gpu in gpu_data:
        if gpu['id'] == gpu_id:
            return gpu
    return None


class RuleReserve(RuleBase):
    def __init__(self, lineno, affected_groups, template, groups):
        groups_text = ','.join(affected_groups)
        rule_msg = 'Reserve {} at line {}'.format(groups_text, lineno)
        RuleBase.__init__(self, rule_msg, affected_groups, template, groups)


    def update(self, gpu_data, proc_data):
        violators = set()
        for proc in proc_data:
            user = proc['username']

            # affected users are allowed to use the system
            if not self.affected_user(user):
                violators.add(user)
        self.update_violators(violators)


class RuleProcRuntime(RuleBase):
    def __init__(self, lineno, affected_groups, template, max_runtime, groups):
        rule_msg = 'Process Runtime {} at line {}'.format(max_runtime, lineno)
        RuleBase.__init__(self, rule_msg, affected_groups, template, groups)

        self.m_max_runtime = float(max_runtime)


    def update(self, gpu_data, proc_data):
        violators = set()
        for proc in proc_data:
            user = proc['username']

            if not self.affected_user(user):
                continue

            proc_age = time.time() - float(proc['proc_birth'])

            if self.affected_user(user) and proc_age > self.m_max_runtime:
                violators.add(user)
        self.update_violators(violators)


class RuleIdleTime(RuleBase):
    def __init__(self, lineno, affected_groups, template, idle_time, groups):
        rule_msg = 'Process Idle Time {} at line {}'.format(idle_time, lineno)
        RuleBase.__init__(self, rule_msg, affected_groups, template, groups)

        self.m_idle_time = idle_time
        self.m_idling_processes = {}


    def update(self, gpu_data, proc_data):
        # keep a list of pid that can be removed after the loop
        # these processes are not violating the rule any more
        # before the timeout is reached
        idling_processes = list(self.m_idling_processes.keys())
        violators = set()
        now = time.time()

        for proc in proc_data:
            pid = proc['pid']
            user = proc['username']

            if not self.affected_user(user):
                continue

            gpu = find_gpu(gpu_data, proc['gpu_id'])
            utilization = int(gpu['gpu_utilization'].split(' ')[0])
            if utilization < 5: #  less than 5% is considdered idle
                if pid not in self.m_idling_processes:
                    self.m_idling_processes[pid] = now
                if pid in idling_processes:
                    idling_processes.remove(pid)

                if self.m_idling_processes[pid] + self.m_idle_time < now:
                    violators.add(user)

        # remove processess that are not violating anymore
        for pid in idling_processes:
            self.m_idling_processes.pop(pid)

        self.update_violators(violators)


class RuleCalimedGpus(RuleBase):
    def __init__(self, lineno, affected_groups, template, max_gpus, groups):
        rule_msg = 'max {} GPUs claimed at line {}'.format(max_gpus, lineno)
        RuleBase.__init__(self, rule_msg, affected_groups, template, groups)

        self.m_max_claimed_gpus = max_gpus


    def update(self, gpu_data, proc_data):
        users = {}
        for proc in proc_data:
            user = proc['username']

            if not self.affected_user(user):
                continue

            if user in users:
                users[user] += 1
            else:
                users[user] = 1

        violators = set()
        for user in users:
            if users[user] > self.m_max_claimed_gpus:
                violators.add(user)

        self.update_violators(violators)

