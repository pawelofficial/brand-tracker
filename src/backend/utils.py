import os
import logging


class Utils:
    def __init__(self) -> None:
        self.BASIC_FORMAT="%(levelname)s:%(name)s:%(message)s"
        self.level=logging.INFO
        self.mode='w'
        self.formatter= logging.Formatter(self.BASIC_FORMAT)
        self.logs_dir='logs'
        self.cur_dir=os.path.dirname(os.path.abspath(__file__))
        self.logger=None
        self.log_fp=None    # log filepath 
        
    def setup_logger(self,log_name='log',level=None,mode=None,formatter=None):
        level=level or self.level 
        mode=mode or self.mode
        
        formatter=formatter or self.formatter
        self.log_fp = self.path_join(self.logs_dir, log_name)
        handler = logging.FileHandler(self.log_fp, mode=mode, encoding="utf-8") 
        handler.setFormatter(formatter)
        self.logger = logging.getLogger(log_name)
        self.logger.setLevel(level)
        self.logger.addHandler(handler)
        self.log_variable(self.logger, msg=f'setting up  {log_name} at {self.log_fp} ')
        return self.logger 
        
    def log_variable(self,logger, msg,**kwargs ):
        s=''
        for k,v in kwargs.items():
            s+= f'\n{k} : {v}'
        logger.log(self.level, f'{msg} {s} '   )

    def path_join(self,*args):
        try:
            return os.path.join(self.cur_dir, *args)
        except TypeError:
            logging.error("Arguments must be strings.")
            return None


if __name__=='__main__':
    u=Utils() 
    u.setup_logger(log_name='test.log')
    u.log_variable(logger=u.logger,msg='test',u_logger=u.logger,mode=u.mode)