# ptop

An awesome task manager written in python. A more awesome top like thing in your terminal !


![ptop-image](https://github.com/darxtrix/ptop/blob/master/docs/ptop_demo.gif)


> Inspired by [vtop](https://github.com/MrRio/vtop)


## Some Screenshots

<img src="https://github.com/darxtrix/ptop/blob/master/docs/ptop_01.png" alt="ptop usage 01"/>
<img src="https://github.com/darxtrix/ptop/blob/master/docs/ptop_02.png" alt="ptop usage 02" />


## Installation

`ptop` is compaible with both Python2.x and Python3.x and is tested on Linux and MaxOSx (should be invoked as root) environments.

```bash
$ pip install ptop
```

or

```bash
$  git clone https://github.com/darxtrix/ptop
$ cd ptop/
$ pip install -r requirements.txt # install requirements
$ sudo python setup.py install
```


## Upgrading ptop

The latest version is 1.0. Older versions of `ptop` can be updated using:
```bash
$ pip install --upgrade ptop
```

Checkout this blog post for more on the latest developments https://medium.com/@darxtrix/releasing-ptop-1-0-a-task-manager-written-using-python-879f63745034


## Usage

```bash
$ ptop

$ ptop -t <theme>   # custom theme

$ ptop -csrt 500    # custom refresh time for cpu stats 

$ ptop -h           # help
```

## Features

- Killing a process :heavy_check_mark:
- Showing system ports and files used by a process :heavy_check_mark:
- Network Monitor :heavy_check_mark:
- Process search :heavy_check_mark:
- Sorting on the basis of process lifetime and memory used :heavy_check_mark:
- Responsiveness with terminal :heavy_check_mark:
- Custom refresh times for different stats like memory info, process info etc :heavy_check_mark:
- Rolling version updates :heavy_check_mark:

For suggesting new features please add to this [issue](https://github.com/darxtrix/ptop/issues/29)


## Supported themes

- `colorful`     
- `elegant`    
- `simple`    
- `dark`   
- `light` 


## Developing ptop

```bash
$ git clone https://github.com/darxtrix/ptop
$ cd ptop   
$ pip install -r requirements.txt
$ python setup.py develop
```
**Note :** ptop will create a log file called `.ptop.log` in the home directory of the user.


## Contributions Guide

- Pull requests are awesome and always welcome. Please use the [issue tracker](https://github.com/darxtrix/ptop/issues) to report any bugs.
- For starters, we have filtered some [newbie issues](https://github.com/darxtrix/ptop/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22).
- Feel free to shoot your queries at the ptop [gitter](https://gitter.im/ptop_task_manager/Lobby) channel.


## Main modules :

- `ptop.core` : Defines a basic `Plugin` class that other plugins in the `ptop.plugins` inherit.
- `ptop.interfaces` : The interface to the ptop built using npyscreen.
- `ptop.plugins` : This module contains all the plugin sensors supported i.e `Disk Sensor`,`Memory Sensor`,`Process Sensor`, etc. ( Any new plugin should be added here).
- `ptop.statistics` : Generate continuous statistics using background thread jobs by locating plugins in the plugins directory.
- `ptop.utils` : Custom thread classes.


## Main Dependencies

- [npyscreen](https://pypi.python.org/pypi/npyscreen)
- [psutil](https://pypi.python.org/pypi/psutil)
- [drawille](https://github.com/asciimoo/drawille)

## Contributors 

* **[vinusankars](https://github.com/vinusankars)**
* **[Deepak Narayanan](https://github.com/deeps-nars)**
* **[Smeet Vora](https://github.com/smeet20)**
* **[Santiago Castro](https://github.com/bryant1410)**
* **[Yu-Jie Lin](https://github.com/livibetter)**

For details please check [Contributors.md](https://github.com/darxtrix/ptop/blob/master/CONTRIBUTORS.md)

## License 

MIT © [Ankush Sharma](http://github.com/darxtrix)
