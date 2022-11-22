# -*- coding: utf-8 -*-
"""
Created on Fri Apr 22 10:44:27 2022

@author: ereznic2
"""

import fnmatch
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sqlite3

import glob
import csv
import sys
import heapq


# Directory from which to pull outputs from
#year = '2022'
dir0 = 'Examples/H2_Analysis/RODeO_files/Output_test/' 
dirfinancial = 'Examples/H2_Analysis/financial_summary_results/'
dircambium = 'Examples/H2_Analysis/Cambium_data/StdScen21_MidCase95by2035_hourly_' 
dir_plot = 'Examples/H2_Analysis/RODeO_files/Plots/LCA_Plots/'

# Specify grid price scenario if interest for down-selection in case multiple grid scenarios
# exist within the output folder
grid_price_scenario = 'retail-peaks'

c0 = [0,0,0]

files2load_results={}
files2load_results_title={}
files2load_results_categories={}


for files2load in os.listdir(dir0):
    if fnmatch.fnmatch(files2load, 'Storage_dispatch_results*'):
        c0[0]=c0[0]+1
        files2load_results[c0[0]] = files2load
        int1 = files2load.split("_")
        int1 = int1[3:]
        int1[-1] = int1[-1].replace('.csv', '')
        files2load_results_title[c0[0]] = int1
    files2load_title_header = ['Year','Site','Turbine Size','Electrolysis case','Policy Option','Grid Case']
    
    
# SMR emissions
g_to_kg_conv = 0.001
smr_NG_combust = 56.2 # Natural gas combustion (g CO2e/MJ)
smr_NG_consume = 167  # Natural gas consumption (MJ/kg H2)
smr_PO_consume = 0    # Power consumption in SMR plant (kWh/kg H2)
smr_steam_prod = 17.4 # Steam production on SMR site (MJ/kg H2)
smr_HEX_eff    = 0.9  # Heat exchanger efficiency (-)
smr_NG_supply  = 9    # Natural gas extraction and supply to SMR plant assuming 2% CH4 leakage rate (g CO2e/MJ)


    
# Loop through all scenarios in output folder
for i0 in range(len(files2load_results)):
    #i0 = 0
    # Read in applicable Cambium file
    filecase = files2load_results_title[i0+1]
    # Extract year and site location to identify which cambium file to import
    year = int(filecase[0])
    site = filecase[1]
    
    if year == 2020:
        cambium_year = 2025
    elif year == 2025:
        cambium_year = 2030
    elif year == 2030:
        cambium_year ==2035
    elif year == 2035:
        cambium_year = 2040
    
    # Read in the cambium 
    cambiumdata_filepath = dircambium + site + '_'+str(cambium_year) + '.csv'
    cambium_data = pd.read_csv(cambiumdata_filepath,index_col = None,header = 4,usecols = ['lrmer_co2_c','lrmer_ch4_c','lrmer_n2o_c','lrmer_co2_p','lrmer_ch4_p','lrmer_n2o_p','lrmer_co2e_c','lrmer_co2e_p','lrmer_co2e'])
    
    cambium_data = cambium_data.reset_index().rename(columns = {'index':'Interval','lrmer_co2_c':'LRMER CO2 combustion (kg/MWh)','lrmer_ch4_c':'LRMER CH4 combustion (g/MWh)','lrmer_n2o_c':'LRMER N2O combustion (g/MWh)',\
                                                  'lrmer_co2_p':'LRMER CO2 production (kg/MWh)','lrmer_ch4_p':'LRMER CH4 production (g/MWh)','lrmer_n2o_p':'LRMER N2O production (g/MWh)','lrmer_co2e_c':'LRMER CO2 equiv. combustion (kg/MWh)',\
                                                  'lrmer_co2e_p':'LRMER CO2 equiv. production (kg/MWh)','lrmer_co2e':'LRMER CO2 equiv. total (kg/MWh)'})
    
    cambium_data['Interval']=cambium_data['Interval']+1
    cambium_data = cambium_data.set_index('Interval')
        
        
    # Read in rodeo data
    rodeo_filepath = dir0+files2load_results[i0+1]
    rodeo_data = pd.read_csv(rodeo_filepath,index_col = None, header = 26,usecols = ['Interval','Input Power (MW)','Non-Ren Import (MW)','Renewable Input (MW)','Curtailment (MW)','Product Sold (units of product)'])
    rodeo_data = rodeo_data.rename(columns = {'Input Power (MW)':'Normalized Electrolyzer Power (-)','Non-Ren Import (MW)':'Normalized Grid Import (-)','Renewable Input (MW)':'Normalized Renewable Input (-)', 'Curtailment (MW)':'Normalized Curtailment (-)','Product Sold (units of product)':'Hydrogen production (kg/MW)'})

    # Combine RODeO and Cambium data into one dataframe
    combined_data = rodeo_data.merge(cambium_data, on = 'Interval',how = 'outer')
    
    # Calculate hourly emissions factors of interest. If we want to use different GWPs, we can do that here.
    combined_data['Total grid emissions (kg-CO2/MW)'] = combined_data['Normalized Grid Import (-)']*combined_data['LRMER CO2 equiv. total (kg/MWh)']
    combined_data['Scope 2 (combustion) grid emissions (kg-CO2/MW)'] = combined_data['Normalized Grid Import (-)']*combined_data['LRMER CO2 equiv. combustion (kg/MWh)']
    combined_data['Scope 3 (production) grid emissions (kg-CO2/MW)'] = combined_data['Normalized Grid Import (-)']*combined_data['LRMER CO2 equiv. production (kg/MWh)']
    
    # Sum total emissions. Note that the 30 indicates system life; the 1000 converts kg to metric tonnes
    total_emissions_sum = combined_data['Total grid emissions (kg-CO2/MW)'].sum()*30/1000
    scope2_combustion_emissions_sum = combined_data['Scope 2 (combustion) grid emissions (kg-CO2/MW)'].sum()*30/1000
    scope3_production_emissions_sum = combined_data['Scope 3 (production) grid emissions (kg-CO2/MW)'].sum()*30/1000
    h2prod_sum = combined_data['Hydrogen production (kg/MW)'].sum()*30/1000
    grid_emission_intensity_annual_average = combined_data['LRMER CO2 equiv. total (kg/MWh)'].mean()
    
    # Calculate SMR emissions
    smr_Scope3_EI = smr_NG_supply * (smr_NG_consume - smr_steam_prod/smr_HEX_eff) * g_to_kg_conv # kg CO2e/kg H2
    smr_Scope2_EI = smr_PO_consume * grid_emission_intensity_annual_average * g_to_kg_conv # kg CO2e/kg H2
    smr_Scope1_EI = smr_NG_combust * (smr_NG_consume - smr_steam_prod/smr_HEX_eff) * g_to_kg_conv # kg CO2e/kg H2
    
    # Put all cumulative metrics into a dictionary, and then a dataframe
    d = {'Total Life Cycle H2 Production (tonnes-H2/MW)': [h2prod_sum],'Total Scope 2 (Combustion) Life Cycle Emissions (tonnes-CO2/MW)':[scope2_combustion_emissions_sum],\
         'Total Scope 3 (Production) Life Cycle Emissions (tonnes-CO2/MW)': [scope3_production_emissions_sum],'Total Life Cycle Emissions (tonnes-CO2/MW)' : [total_emissions_sum],\
         'Annaul Average Grid Emission Intensity (kg-CO2/MWh)':grid_emission_intensity_annual_average,'SMR Scope 3 Life Cycle Emissions (kg-CO2/kg-H2)':smr_Scope3_EI,\
         'SMR Scope 2 Life Cycle Emissions (kg-CO2/kg-H2)':smr_Scope2_EI, 'SMR Scope 1 Life Cycle Emissions (kg-CO2/kg-H2)':smr_Scope1_EI}
    emissionsandh2 = pd.DataFrame(data = d)
    for i1 in range(len(files2load_title_header)):
        emissionsandh2[files2load_title_header[i1]] = files2load_results_title[i0+1][i1]
    if i0 == 0:
        emissionsandh2_output = emissionsandh2
    else:
        emissionsandh2_output = pd.concat([emissionsandh2_output,emissionsandh2],ignore_index = True)
        #emissionsandh2_output = emissionsandh2_output.append(emissionsandh2,ignore_index = True)

# Calculate life cycle emissions on a kg-CO2/kg-H2 basis
emissionsandh2_output['Year'] = emissionsandh2_output['Year'].astype(int)
emissionsandh2_output['Total Life Cycle Emissions (kg-CO2/kg-H2)'] = emissionsandh2_output['Total Life Cycle Emissions (tonnes-CO2/MW)']/emissionsandh2_output['Total Life Cycle H2 Production (tonnes-H2/MW)']
emissionsandh2_output['Scope 2 Emissions (kg-CO2/kg-H2)'] = emissionsandh2_output['Total Scope 2 (Combustion) Life Cycle Emissions (tonnes-CO2/MW)']/emissionsandh2_output['Total Life Cycle H2 Production (tonnes-H2/MW)']
emissionsandh2_output['Scope 3 Emissions (kg-CO2/kg-H2)'] = emissionsandh2_output['Total Scope 3 (Production) Life Cycle Emissions (tonnes-CO2/MW)']/emissionsandh2_output['Total Life Cycle H2 Production (tonnes-H2/MW)']

# Set up Scope 1 emissions as zeros since we currently don't have anything for Scope 1 emissions
scope1_emissions = [0]*emissionsandh2_output.shape[0]
scope1_emissions = pd.DataFrame(scope1_emissions,columns = ['Scope 1 Emissions (kg-CO2/kg-H2)'])
emissionsandh2_output = emissionsandh2_output.join(scope1_emissions)

# Downselect to grid cases of interest
emissionsandh2_output = emissionsandh2_output.loc[emissionsandh2_output['Grid Case'].isin(['grid-only-'+grid_price_scenario,'hybrid-grid-'+grid_price_scenario,'off-grid'])]

### ATTENTION!!! Plotting below doesn't really work. I think we need to change the way we are doing plots
# since we have more distinction between locations

# years = pd.unique(emissionsandh2_output['Year']).tolist()

# for year in years:
#     year = 2030
#     gridonly_emissions = emissionsandh2_output.loc[(emissionsandh2_output['Year'] == year) & (emissionsandh2_output['Grid Case'] == 'grid-only-'+grid_price_scenario)]
#     offgrid_emissions = emissionsandh2_output.loc[(emissionsandh2_output['Year'] == year) & (emissionsandh2_output['Grid Case'] == 'off-grid') ]
#     hybridgrid_emissions = emissionsandh2_output.loc[(emissionsandh2_output['Year'] == year) & (emissionsandh2_output['Grid Case'] == 'hybrid-grid-'+grid_price_scenario) ]

#     smr_emissions = offgrid_emissions.drop(labels = ['Scope 1 Emissions (kg-CO2/kg-H2)','Scope 2 Emissions (kg-CO2/kg-H2)','Scope 3 Emissions (kg-CO2/kg-H2)'],axis=1)
#     # just use IA since all are the same right now
#     smr_emissions = smr_emissions.loc[smr_emissions['Site']=='IA'].drop(labels = ['Site'],axis=1)
#     smr_emissions['Site'] = 'SMR - \n all sites'
#     smr_emissions = smr_emissions.rename(columns = {'SMR Scope 3 Life Cycle Emissions (kg-CO2/kg-H2)':'Scope 3 Emissions (kg-CO2/kg-H2)','SMR Scope 2 Life Cycle Emissions (kg-CO2/kg-H2)':'Scope 2 Emissions (kg-CO2/kg-H2)',
#                                                     'SMR Scope 1 Life Cycle Emissions (kg-CO2/kg-H2)':'Scope 1 Emissions (kg-CO2/kg-H2)'})
    
#     # The current plotting method will not work for all grid cases; we will need to change how we do it
#     # This at least makes it possible to compare grid-only emissions with SMR emissions
#     aggregate_emissions = pd.concat([gridonly_emissions,smr_emissions])

#     smr_total_emissions = aggregate_emissions.loc[aggregate_emissions['Site'] == 'SMR - \n all sites','Scope 3 Emissions (kg-CO2/kg-H2)'] + aggregate_emissions.loc[aggregate_emissions['Site'] == 'SMR - \n all sites','Scope 2 Emissions (kg-CO2/kg-H2)'] \
#                         + aggregate_emissions.loc[aggregate_emissions['Site'] == 'SMR - \n all sites','Scope 1 Emissions (kg-CO2/kg-H2)'] 
#     smr_total_emissions = smr_total_emissions.tolist()
#     smr_total_emissions = smr_total_emissions[0]
    
#     labels = pd.unique(aggregate_emissions['Site']).tolist()
    
#     scope3 = aggregate_emissions['Scope 3 Emissions (kg-CO2/kg-H2)']
#     scope2 = aggregate_emissions['Scope 2 Emissions (kg-CO2/kg-H2)']
#     scope1 = aggregate_emissions['Scope 1 Emissions (kg-CO2/kg-H2)']
#     width = 0.3
#     fig, ax = plt.subplots()
#     #ax.set_ylim([0, 18])
#     ax.bar(labels, scope3, width, label = 'Scope 3 emission intensities', color = 'darkcyan')
#     ax.bar(labels, scope2, width, bottom = scope3, label = 'Scope 2 emission intensities', color = 'darkorange')
#     ax.bar(labels, scope1, width, bottom = scope3, label = 'Scope 1 emission intensities', color = 'goldenrod')
#     #valuelabel(scope1, scope2, scope3, labels)
#     ax.set_ylabel('GHG Emission Intensities (kg CO2e/kg H2)')
#     ax.set_title('GHG Emission Intensities - All Sites ' + str(year))
#     plt.axhline(y = smr_total_emissions, color='red', linestyle ='dashed', label = 'GHG emissions baseline')
#     ax.legend(loc='upper right', 
#                       #bbox_to_anchor=(0.5, 1),
#              ncol=1, fancybox=True, shadow=False, borderaxespad=0, framealpha=0.2)
#             #fig.tight_layout() 
#     plt.savefig(dir_plot+'GHG Emission Intensities_all_sites_'+str(year)+'.png', dpi = 1000)
    
#Pull in TEA data
# Read in the summary data from the database
conn = sqlite3.connect(dirfinancial+'Default_summary.db')
TEA_data = pd.read_sql_query("SELECT * From Summary",conn)

conn.commit()
conn.close()


TEA_data = TEA_data[['Hydrogen model','Site','Year','Turbine Size','Electrolysis case','Policy Option','Grid Case','Hydrogen annual production (kg)',\
                     'Steel annual production (tonne/year)','Ammonia annual production (kg/year)','LCOH ($/kg)','Steel price: Total ($/tonne)','Ammonia price: Total ($/kg)']]
TEA_data = TEA_data.loc[(TEA_data['Hydrogen model']=='RODeO') & (TEA_data['Grid Case'].isin(['grid-only-'+grid_price_scenario,'hybrid-grid-'+grid_price_scenario,'off-grid']))]
TEA_data['Year'] = TEA_data['Year'].astype(np.int32)
TEA_data = TEA_data.drop(labels = ['Hydrogen model'],axis =1)
TEA_data['Policy Option'] = TEA_data['Policy Option'].replace(' ','-')

# Combine data into one dataframe
combined_TEA_LCA_data = TEA_data.merge(emissionsandh2_output,how = 'outer', left_index = False,right_index = False)

# Example of calculating carbon abatement cost. 
# This section is mostly just to give a sense for how things like carbon abatement cost could be calculated for the above 
# structure
smr_cost_no_ccs = 1 # USD/kg-H2; just an approximation for now

combined_TEA_LCA_data['Total SMR Emissions (kg-CO2/kg-H2)'] = combined_TEA_LCA_data['SMR Scope 3 Life Cycle Emissions (kg-CO2/kg-H2)'] +combined_TEA_LCA_data['SMR Scope 2 Life Cycle Emissions (kg-CO2/kg-H2)'] + combined_TEA_LCA_data['SMR Scope 1 Life Cycle Emissions (kg-CO2/kg-H2)']

combined_TEA_LCA_data['CO2 abatement cost ($/MT-CO2)'] = (combined_TEA_LCA_data['LCOH ($/kg)'] - smr_cost_no_ccs)/(combined_TEA_LCA_data['Total SMR Emissions (kg-CO2/kg-H2)']-combined_TEA_LCA_data['Total Life Cycle Emissions (kg-CO2/kg-H2)'])*1000

# Segregate data by grid scenario
TEALCA_data_offgrid = combined_TEA_LCA_data.loc[combined_TEA_LCA_data['Grid Case'].isin(['off-grid'])] 
TEALCA_data_gridonly = combined_TEA_LCA_data.loc[combined_TEA_LCA_data['Grid Case'].isin(['grid-only-'+grid_price_scenario])]
TEALCA_data_hybridgrid = combined_TEA_LCA_data.loc[combined_TEA_LCA_data['Grid Case'].isin(['hybrid-grid-'+grid_price_scenario])]

# Pivot tables for Emissions plots vs year
hydrogen_abatementcost_offgrid = TEALCA_data_offgrid.pivot_table(index = 'Year',columns = ['Site','Grid Case'], values = 'CO2 abatement cost ($/MT-CO2)')
hydrogen_abatementcost_gridonly = TEALCA_data_gridonly.pivot_table(index = 'Year',columns = ['Site','Grid Case'], values = 'CO2 abatement cost ($/MT-CO2)')
hydrogen_abatementcost_hybridgrid = TEALCA_data_hybridgrid.pivot_table(index = 'Year',columns = ['Site','Grid Case'], values = 'CO2 abatement cost ($/MT-CO2)')

# Create lists of scenario names for plot legends
names_gridonly = hydrogen_abatementcost_gridonly.columns.values.tolist()
names_gridonly_joined = []
for j in range(len(hydrogen_abatementcost_gridonly.columns)):
    names_gridonly_joined.append(', '.join(names_gridonly[j]))
    
names_hybridgrid = hydrogen_abatementcost_hybridgrid.columns.values.tolist()
names_hybridgrid_joined = []
for j in range(len(hydrogen_abatementcost_hybridgrid.columns)):
    names_hybridgrid_joined.append(', '.join(names_hybridgrid[j]))
    
names_offgrid = hydrogen_abatementcost_offgrid.columns.values.tolist()
names_offgrid_joined = []
for j in range(len(hydrogen_abatementcost_offgrid.columns)):
    names_offgrid_joined.append(', '.join(names_offgrid[j]))

# Abatement cost vs year
fig5, ax5 = plt.subplots(3,1,sharex = 'all',figsize = (4,8),dpi = 150)
ax5[0].plot(hydrogen_abatementcost_gridonly,marker = '.')
ax5[1].plot(hydrogen_abatementcost_hybridgrid,marker = '.')
ax5[2].plot(hydrogen_abatementcost_offgrid ,marker = '.')
for ax in ax5.flat:
    ax.tick_params(axis = 'y',labelsize = 10,direction = 'in')
    ax.tick_params(axis = 'x',labelsize = 10,direction = 'in',rotation = 45)
ax5[0].set_ylabel('Grid-Only CO2 Abatement Cost \n($/t-CO2)',fontsize = 10, fontname = 'Arial')
ax5[1].set_ylabel('Hybrid-Grid CO2 Abatement Cost \n($/t-CO2)',fontsize = 10, fontname='Arial')
ax5[2].set_ylabel('Off-Grid CO2 Abatement Cost \n($/t-CO2)',fontsize = 10, fontname = 'Arial')
ax5[2].set_xlabel('Year',fontsize = 10,fontname = 'Arial')
ax5[0].legend(names_gridonly_joined,prop = {'family':'Arial','size':6})
ax5[1].legend(names_hybridgrid_joined,prop = {'family':'Arial','size':6})
ax5[2].legend(names_offgrid_joined ,prop = {'family':'Arial','size':6})
plt.tight_layout()
plt.savefig(dir_plot+'hydrogen_abatement_cost.png',pad_inches = 0.1)
plt.close(fig = None)