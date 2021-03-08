import logging
import logging.config
from os import path

def get_logger(mode):
    ## Get_Logger Function
    ## Description:     Determines which log configuration to use based on optional arguments
    ## Arguments:       mode - string - any profile names passed to script as arguments 
    ## Return:          loghandler object
    # create logger
    log_file_path = path.join(path.dirname(path.abspath(__file__)), 'logging.config')
    logging.config.fileConfig(log_file_path)
    # Fetch the right handler for our purposes
    if mode == "debug":
        logger = logging.getLogger('debug')
        logger_test(logger)
    if mode == "test":
        logger = logging.getLogger('test')
        logger_test(logger)
    else:
        logger = logging.get_logger('default')
        logger_test(logger)
    return logger

    
def logger_test(logger):
    ## Logger_Test Function
    ## Description:     Tests each logstream.
    ## Arguments:       logger - loghandler object - the logger we want to test
    ## Return:          None
    try:
        logger.debug('debug message')
        logger.info('info message')
        logger.warning('warn message')
        logger.error('error message')
        logger.critical('critical message')
    except Exception as e:
        # If we can't log, raise Exception and exit
        raise Exception(e)