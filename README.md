# Pyphox
Simple python wrapper for the Phyphox Remote-interface Communication API
(https://phyphox.org/wiki/index.php/Remote-interface_communication)

# Setup

Clone/download the repository to your project folder.

## Linux
```
cd /PATH/TO/YOUR/PROJECT
git clone git@github.com:alom101/pyphox.git
```

# Usage

*With Phyphox on remote access mode*

```
import phyphox

exp = phyphox.Experiment('PHONE_IP_HERE','PHONE_PORT_HERE')
```

## Experiment data available
```
exp.crc32
exp.title
exp.localTitle
exp.category
exp.localCategory
exp.bufferNames
```
Read more on https://phyphox.org/wiki/index.php/Remote-interface_communication#.2Fconfig

## Controlling your experiment
```
exp.start()
exp.stop()
exp.clear()
```
Read more on https://phyphox.org/wiki/index.php/Remote-interface_communication#.2Fcontrol

## Retrieving data
*Warning:* exp.get will be changed to a more user friendly method in the future

### All data
```
data = exp.get()
```

### Only from some buffers
```
buffer_list = ['abc', 'efg']
data = exp.get(buffer_list)
```

### Only after some threshold
```
data = exp.get(threshold='2|time_buffer') #Retrieves all buffers after t=2
```
Read more on https://phyphox.org/wiki/index.php/Remote-interface_communication#.2Fget

# ToDo
- Handle exceptions
- Handle entire url on Experiment.__init__
- Enable installation via pip
