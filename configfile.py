from xml.etree.cElementTree import Element,SubElement,dump,indent,tostring

class File:

    def __init__(self,sensors, views, broker_ip=None, title='Pyphox', category='Pyphox', icon='Py', description='Generated with Pyphox'):
        self.root = Element('phyphox',{'version':'1.11', 'locale':'en'})
        #metadata
        self.title       = SubElement(self.root, 'title')
        self.category    = SubElement(self.root, 'category')
        self.icon        = SubElement(self.root, 'icon')
        self.description = SubElement(self.root, 'description')

        self.title.text       = title.strip()
        self.category.text    = category.strip()
        self.icon.text        = icon.strip()
        self.description.text = description.strip()

        #data
        self.data_containers = SubElement(self.root, 'data-containers')
        self.network = SubElement(self.root, 'network')
        self.input = SubElement(self.root, 'input')
#         self.output = SubElement(self.root, 'output')
#         self.analysis = SubElement(self.root, 'analysis')
        self.views = SubElement(self.root, 'views')
        self.export = SubElement(self.root, 'export')

        #adding stuff
        self.add_data_conteiners(sensors)
        if broker_ip is not None:
            self.add_mqtt_connection(broker_ip, sensors)
        self.add_input(sensors)
        for view in views:
            self.add_view(view)



    def add_data_conteiners(self, sensors):
        if type(sensors) is not list:
            sensors = [sensors]

        for sensor in sensors:
            for output in sensor.outputs:
                buffer = SubElement(self.data_containers, 'container', size='0')
                buffer.text = f'{sensor.abrev}_{output}'
        return

    def add_mqtt_connection(self, broker_ip, sensors):
        if type(sensors) is not list:
            sensors = [sensors]

        for sensor in sensors:
            attr = {
                'address': broker_ip,
                'AutoConnect':'true',
                'service': 'mqtt/csv',
                'conversion': 'none',
                'interval': str(sensor.interval)
            }
            conn = SubElement(self.network, 'connection', attr)
            for output in sensor.outputs:
                attr = {
                    'id': f'{self.title.text}/{sensor.abrev}/{output}'.lower(),
                    'datatype': f'number'
                }
                send = SubElement(conn, 'send', attr)
                send.text = f'{sensor.abrev}_{output}'
        return

    def add_input(self, sensors):
        if type(sensors) is not list:
            sensors = [sensors]

        for sensor in sensors:
            params = {
                'type': sensor.name,
                'rate': str(1/sensor.interval)
            }
            sensor_tag = SubElement(self.input, 'sensor', params)
            for output in sensor.outputs:
                output_tag = SubElement(sensor_tag, 'output', component=output)
                output_tag.text = f'{sensor.abrev}_{output}'
        return

    def add_view(self, sensor_views, label='View'):
        if type(sensor_views) is not list:
            sensor_views = [sensor_views]

        view = SubElement(self.views, 'view', label=label)
        for sensor_view in sensor_views:
            sensor_view(view)

    def save(self, name):
        with open(f'{name}.xml','wt') as file:
            file.write(tostring(self.root, encoding='unicode'))
        return

    def display(self):
        indent(self.root)
        dump(self.root)
        return


class Sensor:

    def __init__(self, name, abrev, interval, outputs):
        self.name = name
        self.abrev = abrev
        self.interval = interval
        self.outputs = outputs

    def graph(self, view):   #COM ERRO: sobrescreve o valor de Y e mostra só o abs
        params = {
            'label': self.name,
            'size': '2',
            'precision': '2'
        }
        graph = SubElement(view, 'graph', params)
        outputs_without_t = self.outputs.copy()
        outputs_without_t.remove('t')
        for output in outputs_without_t:
            value = SubElement(graph, 'input', axis='y')
            value.text = f'{self.abrev}_{output}'
        time = SubElement(graph, 'input', axis='x')
        time.text = f'{self.abrev}_t'

    def graphs(self, view):
        outputs_without_t = self.outputs.copy()
        outputs_without_t.remove('t')
        for output in outputs_without_t:
            params = {
                'label': output,
                'size': '2',
                'precision': '2'
            }
            graph = SubElement(view, 'graph', params)
            value = SubElement(graph, 'input', axis='y')
            value.text = f'{self.abrev}_{output}'
            time = SubElement(graph, 'input', axis='x')
            time.text = f'{self.abrev}_t'

    def value(self, view): #ToDo
        pass

Accelerometer       = Sensor('accelerometer', 'acc', 0.01, ['t','x','y','z','abs'])
Linear_acceleration = Sensor('linear_acceleration', 'lin_acc', 0.01, ['t','x','y','z','abs'])
Magnetic_field      = Sensor('magnetic_field', 'mag', 0.01, ['t','x','y','z','abs'])
Gyroscope           = Sensor('gyroscope', 'gyr', 0.01, ['t','x','y','z','abs'])
Humidity            = Sensor('humidity', 'wtr', 0.1, ['t','x'])
Light               = Sensor('light', 'lux', 0.01, ['t','x'])
Pressure            = Sensor('pressure', 'pss', 0.01, ['t','x'])
Proximity           = Sensor('proximity', 'prox', 0.1, ['t','x'])
Temperature         = Sensor('temperature', 'temp', 0.1, ['t','x'])
Attitude            = Sensor('attitude', 'att', 0.01, ['t','x','y','z','abs'])
