from urllib.request import urlopen
from urllib.parse import urlencode
from urllib.error import URLError
from threading import Thread
from dataclasses import dataclass
import json

@dataclass
class Phone:
    version: str
    build: str
    file_format: str
    devide_model: str
    device_board: str
    devide_manufacturer: str
    device_base_os: str
    device_codename: str
    device_release: str
    depth_front_sensor: str
    depth_back_sensor: str
    sensors: list

@dataclass
class Sensor:
    type: str
    name: str
    vendor: str
    range: float
    resolution: float
    min_delay: int
    max_delay: int
    power: float
    version: int

@dataclass
class Experiment:
    crc32: str
    title: str
    local_title: str
    category: str
    local_category: str


class RemoteInterface:
    '''
    Interface with phyphox's API
    Read more on https://phyphox.org/wiki/index.php/Remote-interface_communication
    '''

    def __init__(self, ip, port=8080):
        self.address = f'http://{ip}:{port}/'

    def get(self, buffers=[], threshold=None, reference=''):
        '''Retrieves buffer data'''
        response = self._api('get',params)

    def start(self):
        '''Starts the experiment'''
        response = self._api('control',{'cmd':'start'})
        return response['result']

    def stop(self):
        '''Stops the experiment'''
        response = self._api('control',{'cmd':'stop'})
        return response['result']

    def clear(self):
        '''Clear all buffers'''
        response = self._api('control',{'cmd':'clear'})
        return response['result']

    def config(self):
        resp = self._api('config')

        exp = Experiment(
                        resp['crc32'],
                        resp['title'],
                        resp['localTitle'],
                        resp['category'],
                        resp['localCategory']
                        )

        buffer_sizes = {}
        for buff in resp['buffers']:
            buffer_sizes[buff['name']] = buff['size']

        inputs = {}
        for sensor in resp['inputs']:
            sensor_name = sensor['source']
            sensor_data = {}
            for out in sensor['outputs']:
                out_name = list(out.keys())[0]
                buffer_name = out[out_name]
                sensor_data[out_name] = buffer_name
            inputs[sensor_name] = sensor_data

        sets = {}
        for set in resp['export']:
            set_name = set['set']
            set_data = {}
            for src in set['sources']:
                set_data[src['buffer']] = src['label']
            sets[set_name] = set_data

        return exp, buffer_sizes, inputs, sets

    def meta(self):
        '''
        tip: pd.DataFrame(exp.meta())
        https://phyphox.org/wiki/index.php/Network_Connections#Metadata
        '''
        response = self._api('meta')
        return response['sensors'] #for now

    def time(self):
        response = self._api('time')
        return response

    def _api(self, cmd, params={}, timeout=10):
        '''Sends a generic api call to: "http://{ip}:{port}/{cmd}?{params_key=params_value}"'''
        url = f'{self.address}{cmd}?{urlencode(params)}'
        response = urlopen(url, timeout=timeout)
        return json.loads(response.read().decode())





















class old_Experiment:
    def __init__(self, ip, port=8080):
        self.address = f'http://{ip}:{port}/'
        self._update_config()
        self.buffers = {}
        for name in self.bufferNames:
            self.buffers[name] = []
        self.update_thread = Thread(target=self._auto_update)
        self.update_thread.start()

    def start(self):
        '''Starts the experiment'''
        response = self.api('control?cmd=start')
        return response['result']

    def stop(self):
        '''Stops the experiment'''
        response = self.api('control?cmd=stop')
        return response['result']

    def clear(self):
        '''Clear all buffers'''
        response = self.api('control?cmd=clear')
        self.buffers = {}
        for name in self.bufferNames:
            self.buffers[name] = []
        return response['result']

    def _update_config(self):
        '''Updates the known experiment configuration'''
        config = self.api('config')
        self.crc32 = config['crc32']
        self.title = config['title']
        self.localTitle = config['localTitle']
        self.category = config['category']
        self.localCategory = config['localCategory']
        self.bufferNames = []
        for b in config['buffers']:
            self.bufferNames.append(b['name'])
        self.time_buffer_candidates = self.bufferNames.copy()
        return

    def get(self, buffers=None, threshold=None):
        '''Retrieves buffer data'''
        if buffers is None:
            buffers = self.bufferNames
        if threshold is None:
            threshold = 'full'
        params = {}
        for b in buffers:
            params[b] = str(threshold)
        params = urlencode(params, safe='|')
        data =  self.api('get?' + params)
        response = {}
        for name in data['buffer']:
            response[name] = data['buffer'][name]['buffer']
        return response

    def api(self, cmd):
        '''Sends a generic api call to: "http://{ip}:{port}/{cmd}"'''
        response = urlopen(self.address + cmd) #NEED A TIMEOUT and urllib.error.URLError handling!!!
        return json.loads(response.read().decode())

    def _time_buffer_candidates_check(self):
        not_time_buffers = []
        for name in self.time_buffer_candidates:
            data = self.buffers[name]
            if self._is_not_growing(data):
                not_time_buffers.append(name)
        for name in not_time_buffers:
            self.time_buffer_candidates.remove(name)
        return self.time_buffer_candidates[0]

    def _is_not_growing(self, data):
        for i in range(len(data)-1):
            if data[i+1] <= data[i]:
                return True
        return False

    def _update_buffers(self):
        time_buffer_name = self._time_buffer_candidates_check()
        try:
            last_time = self.buffers[time_buffer_name][-1]
            time_threshold = f'{last_time}|{time_buffer_name}'
        except IndexError:
            time_threshold = None
        data = self.get(threshold=time_threshold)
        for name in data.keys(): #Duplicating data here!
            self.buffers[name] = self.buffers[name] + data[name]
        return

    def _auto_update(self):
        while True:
            self._update_buffers()
