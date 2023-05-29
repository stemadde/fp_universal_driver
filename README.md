# FP Universal Driver (Not published)
A driver to send commands to any Fiscal Printer produced under the Italian regulations (RT).

The driver exposes a limited list of functionalities:
- Command to perform the daily closing operation
- Command to perform the daily read operation
- Commands to read/write the ivas table
- Commands to read/write the payments table
- Commands to read/write the categories table
- Commands to read/write the plus table
- Commands to read/write the headers table


## Installation (Not published yet)

```
pip install fp_universal_driver
```


# Guide for contributors

## How to integrate a new fiscal printer
Inside the `fp_universal_driver\src` are located all the drivers that handle translation for fiscal printers.
If you would like to start the integration of a new Fiscal Printer brand create a sub package with the following name sintax:

`fp_universal_driver.src.Prod<brand_logotype>`

Follow the example provided in the src folder. Do not use copywrited protected names in your code.

Inside each sub package you need to define a file structure as it follows:
    
    
    fp_universal_driver
    ├── src
    │   ├── Prod<brand_logotype>
    │   │   ├── __init__.py
    │   │   ├── category.py
    │   │   ├── command.py
    │   │   ├── fp.py
    │   │   ├── header.py
    │   │   ├── iva.py
    │   │   ├── payment.py
    │   │   ├── plu.py

Inside each one of the files a corresponding class need to be defined, inheriting from the base class defined in the `fp_universal_driver.src` package.

Classed should implement their own logic as to what validations to perform, how to handle types, etc... Methods that begins with `def __validate` are automatically called upon instanciation.

Finally, but most importantly, each subclass should define the methods `from_fp` and `to_fp`.
- `from_fp` should handle the translation process given a base FP instance. It should be able to convert the base FP class into an instance of the caller class.
- `to_fp` should handle the translation process given an instance of the caller class. It should be able to convert the caller class into an instance of the base FP class.

The end goal is that each driver should be able to comunicate bidirectionally with the base FP class.

## How to test a new fiscal printer
Test are splitted into two categories:
- **Unit tests**: For each fiscal printer create a sub module containing the unit tests for the function
- **Functional tests**: For each fiscal printer create a .py file containing the logic to perform a test of the general functionality of the procedures, like converting from and to the base FP class.

