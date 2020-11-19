# ModOrganizer2 - Python debug plugin

This is a small plugin built upon [`pyqtconsole`](https://github.com/marcus-oscarsson/pyqtconsole) that
offers a Python interpreter within MO2.

## Installation

To install, go to the [releases](https://github.com/Holt59/modorganizer-python_debug/releases) page and
download the latest release (`python_debug-x.y.z.zip`).
Extract the archive in your MO2 `plugins/` folder (you should get a `plugins/python_debug` folder).

## Usage

To start the interpreter, press F12 or use the Tools menu. Within the interpreter, you have access to
the following immediately:

```
mobase  # The mobase module
organizer  # The global IOrganizer instance
```

## License

MIT License

Copyright (c) 2020 Mikaël Capelle

See [LICENSE](LICENSE) for more information.
