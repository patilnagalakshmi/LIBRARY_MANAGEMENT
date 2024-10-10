import logging

def setup_logger(log_file, level=logging.DEBUG):
    logger = logging.getLogger('lib_management')
    logger.setLevel(level)

    file_handler = logging.FileHandler(log_file)
    console_handler = logging.StreamHandler()

    file_handler.setLevel(level)
    console_handler.setLevel(logging.DEBUG)  

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s-%(name)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
