import logging
import sys


def init_logging(_logger, log_cfg):

    debug = log_cfg['logging']['debug']
    log_levels = {'DEBUG':logging.DEBUG, 'ERROR':logging.ERROR, 'INFO':logging.INFO}
    log_level = log_levels.get(log_cfg['logging']['log_level'], logging.ERROR)
    log_file = log_cfg['logging']['log_file']

    print(sys.platform)
    if sys.platform == 'win32':
        console = logging.StreamHandler()
        console.setLevel(log_level)
        console.setFormatter(logging.Formatter('%(levelname)s[%(asctime)s]:%(message)s',datefmt='%Y-%m-%d %H:%M:%S'))
        _logger.addHandler(console)
        _logger.setLevel(log_level)
    else:
        if debug.lower() != "true":
            log_level = logging.ERROR
        file=logging.FileHandler(log_file,'a')
        file.setLevel(log_level)
        file.setFormatter(logging.Formatter('%(levelname)s[%(asctime)s]:%(message)s',datefmt='%Y-%m-%d %H:%M:%S'))
        _logger.addHandler(file)
        _logger.setLevel(log_level)

logger = logging.getLogger("tenant_site")
