# Extracting and summarizing SWB2 output

SWB2 was designed to output all components of the daily water budget in the form of netCDF files. There are many tools and language hooks available that make it relatively easy to work with the netCDF output files. This repo contains an informal collection of examples that demonstrate some ways to extract and summarize SWB2 output.

# Processing methods

## SWB2

The SWB2 code has the ability to dump all state variables and some relevant temporary or internal variables to a comma-spaced variable (csv) file; this output corresponds to a single cell within the model domain and is not filtered or averaged in any way. This output may be obtained by adding a statement similar to the following to the SWB control file:
```
# EVERGREEN FOREST
#                          x-coord y-coord
DUMP_VARIABLES COORDINATES 557220. 451551.
```
If you know the row and column numbers of the cell of interest, you may extract the data by adding a statement similar to this to your control file:
```

# EVERGREEN FOREST
#              row num    col num
DUMP_VARIABLES 128        234
```

## SWBSTATS2

The `swbstats2` code is aimed at quickly summarizing and extracting values from `swb2` netCDF output files. Basic `swbstats2` operations are discussed [here](swbstats/basic_swbstats2_operation.md).

## Python

Python with the package 'xarray' and 'xarray-spatial' can be used to quickly summarize swb output over various time and spatial scales. 'xarray' allows for straightforward calculation of statistics over one or more dimensions. 'xarray-spatial' adds the ability to perform zonal statistics on the netCDF output. A short example is given [here](jupyter/basic_munging_with_xarray.ipynb).

