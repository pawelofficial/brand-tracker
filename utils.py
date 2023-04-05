import logging 
import datetime 
import os 

class Utils:
    def __init__(self) -> None:
        pass
    
    @staticmethod
    def setup_logger(name, log_file, level=logging.INFO,mode='w'):
        """ sets up logger """
        current_dir=os.path.dirname(os.path.abspath(__file__))
#        log_fp=Utils().path_join(current_dir,'logs',log_file)
        log_fp=os.path.join(current_dir,'logs',log_file)
        handler = logging.FileHandler(log_fp,mode=mode,encoding="utf-8")        
        BASIC_FORMAT = "%(levelname)s:%(name)s:%(message)s"  
        formatter=logging.Formatter(BASIC_FORMAT)
        handler.setFormatter(formatter)
        logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.addHandler(handler)
        Utils().log_variable(logger,msg=f'logger setup {name}')
        return logger
    
    
    @staticmethod
    def log_variable(logger,msg='',lvl='info',**kwargs):
        """ my way of logging variables in the log """
        ts=datetime.datetime.now().isoformat()
        s=f'{msg} {ts}'
        for k,v in kwargs.items():
            s+= f'\n{k} : {v}'
        if lvl=='warning':
            logger.warning(s)
        else:
            logger.info(s)