# Installation

## Local paths setup

Create system.json file in the root of this directory with your machine's file paths using `system.template.json` as a template.
`system.json` should include the following:
* Path for creating logs for one-off scripts (`'output'`)
* Path to the folder with (generated) datasets of sewing patterns (`'datasets_path'`)
* Path to the folder with simulation results on the datasets of sewing patterns (`'datasets_sim'`)

* Data generation & Simulation resources
    * path to folder with simulation\rendering configurations (`'sim_configs_path'`)
    * path to folder containing body files for neutral body and other base body models (`'bodies_default_path'`)
    * path to folder containing datasets of body shape samples (`'body_samples_path'`)
<<<<<<< HEAD


## Installing simulator

We use our own version of the [NVIDIA warp](https://github.com/maria-korosteleva/NvidiaWarp-GarmentCode) simulator. It should be installed manually to use our library correctly.

See the instructions in the [NvidiaWarp-GarmentCode](https://github.com/maria-korosteleva/NvidiaWarp-GarmentCode) repo.

## Using pip

With pip, you can install the core pygarment library and its dependencies to start writing your own garment programs!

```
pip install pygarment
```

## Manual Installation

If required, you could install the library and dependecies manually

### Install python with dependencies:

* Python 3.9
* numpy<2
* scipy
* pyyaml >= 6.0
* [svgwrite](https://pypi.org/project/svgwrite/)
* psutil
* matplotlib
* [svgpathtools](https://github.com/mathandy/svgpathtools)
* [cairoSVG](https://cairosvg.org/)
    NOTE: this lib has some quirks on Windows, which we resolve with including needed dlls in `./pygarment/pattern/cairo_dlls` and adding the ditrectory to PATH in runtime
* [NiceGUI](https://nicegui.io/#installation)
* [trimesh](https://trimesh.org/)
* [libigl](https://libigl.github.io/libigl-python-bindings/)
* [pyrender](https://pyrender.readthedocs.io/en/latest/index.html)
* [CGAL](https://pypi.org/project/cgal/)
=======
>>>>>>> f20c6f13d9ecc069292c6e8158d8049e235ff0e7

All python dependencies can be installed with `pip install` / `conda install`:

```
conda create -n garmentcode python=3.9
conda activate garmentcode
pip install pygarment
<build and install warp for GarmentCode>
```

#### Create .env as mentioned in .env.example file

#### Configure system.json values with reference to system.template.json

<<<<<<< HEAD
> NOTE: check out a full environment setup and running process from our early adopter: https://github.com/Sayvai-io/yoko/GarmentCode/issues/17
=======
#### For Database Backup, Setup using [Docker](./Dockerization.md) (Optional)

## Warp simulator

We use our own version of the [NVIDIA warp](https://github.com/maria-korosteleva/NvidiaWarp-GarmentCode) simulator. It should be installed manually to use our library correctly.

 Visit [NvidiaWarp-GarmentCode](https://github.com/maria-korosteleva/NvidiaWarp-GarmentCode), For more details.

## Installing warp simulator

To use this version of NVIDIA Warp, please, follow the steps for manual installation below. The following tools are required:

* Microsoft Visual Studio 2019 upwards (Windows)
* GCC 7.2 upwards (Linux)
* CUDA Toolkit 11.5 or higher [Download page](https://developer.nvidia.com/cuda-downloads)
* [Git LFS](https://git-lfs.github.com/) installed

Clone the repository now [NvidiaWarp-GarmentCode](https://github.com/maria-korosteleva/NvidiaWarp-GarmentCode)

    git clone https://github.com/maria-korosteleva/NvidiaWarp-GarmentCode

After cloning the repository, users should run:

    python build_lib.py

This will generate the `warp.dll` / `warp.so` core library respectively. When building manually users should ensure that their `CUDA_PATH` environment variable is set, otherwise Warp will be built without CUDA support. Alternatively, the path to the CUDA toolkit can be passed to the build command as `--cuda_path="..."`. After building, the Warp package should be installed using:

    pip install -e .

This ensures that subsequent modifications to the library will be reflected in the Python package.

If you are cloning from Windows, please first ensure that you have enabled "Developer Mode" in Windows settings and symlinks in git:

    git config --global core.symlinks true

This will ensure symlinks inside ``exts/omni.warp.core`` work upon cloning.
>>>>>>> f20c6f13d9ecc069292c6e8158d8049e235ff0e7
