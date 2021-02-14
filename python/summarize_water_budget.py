import xarray as xr
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import plot_and_table_functions as ptf
from matplotlib.backends.backend_pdf import PdfPages
from Figures import ReportFigures
from scipy.interpolate import InterpolatedUnivariateSpline
import glob

# 31.9, 34.3 = min, max precipitation values for central sands for 1981-2010
# mean min temp (C) = 0.8 to 2  (33.4 to 35.6 F)
# mean max temp (C) = 12.07 to 13.68 (53.7 to 56.6 F)

if len(sys.argv) >= 1:
    output_path = sys.argv[1]
else:
    output_path='.'

rf = ReportFigures()
rf.set_style()

# functions to convert between feet and meters
def meters_to_feet(x):
    return (x*3.28084)
def feet_to_meters(x):
    return (x*0.3048)

# functions to convert between cubic meter per day and cubic feet per second
def cu_meters_day_to_cfs(x):
    return (x*0.000408734569)
def cfs_to_cu_meters_day(x):
    return (x*2446.58)

# functions to convert between inches and millimeters
def inches_to_mm(x):
    return (x * 25.4)
def mm_to_inches(x):
    return (x / 25.4)    

# functions to convert between Fahrenheit and Celsius 
def F_to_C(x):
    return((x-32.) * 5. / 9.)
def C_to_F(x):
    return(x*9./5. + 32.)

class swb_var:

    def __init__(self, filename, variable_name):
        self.filename = filename
        self.variable_name = variable_name
        self.variable_title = variable_name.replace('_',' ').title().replace('Et','ET')
        self.variable_name = self.variable_name.replace('MODIS_','')
        self.units = 'inches'
        self.units2 = 'millimeters'
        self.func_eng_to_metric = inches_to_mm
        self.func_metric_to_eng = mm_to_inches

    def open(self):
        self.ds = xr.open_dataset(self.filename, chunks=800 )
        self.min_time = self.ds.time.min().values
        self.max_time = self.ds.time.max().values

    def set_min_time(self, str):
        self.min_time = np.datetime64(str)

    def set_max_time(self, str):
        self.max_time = np.datetime64(str)

    def calc_monthly_mean_grids(self):
        ds = self.ds.get(self.variable_name)
        self.monthly_mean_grids = ds.sel(time=slice(self.min_time,self.max_time)).resample(time="1MS", restore_coord_dims=True).mean(dim='time')

    def calc_annual_mean_grids(self):
        ds = self.ds.get(self.variable_name)
        self.annual_mean_grids = ds.sel(time=slice(self.min_time,self.max_time)).resample(time="A", restore_coord_dims=True).mean(dim='time')

    def calc_monthly_sum_grids(self):
        ds = self.ds.get(self.variable_name)
        self.monthly_sum_grids = ds.sel(time=slice(self.min_time,self.max_time)).resample(time="1MS", restore_coord_dims=True).sum(dim='time')

    def calc_annual_sum_grids(self):
        ds = self.ds.get(self.variable_name)
        self.annual_sum_grids = ds.sel(time=slice(self.min_time,self.max_time)).resample(time="A", restore_coord_dims=True).sum(dim='time')

    def calc_annual_sum_means(self):
        ds = self.ds.get(self.variable_name)
        self.annual_sum_means = ds.sel(time=slice(self.min_time,self.max_time)).resample(time="A", restore_coord_dims=True).sum(dim='time').mean(dim=('x','y'))

    def calc_annual_mean_means(self):
        ds = self.ds.get(self.variable_name)
        self.annual_mean_means = ds.sel(time=slice(self.min_time,self.max_time)).resample(time="A", restore_coord_dims=True).mean(dim='time').mean(dim=('x','y'))

#        output_filename = self.variable_name + '__annual_means_plot.pdf'
#        with PdfPages(output_filename) as pdf:
#            self.annual_means.plot()
#            pdf.savefig()  # saves the current figure into a pdf page
#            plt.close()


    def calc_monthly_sum_means(self):
        ds = self.ds.get(self.variable_name)
        self.monthly_sum_means = ds.sel(time=slice(self.min_time,self.max_time)).resample(time="1MS", restore_coord_dims=True).sum(dim='time').mean(dim=('x','y'))

def make_annual_barchart(labels, values, xlab='', ylab=''):
#    labels =  swb_varname.annual_sum_means.time.dt.strftime("%Y")
#    x = np.arange(swb_varname.annual_sum_means.size)
#    height = swb_varname.annual_sum_means.values
    fig, ax = plt.subplots(figsize=rf.singlecolumn_size)
    ax.bar(labels, values, color='blue')
    ax.set_xlabel(xlab)
    ax.set_ylabel(ylab)

def make_linechart(labels, values, figsize=rf.singlecolumn_size, xlab='', ylab='', ylab2='',
    func1=mm_to_inches, func2=inches_to_mm):
    fig, ax = plt.subplots(figsize=figsize)
    ax.plot(labels, values, color='blue')
    ax.set_xlabel(xlab)
    ax.set_ylabel(ylab)
    secaxy = ax.secondary_yaxis('right', functions=(func1, func2))
    secaxy.set_ylabel(ylab2)        
    secaxy.yaxis.set_major_formatter(mpl.ticker.StrMethodFormatter('{x:,.1f}'))
    ax.yaxis.set_major_formatter(mpl.ticker.StrMethodFormatter('{x:,.0f}'))
    plt.tight_layout()

def make_linechart_w_normals(labels, values, norm1, norm2, figsize=rf.singlecolumn_size, xlab='', ylab='', ylab2='',
    func1=mm_to_inches, func2=inches_to_mm):
    fig, ax = plt.subplots(figsize=figsize)
    ax.fill_between(labels, norm1, norm2, color='gray')
    ax.plot(labels, values, color='blue')
    ax.set_xlabel(xlab)
    ax.set_ylabel(ylab)
    secaxy = ax.secondary_yaxis('right', functions=(func1, func2))
    secaxy.set_ylabel(ylab2)        
    secaxy.yaxis.set_major_formatter(mpl.ticker.StrMethodFormatter('{x:,.1f}'))
    ax.yaxis.set_major_formatter(mpl.ticker.StrMethodFormatter('{x:,.0f}'))
    plt.tight_layout()

swb = {}

swb_varlist = ['rejected_net_infiltration','net_infiltration', 'gross_precipitation','actual_et','reference_ET0',
            'MODIS_actual_et','irrigation','runoff_outside','runoff','tmin','tmax','crop_et','bare_soil_evaporation']

# make dictionary of all SWB outputs that can be found
for root, directories, files in os.walk(output_path, topdown=False):
    for file in files:
        for var in swb_varlist:
            if var in file and file.endswith('.nc'):
                if var == 'net_infiltration' and 'rejected_net_infiltration' in file:
                    pass
                elif var == 'runoff' and 'runoff_outside' in file:
                    pass
                elif var == 'actual_et' and 'MODIS' in file:
                    pass
                else:
                    swb[var] = swb_var(os.path.join(root,file), var)

# overrides for units of temperature
swb['tmin'].units = 'degrees F'
swb['tmax'].units = 'degrees F'
swb['tmin'].units2 = 'degrees C'
swb['tmax'].units2 = 'degrees C'
swb['tmin'].func_eng_to_metric = F_to_C
swb['tmax'].func_eng_to_metric = F_to_C
swb['tmin'].func_metric_to_eng = C_to_F
swb['tmax'].func_metric_to_eng = C_to_F

#for key, value in swb.items():
for key in swb_varlist:
    print(key)
    value = swb.get(key)
    value.open()
    value.set_min_time('2012-01-01')
    value.set_max_time('2018-12-31')

    if key not in ['tmax','tmin']:
        value.calc_annual_sum_means()
        output_filename = swb[key].variable_name + '__annual_sum_means_plot.pdf'
        with PdfPages(output_filename) as pdf:
            labels =  swb[key].annual_sum_means.time.dt.strftime("%Y")
            values = swb[key].annual_sum_means.values * 25.4
            make_linechart(labels, values, ylab=swb[key].variable_title + ' in ' + swb[key].units2,
                                        ylab2=swb[key].variable_title + ' in ' + swb[key].units,
                                        func1=swb[key].func_metric_to_eng, func2=swb[key].func_eng_to_metric)
            pdf.savefig()  # saves the current figure into a pdf page
        plt.close()
    else:
        value.calc_annual_mean_means()
        output_filename = swb[key].variable_name + '__annual_mean_means_plot.pdf'
        with PdfPages(output_filename) as pdf:
            labels =  swb[key].annual_mean_means.time.dt.strftime("%Y")
            values = swb[key].annual_mean_means.values
            make_linechart(labels, values, ylab=swb[key].variable_title + ' in ' + swb[key].units2,
                                        ylab2=swb[key].variable_title + ' in ' + swb[key].units,
                                        func1=swb[key].func_metric_to_eng, func2=swb[key].func_eng_to_metric)
            pdf.savefig()  # saves the current figure into a pdf page
        plt.close()

    
ylab = 'Water budget component, in inches'
xlab = ''

xnew = np.linspace(0, 11, num=12)
xnew2 = np.linspace(0, 11)
ynew2 = np.zeros(len(xnew2))

output_filename = 'monthly_water_budget_components_plot.pdf'
with PdfPages(output_filename) as pdf:

    for year in range(2010,2020):

        fig, ax = plt.subplots(figsize=rf.doublecolumn_size)
        fig.suptitle('Water budget components for ' + str(year))

        actual_et=swb['actual_et']
        actual_et.set_min_time(str(year)+'-01-01')
        actual_et.set_max_time(str(year)+'-12-31')
        labels = actual_et.monthly_sum_means.sel(time=slice(actual_et.min_time,actual_et.max_time)).time.dt.strftime("%b")
        values = actual_et.monthly_sum_means.sel(time=slice(actual_et.min_time,actual_et.max_time)).values
        ax.plot(labels, values, color='green', label='SWB actual et')

        rainfall = swb['rainfall']
        rainfall.set_min_time(str(year)+'-01-01')
        rainfall.set_max_time(str(year)+'-12-31')
        labels = rainfall.monthly_sum_means.sel(time=slice(rainfall.min_time,rainfall.max_time)).time.dt.strftime("%b")
        values = rainfall.monthly_sum_means.sel(time=slice(rainfall.min_time,rainfall.max_time)).values
        spl = InterpolatedUnivariateSpline(xnew, values,k=2)
        ax.plot(labels, values, color='blue', marker='.', linestyle='none', label='rainfall')
        ax.plot(xnew2, np.maximum(spl(xnew2),0.0),linestyle='-',color='blue', label='rainfall')

        reference_ET0 = swb['reference_ET0']
        reference_ET0.set_min_time(str(year)+'-01-01')
        reference_ET0.set_max_time(str(year)+'-12-31')
        labels = reference_ET0.monthly_sum_means.sel(time=slice(reference_ET0.min_time,reference_ET0.max_time)).time.dt.strftime("%b")
        values = reference_ET0.monthly_sum_means.sel(time=slice(reference_ET0.min_time,reference_ET0.max_time)).values
        spl = InterpolatedUnivariateSpline(xnew, values,k=2)
        ax.plot(labels, values, color='purple', marker='.', linestyle='none', label='reference ET0')
        ax.plot(xnew2, np.maximum(spl(xnew2),0.0),linestyle='-',color='purple', label='reference ET0')

        snowmelt = swb['snowmelt']
        snowmelt.set_min_time(str(year)+'-01-01')
        snowmelt.set_max_time(str(year)+'-12-31')
        labels = snowmelt.monthly_sum_means.sel(time=slice(snowmelt.min_time,snowmelt.max_time)).time.dt.strftime("%b")
        values = snowmelt.monthly_sum_means.sel(time=slice(snowmelt.min_time,snowmelt.max_time)).values
        spl = InterpolatedUnivariateSpline(xnew, values,k=2)
        ax.plot(labels, values, color='cyan', label='snowmelt', marker='.', linestyle='none')
        ax.plot(xnew2, np.maximum(spl(xnew2),0.),linestyle='-',color='cyan', label='snowmelt')

        irrigation = swb['irrigation']
        irrigation.set_min_time(str(year)+'-01-01')
        irrigation.set_max_time(str(year)+'-12-31')
        labels = irrigation.monthly_sum_means.sel(time=slice(irrigation.min_time,irrigation.max_time)).time.dt.strftime("%b")
        values = irrigation.monthly_sum_means.sel(time=slice(irrigation.min_time,irrigation.max_time)).values
        spl = InterpolatedUnivariateSpline(xnew, values,k=2)
        ax.plot(labels, values, color='orange', label='irrigation', marker='.', linestyle='none')
        ax.plot(xnew2, np.maximum(spl(xnew2),0.),linestyle='-',color='orange', label='irrigation')

        ax.legend()
        pdf.savefig()  # saves the current figure into a pdf page

plt.close()
