# GreenHEART: Green Hydrogen Energy and Renewable Technologies

[![PyPI version](https://badge.fury.io/py/GreenHEART.svg)](https://badge.fury.io/py/GreenHEART)
![CI Tests](https://github.com/NREL/GreenHEART/actions/workflows/ci.yml/badge.svg)
[![image](https://img.shields.io/pypi/pyversions/GreenHEART.svg)](https://pypi.python.org/pypi/GreenHEART)
[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)

Hybrid project power-to-x component-level system performance and financial modeling for control and
design optimization. GreenHEART currently includes renewable energy, hydrogen, ammonia, and steel.
Other elements such as desalination systems, pipelines, compressors, and storage systems can also be
included as needed.


## Publications where GreenHEART has been used

For more context about GreenHEART and to see analyses that have been performed using the tool, please see some of these publications.
PDFs are available in the linked titles.

Grant, E., et al. "[Hybrid power plant design for low-carbon hydrogen in the United States.](https://iopscience.iop.org/article/10.1088/1742-6596/2767/8/082019/pdf)" Journal of Physics: Conference Series. Vol. 2767. No. 8. IOP Publishing, 2024.

Brunik, K., et al. "[Potential for large-scale deployment of offshore wind-to-hydrogen systems in the United States.](https://iopscience.iop.org/article/10.1088/1742-6596/2767/6/062017/pdf)" Journal of Physics: Conference Series. Vol. 2767. No. 6. IOP Publishing, 2024.

Breunig, Hanna, et al. "[Hydrogen Storage Materials Could Meet Requirements for GW-Scale Seasonal Storage and Green Steel.](https://assets-eu.researchsquare.com/files/rs-4326648/v1_covered_338a5071-b74b-4ecd-9d2a-859e8d988b5c.pdf?c=1716199726)" (2024).

King, J. and Hammond, S. "[Integrated Modeling, TEA, and Reference Design for Renewable Hydrogen to Green Steel and Ammonia - GreenHEART](https://www.hydrogen.energy.gov/docs/hydrogenprogramlibraries/pdfs/review24/sdi001_king_2024_o.pdf?sfvrsn=a800ca84_3)" (2024).

## Software requirements

- Python version 3.9, 3.10, 3.11 64-bit
- Other versions may still work, but have not been extensively tested at this time

## Installing from Package Repositories

1. GreenHEART is available as a PyPi package:

    ```bash
    pip install greenheart
    ```

## Installing from Source

1. Using Git, navigate to a local target directory and clone repository:

    ```bash
    git clone https://github.com/NREL/GreenHEART.git
    ```

2. Navigate to `GreenHEART`

    ```bash
    cd GreenHEART
    ```

3. Create a new virtual environment and change to it. Using Conda and naming it 'greenheart':

    ```bash
    conda create --name greenheart python=3.9 -y
    conda activate greenheart
    ```

4. Install GreenHEART and its dependencies:

    ```bash
    conda install -y -c conda-forge coin-or-cbc=2.10.8 glpk
    pip install electrolyzer@git+https://github.com/jaredthomas68/electrolyzer.git@smoothing
    pip install ProFAST@git+https://github.com/NREL/ProFAST.git
    ```

    Note if you are on Windows, you will have to manually install Cbc: https://github.com/coin-or/Cbc.

    - If you want to just use GreenHEART:

       ```bash
       pip install .  
       ```

    - If you want to work with the examples:

       ```bash
       pip install ".[examples]"
       ```

    - If you also want development dependencies for running tests and building docs:  

       ```bash
       pip install -e ".[develop]"
       ```

    - In one step, all dependencies can be installed as:

      ```bash
      pip install -e ".[all]"
      ```

5. The functions which download resource data require an NREL API key. Obtain a key from:

    [https://developer.nrel.gov/signup/](https://developer.nrel.gov/signup/)

6. To set up the `NREL_API_KEY` and `NREL_API_EMAIL` required for resource downloads, you can create
   Environment Variables called `NREL_API_KEY` and `NREL_API_EMAIL`. Otherwise, you can keep the key
   in a new file called ".env" in the root directory of this project.

    Create a file ".env" that contains the single line:

    ```bash
    NREL_API_KEY=key
    NREL_API_EMAIL=your.name@email.com
    ```

7. Verify setup by running tests:

    ```bash
    pytest
    ```


2. To set up `NREL_API_KEY` for resource downloads, first refer to section 7 and 8 above. But for
   the `.env` file method, the file should go in the working directory of your Python project, e.g.
   directory from where you run `python`.

## Parallel processing for GreenHEART finite differences and design of experiments

GreenHEART is set up to run in parallel using MPI and PETSc for finite differencing and for design of
experiments runs through OpenMDAO. To use this capability you will need to follow the addtional installation
instruction below:

```bash
conda install -c conda-forge mpi4py petsc4py
```

For more details on implementation and installation, reference the documentation for OpenMDAO.

To to check that your installation is working, do the following:

```bash
cd tests/greenheart/
mpirun -n 2 pytest test_openmdao_mpi.py
```

## Getting Started

The [Examples](./examples/) contain Jupyter notebooks and sample YAML files for common usage
scenarios in GreenHEART. These are actively maintained and updated to demonstrate GreenHEART's
capabilities. For full details on simulation options and other features, documentation is
forthcoming.

## Contributing

Interested in improving GreenHEART? Please see the [Contributing](./CONTRIBUTING.md) section for more information.
