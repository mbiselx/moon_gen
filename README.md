# Moon Surface Generator

[![Testing](https://github.com/mbiselx/moon_gen/actions/workflows/python-testing.yml/badge.svg)](https://github.com/mbiselx/moon_gen/actions/workflows/python-testing.yml)
[![Formatting](https://github.com/mbiselx/moon_gen/actions/workflows/python-lint_and_format.yml/badge.svg)](https://github.com/mbiselx/moon_gen/actions/workflows/python-lint_and_format.yml) 



The following is a small app allowing one to visualize a surface (such as an elevation model), defined in a python file. 
The purpose is to aid in the development of algorithms to generate nice-looking lunar-like surfaces for lunar rover surface operation simulations. 


## Preview

| ![surface 1](img/Screenshot(1).png) | ![surface 2](img/Screenshot(2).png) | ![surface 3](img/Screenshot(3).png) |
| --- | --- | --- |
| a somewhat older surface, with randomly placed craters | a surface with a fresh crater | a surface with a randomly generated height map |


## Running

After installation, the project can be run as module:
```bash
python -m moon_gen
```


## TODOs

This project is still a work in progress. As such, there are a number of features I would still like to implement. Some are listed below : 
- [ ] better crater and ejecta modelling (more scientifically accurate shapes)
- [ ] better mass wasting (using a dffusion equation, rather than smoothing)
- [ ] use real DEMs for base terrain
- [x] non-crater procedural base terrain
- [ ] generate albedo maps based on crater placement
- [x] export generated surfaces for use in Gazebo
- [ ] export generated surfaces to a standard DEM format, for use in Gazebo