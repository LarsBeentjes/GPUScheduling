import time
import json
import subprocess

from config import get_config
from logger import get_logger
from utility import is_student


def generate_email_address(username, fullname):
    if is_student(username):
        return '{}@umail.leidenuniv.nl'.format(username)
    else:
        mail_name = fullname.replace(' ', '.').replace('..', '.').lower()
        return '{}@liacs.leidenuniv.nl'.format(mail_name)


class Mailer:
    def __init__(self, templates):
        config = get_config()

        self.m_templates = templates
        self.m_cooldown_file = config.get('mail_cooldown_file')
        self.m_cooldown_time = config.get('mail_cooldown_time')
        self.m_dryrun = config.get('mail_dry_run')
        self.__load_cooldown()


    def __send_mail(self, username, fullname, template):
        to_addr = generate_email_address(username, fullname)
        mail_content = self.m_templates.generate(template, fullname, to_addr)

        command = ['/usr/sbin/sendmail', to_addr]
        sendmail_proc = subprocess.Popen(command, stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        bytes_written = sendmail_proc.stdin.write(mail_content.encode('UTF-8'))
        if bytes_written != len(mail_content):
            raise Exception('Partial write')
        sendmail_proc.stdin.close()
        sendmail_proc.wait()

        # Attempty to deliver mail
        subprocess.Popen(['/usr/sbin/sendmail', '-q',],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).wait()


    def __load_cooldown(self):
        try:
            self.m_cooldown = json.load(open(self.m_cooldown_file, 'r'))
        except Exception as e:
            get_logger().msg('No mailcooldown history')
            self.m_cooldown = {}


    def __save_cooldown(self):
        try:
            json.dump(self.m_cooldown, open(self.m_cooldown_file, 'w'))
        except Exception as e:
            get_logger().msg('Failed to save cooldownfile "{}"'.format(str(e)))


    def try_send_mail(self, username, fullname, template):
        if username in self.m_cooldown:
            previous_mail = self.m_cooldown[username]
        else:
            previous_mail = 0

        if previous_mail + self.m_cooldown_time < time.time():
            logger = get_logger()
            logger.msg('Sending mail to "{} ({}) with template "{}"'.format(
                fullname, username, template))
            if not self.m_dryrun:
                self.__send_mail(username, fullname, template)
            self.m_cooldown[username] = time.time()
            self.__save_cooldown()

