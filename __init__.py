from urllib.request import urlopen
from urllib.parse import urlencode
import json

class Experiment:
    def __init__(self, ip, port=8080):
        self.address = f'http://{ip}:{port}/'
        self.update_config()

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
        return response['result']

    def update_config(self):
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
        return self.api('get?' + params)

    def api(self, cmd):
        '''Sends a generic api call to: "http://{ip}:{port}/{cmd}"'''
        response = urlopen(self.address + cmd)
        return json.loads(response.read().decode())
