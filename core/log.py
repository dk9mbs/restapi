import logging

def create_logger(name):
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(name)s %(levelname)s:%(module)s - %(message)s')
    #formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')
    handler = logging.StreamHandler()
    #handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    #logger.setLevel(logging.DEBUG)
    #logger.addHandler(handler)
    return logger
