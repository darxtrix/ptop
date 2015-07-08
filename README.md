#ptop

An awesome task manager written in python. A more awesome top like thing in your terminal !


![ptop-image](https://github.com/black-perl/ptop/blob/master/docs/ptop.gif)


##Installing

```bash
$ pip install ptop
```
**Note:** Python 2.X supported yet, no support for python3.

##Usage

```
$ ptop -t <theme>
```


## Supported themes

- `colorful`
- `elegant`
- `simple`
- `dark`
- `light` etc.

## Changelog

- version 0.0.6 fixes index errors.[Issue4](https://github.com/black-perl/ptop/issues/4)
- A default theme option has been set.[Issue5](https://github.com/black-perl/ptop/issues/5)
- Though there are some [known issues](https://github.com/black-perl/ptop#known-issues) still left. :cold_sweat:


## Some Screenshots

![ptop-1](https://github.com/black-perl/ptop/blob/master/docs/ptop1.png)

![ptop-2](https://github.com/black-perl/ptop/blob/master/docs/ptop.png)

![ptop-3](https://github.com/black-perl/ptop/blob/master/docs/ptop2.png)


##Help

```bash
$ ptop -h
```


## Known Issues

- Sometimes garbage text appears on the screen, press `Ctrl` + `L` to **clear**. (Anybody having idea about this ?)
- Though ptop is responsive across various terminal sizes as positioning is done according to terminal sizes, but sometimes things may break. If so, then try in a terminal of bigger size.


## Development

### Installing
```bash
$ git clone https://github.com/black-perl/ptop
$ python setup.py develop
```

### Running

```bash
$ cd ptop/
$ python main.py
```

**Note :** ptop will create a log file called `.ptop.log` in the home directory of the user.


## Main modules :
- `ptop.core` : Defines a basic `Plugin` class that other plugins in the `ptop.plugins` in inherit.
- `ptop.interfaces` : The interface to the ptop built using npyscreen.
- `ptop.plugins` : This module contains all the plugin sensors supported i.e `Disk Sensor`,`Memory Sensor`,`Process Sensor`, etc. ( Any new plugin should be added here).
- `ptop.statistics` : Generate continuous statistics using background thread jobs by location plugins in the plugins directory.
- `ptop.utils` : Custom thread classes.


## Main Dependencies
- [npyscreen](https://pypi.python.org/pypi/npyscreen)
- [psutil](https://pypi.python.org/pypi/psutil)
- [drawille](https://github.com/asciimoo/drawille)


## Contributions

Pull requests are awesome and always welcome. Please use the **issue tracker** to report any bugs or file feature requests.


## License

MIT (C) [Ankush Sharma](http://github.com/black-perl)
