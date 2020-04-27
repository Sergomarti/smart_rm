import logging

logger = logging.getLogger('smartRM')
bracket_handler = logging.StreamHandler()
bracket_format = logging.Formatter('%(mess)s')
bracket_handler.setFormatter(bracket_format)
bracket_handler.setLevel(logging.DEBUG)
logger.setLevel(logging.DEBUG)
logger.addHandler(bracket_handler)

if __name__ == '__main__':
    my_log = logging.getLogger('SmartRM')
    my_log.debug('Debug information')
    my_log.info('Information')
    my_log.warning('Warning')
    my_log.error('Error')
    my_log.critical('Critical error')
