# Introduction to swbstats2

`swbstats2` is designed as a simple command-line driven utility to quickly extract and summarize output from a swb2 netCDF output file. There are more elegant ways of doing this by means of R or Python scripts, for example, but `swbstats2` can perform well without any scripting.

## Basic output

The simplest use of `swbstats2` is to calculate the mean and sum of the variable values within a grid over all timesteps for which data exist:

`swbstats2 ../data/gross_precipitation__2012-01-01_to_2013-12-31__173_by_200.nc`

This causes `swbstats2` to produce both summaries of the *MEAN* and *SUM* of the daily values for the variable. The outputs are:

`gross_precipitation___MEAN_2012-01-01_to_2013-12-31__173_by_200.nc`

`gross_precipitation___SUM_2012-01-01_to_2013-12-31__173_by_200.nc
`
Since the output file covers two calendar years, the output file containing sum of all daily values is a bit hard to interpret, since we commonly report water budget components for monthly or annual date ranges rather than a date range encompassing two complete years.

## Period output

`swbstats2` can produce output for time ranges that may make more sense to us, say annual, monthly, or quarterly, by specifying the appropriate interval by means of command-line switches:
```
--annual_statistics
    calculate statistics for every calendar year between start and end
--monthly_statistics
    calculate statistics for every month between start and end
--daily_statistics
    calculate statistics for every day between start and end
--slice=yyyy-mm-dd,yyyy-mm-dd
    dates over which statistics should be calculated,
    with start date and end date formatted as yyyy-mm-dd,yyyy-mm-dd
```

So to obtain a set of monthly grids (packed into a single netCDF output file), we could run `swbstats2` as follows:

`swbstats2 --monthly_statistics ../data/gross_precipitation__2012-01-01_to_2013-12-31__173_by_200.nc`

The output from `swbstats2` will be two netCDF files, one containing monthly summed values calculated from daily values, and one containing monthly mean values calculated from the daily values:

`gross_precipitation__MONTHLY_MEAN_2012-01-01_to_2013-12-31__173_by_200.nc`

`gross_precipitation__MONTHLY_SUM_2012-01-01_to_2013-12-31__173_by_200.nc`

Note that the output represents summarized values for each month within the date range covered by the output, 24 in this case; in other words, the first set of statistics are calculated for the period 2012-01-01 through 2012-01-31, the second set of statistics cover the period 2012-02-01 through 2012-02-29, etc. The embedded date values in a monthly output file represent approximately the 15th of each month.

To obtain output for any arbitrary period, the `--slice` option may be used. For example, to summarize precipitation over the summertime (June, July, August in the Northern Hemisphere), `swbstats2` can be run as follows:

`swbstats2 --slice=2012-06-01,2012-08-31 ../data/gross_precipitation__2012-01-01_to_2013-12-31__173_by_200.nc`,

which produces the following output files:

`gross_precipitation__SLICE_STATS--2012-06-01_to_2012-08-31_MEAN_2012-01-01_to_2012-08-31__173_by_200.nc`
`gross_precipitation__SLICE_STATS--2012-06-01_to_2012-08-31_SUM_2012-01-01_to_2012-08-31__173_by_200.nc`

The filename is a bit misleading, in that the first date range refers to the actual range used in the calculation, while the second date range refers to the starting date of the input data file and the end date for all calculations.

## Arc ASCII Grid output

Often one just wants a simple ASCII representation of the SWB-calculated values. SWBSTATS2 can be instructed to output or suppress gridded outut with the following options:

`[ --{no_}netcdf_output ]
    toggle whether netCDF file is target for gridded output`

`[ --{no_}arcgrid_output ]
    toggle whether an ASCII Arc Grid is target for gridded output`

So to produce a series of Arc ASCII monthly grids, one could use the following syntax:

`swbstats2 --monthly_statistics --no_netcdf_output --arcgrid_output ../data/gross_precipitation__2012-01-01_to_2013-12-31__173_by_200.nc`

The result will be a set of 48 Arc ASCII files covering the desired months:


    gross_precipitation__2012-01-01_to_2012-01-31__200_by_173__MEAN__inches.asc
    gross_precipitation__2012-01-01_to_2012-01-31__200_by_173__SUM__inches.asc

                ...

    gross_precipitation__2013-12-01_to_2013-12-31__200_by_173__MEAN__inches.asc
    gross_precipitation__2013-12-01_to_2013-12-31__200_by_173__SUM__inches.asc

## Zonal statistics

`swbstats2` can calculate zonal statistics for any integer-valued grid supplied (as an Arc ASCII grid) that covers the same model extent and whose projection is the same as that of the base grid. For example, to summarize values for the entire simulation period by the hydrologic soil group of the cells, `swbstats2` can be run as follows:

```
swbstats2 --zone_grid=../data/Hydrologic_soil_groups__as_read_into_SWB.asc ../data/gross_precipitation__2012-01-01_to_2013-12-31__173_by_200.nc
```

The resulting output file is called `zonal_stats__gross_precipitation.csv`; the contents look like this:

```
start_date,end_date,zone_id,minimum_swb,maximum_swb,mean_swb,sum_swb,count_swb
2012-01-01,2013-12-31, 3,  61.299212634563 ,  68.07086612284184 ,  63.63703154502019 ,  130583.1887303814  ,2052
2012-01-01,2013-12-31, 6,  61.299212720245 ,  67.04724368080497 ,  63.58179933940418 ,  59894.05497771874  ,942
2012-01-01,2013-12-31, 2,  61.062992151826 ,  69.37007859721780 ,  65.08027240993962 ,  1083456.375080675  ,16648
```

The `zone_id` is listed in the third column of the output file; in this case the zone_id value in the first row corresponds to hydrologic soil group 3, which in this case means that the summary is valid for the cells that belong to soil hydrologic group 'C'.
