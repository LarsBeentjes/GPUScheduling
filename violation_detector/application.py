import sys
import time

from templates import Templates
from groups import Groups
from rules import Rules
from mailer import Mailer
from MonitorClient import MonitorClient
from config import get_config
from logger import get_logger

class Application:
    def __init__(self):
        if get_config().get('mail_dry_run'):
            get_logger().msg('Dryrun is enabled, no mails will be sent')

        templates = Templates()
        self.m_groups = Groups()
        mailer = Mailer(templates)
        self.m_rules = Rules(self.m_groups, templates, mailer)

    def run(self):
        monitor_client = MonitorClient('/tmp/monitor.socket')

        while True:
            gpu_data = monitor_client.get_gpu_data()
            proc_data = monitor_client.get_process_data()

            self.m_rules.update(gpu_data, proc_data)
            time.sleep(10.0)
