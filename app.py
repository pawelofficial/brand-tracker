from typing import Any
from flask import Flask, render_template, request , jsonify
import logging 
#logging.basicConfig(filename='./logs/flask.log', level=logging.DEBUG, 
#                    format='%(asctime)s:%(levelname)s:%(message)s')
from mypg import mypg
from utils import Utils

# logs all state variables of a class 
class traceback:
    def __init__(self,c) -> None:
        self.c=c
        self.utils=Utils()
        self.logger= self.utils.setup_logger(name='trace_log',log_file=f'trace_log.log')
        self.utils.log_variable(logger=self.logger,msg=f" traceback for class {self.c.__class__.__name__}")
        
    def log_state(self,exclude=['logger','utils','pg']):
        v=vars(self.c)
        for k,v in v.items():
            if k in exclude:
                continue
            self.utils.log_variable(logger=self.logger,msg=f' {self.c.__class__.__name__}.{k} = {v}')



# class for storing usr stuff with little flexibility 
class usr_json:
    def __init__(self ):
        self.data = {}                                                # json 
        self.premium=True                                             # premium account status                   
        self.list_keys=['channels','keywords']                        # list data 
        self.scalar_keys=['username','email','sentiment','frequency'] # scalar data  
        self.keys=self.list_keys+self.scalar_keys  
        
        for key in self.list_keys:
            self.data[key]=[]
        
        for key in self.scalar_keys:
            self.data[key]=None
        
        
    def __getitem__(self, key):
        if key not in self.keys: # error handling for missing keys 
            print('no such key')
            return None 
        return self.data[key]
    
    
    def __setitem__(self, key, value):
        if key not in self.keys: # append key to keys 
            print('warning, no such key defined')
            return None
        
        if key in self.scalar_keys:
            self.data[key]=value
        
        if key in self.list_keys:
            self.data[key].append(value)
            self.data[key]=list(set(self.data[key]))
            
            
            
            
    def __repr__(self):
        return str(self.data)
    
    def __str__(self): 
        return str(self.data)


u=usr_json()
print(u)
u['channels']='foo'
u['channels']='bar'
u['keywords']='foo'
u['keywords']='foo'
u['keywords']='bar'
u['foo']='bar'
u['username']='bar'
u['username']='kez'
u['sentiment']=True
print(u)

 



class website:
    def __init__(self) -> None:
        self.utils=Utils()
        self.logger= self.utils.setup_logger(name='website_log',log_file=f'website_log.log')
        self.pg=mypg()
        self.channels=self.pg.get_channels()
        self.configs={'foo':'bar','kez':'bark'}
        self.json=usr_json()
        
        
    @property
    def channels(self):
        return self._channels
    
    @channels.setter
    def channels(self, value):
        #self.utils.log_variable(logger=self.logger,msg=f"self.channels = {value}")
        self._channels = value
        
        
w=website()
t_w=traceback(c=w)

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('home.html'
                           , python_d_items = lambda d: d.items()
                           , title='My Website'
                           , content1='FOOBAR'
                           , content2='BARKEZ'
                           , services=['Service 1', 'Service 2', 'Service 3']
                           ,channels=w.channels
                           ,configs = w.configs
                           )




@app.route('/channels', methods=['POST'])
def checklist():
    print('checklist ')
    t_w.log_state()
    data = request.json             # get data from website 
    name, isChecked =data['name'],data['isChecked']
    w.channels[name]=isChecked      # write data to website object
    t_w.log_state()
    return jsonify({'message': 'Success'})



if __name__=='__main__':
    app.run(debug=True)
    