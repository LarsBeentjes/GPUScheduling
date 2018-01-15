import os
import socket

from config import get_config
from logger import get_logger
from utility import get_timestring


class Templates:
    def __init__(self):
        config = get_config()
        template_dir = config.get('template_dir')

        self.m_templates = {}

        for template_file in os.listdir(template_dir):
            self.__load_tempate(template_dir, template_file)


    def __load_tempate(self, template_dir, filename):
        logger = get_logger()

        template_name = filename.split('.')[0]
        try:
            with open(template_dir + '/' + filename, 'r') as fp:
                template_text = fp.read()
        except Exception as e:
            logger.msg('Failed to load template "{}", error "{}"'.format(
                template_name, str(e)))
            return

        self.m_templates[template_name] = template_text
        logger.msg('Loaded template "{}"'.format(template_name))


    def generate(self, template, fullname, to_addr):
        text = self.m_templates[template]
        text = text.replace('[FROM_ADDR]', get_config().get('mail_from_addr'))
        text = text.replace('[TO_ADDR]', to_addr)
        text = text.replace('[FULLNAME]', fullname)
        text = text.replace('[SERVER]', socket.gethostname())
        text = text.replace('[TIME]', get_timestring())
        return text


    def template_exits(self, template):
        return template in self.m_templates

