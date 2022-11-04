"""
Function to call pyfast for ammonia model
Written by Abhineet Gupta
"""


# Add location of PyFAST code 
import sys
sys.path.append('../PyFAST/')

import src.PyFAST as PyFAST

# Implement equations from Ammonia model received
def run_pyfast_for_ammonia(plant_capacity_kgpy,plant_capacity_factor,plant_life,levelized_cost_of_hydrogen, electricity_cost,cooling_water_cost,iron_based_catalyist_cost,oxygen_price):
    # Inputs:
        # plant_capacity_kgpy = 462,323,016 KgNH3/year
        # plant_capacity_factor = 0.9
        # plant_life = 40 years
        
        # ammonia_production_kgpy = plant_capacity_kgpy*plant_capacity_factor =  416,090,714 
        
        # Costs from original model (for reference)
        # levelized_cost_of_hydrogen = 4.83       # $/kg
        # electricity_cost = 69.83                # $/MWh
        # cooling_water_cost = 0.000113349938601175 # $/Gal
        # iron_based_catalyist_cost = 23.19977341 # $/kg
        # oxygen_price = 0.0285210891617726       # $/kg
    
    # scale with respect to a baseline plant
    scaling_ratio = plant_capacity_kgpy/(365.0*1266638.4)
    
    # CapEx
    scaling_factor_equipment = 0.6
    capex_scale_factor = scaling_ratio**scaling_factor_equipment
    capex_air_separation_crygenic = 22506100 * capex_scale_factor
    capex_haber_bosch = 18642800 * capex_scale_factor
    capex_boiler = 7069100 * capex_scale_factor
    capex_cooling_tower = 4799200 * capex_scale_factor
    capex_direct = capex_air_separation_crygenic + capex_haber_bosch\
        + capex_boiler + capex_cooling_tower
    capex_depreciable_nonequipment = capex_direct*0.42 + \
        4112701.84103543*scaling_ratio
    capex_total = capex_direct + capex_depreciable_nonequipment\
        + 2500000*capex_scale_factor
    
    
    # O&M Cost
    scaling_factor_labor = 0.25
    labor_cost = 57 * 50 * 2080 * scaling_ratio**scaling_factor_labor
    general_administration_cost = labor_cost * 0.2
    property_tax_insurance = capex_total * 0.02
    maintenance_cost = capex_direct * 0.005 * \
        scaling_ratio^scaling_factor_equipment
    fixed_O_and_M_cost = labor_cost + general_administration_cost + \
        property_tax_insurance + maintenance_cost
    
    # Feedstock
    H2_consumption = 0.197284403 # kg_H2/ kg_NH3
    H2_cost_in_startup_year = levelized_cost_of_hydrogen * H2_consumption\
         * plant_capacity_kgpy * plant_capacity_factor
    
    electricity_usage = 0.530645243/1000 # mWh/kg_NH3
    energy_cost_in_startup_year = electricity_cost * electricity_usage\
        * plant_capacity_kgpy * plant_capacity_factor # 
    
    cooling_water_usage = 0.049236824 # Gal/kg_NH3
    iron_based_catalyist_usage = 0.000091295354067341 # kg/kg_NH3
    non_energy_cost_in_startup_year = \
        ((cooling_water_cost * cooling_water_usage) + \
            (iron_based_catalyist_cost*iron_based_catalyist_usage)) * \
                plant_capacity_kgpy * plant_capacity_factor
    
    variable_cost_in_startup_year = energy_cost_in_startup_year\
        + non_energy_cost_in_startup_year

    # By-product
    oxygen_byproduct = 0.29405077250145     # kg/kg_NH#
    credits_byproduct = oxygen_price*oxygen_byproduct * \
        plant_capacity_kgpy * plant_capacity_factor
    



     # Set up PyFAST
    pf = PyFAST.PyFAST('blank')
    
    # Fill these in - can have most of them as 0 also
    gen_inflation = 0.019
    pf.set_params('commodity',{"name":'Ammonia',"unit":"kg","initial price":1000,"escalation":gen_inflation})
    pf.set_params('capacity',plant_capacity_kgpy/365) #units/day
    pf.set_params('maintenance',{"value":0,"escalation":gen_inflation})
    pf.set_params('analysis start year',2015)
    pf.set_params('operating life',plant_life)
    pf.set_params('installation months',36)
    # pf.set_params('installation cost',{"value":XXX,"depr type":"Straight line","depr period":4,"depreciable":False})
    # pf.set_params('non depr assets',XXX)
    # pf.set_params('end of proj sale non depr assets',XXX*(1+gen_inflation)**plant_life)
    # pf.set_params('demand rampup',XXX)
    # pf.set_params('long term utilization',plant_capacity_factor)
    # pf.set_params('credit card fees',0)
    # pf.set_params('sales tax',0) 
    # pf.set_params('license and permit',{'value':00,'escalation':gen_inflation})
    # pf.set_params('rent',{'value':0,'escalation':gen_inflation})
    # pf.set_params('property tax and insurance percent',0)
    # pf.set_params('admin expense percent',0)
    # pf.set_params('total income tax rate',0.27)
    # pf.set_params('capital gains tax rate',0.15)
    # pf.set_params('sell undepreciated cap',True)
    # pf.set_params('tax losses monetized',True)
    # pf.set_params('operating incentives taxable',True)
    # pf.set_params('general inflation rate',gen_inflation)
    # pf.set_params('leverage after tax nominal discount rate',0.1)
    # pf.set_params('debt equity ratio of initial financing',0.5)
    # pf.set_params('debt type','Revolving debt')
    # pf.set_params('debt interest rate',0.06)
    # pf.set_params('cash onhand percent',1)
    
    #----------------------------------- Add capital items to PyFAST ----------------
    pf.add_capital_item(name="Air Separation by Cryogenic",cost=capex_air_separation_crygenic,depr_type="MACRS",depr_period=20,refurb=[0])
    pf.add_capital_item(name="Haber Bosch",cost=capex_haber_bosch,depr_type="MACRS",depr_period=20,refurb=[0])
    pf.add_capital_item(name="Boiler and Steam Turbine",cost=capex_boiler,depr_type="MACRS",depr_period=20,refurb=[0])
    pf.add_capital_item(name="Cooling Tower",cost=capex_cooling_tower,depr_type="MACRS",depr_period=20,refurb=[0])
    pf.add_capital_item(name="Cooling Tower",cost=capex_cooling_tower,depr_type="MACRS",depr_period=20,refurb=[0])
    pf.add_capital_item(name="Depriciable Nonequipment",cost=capex_depreciable_nonequipment,depr_type="MACRS",depr_period=20,refurb=[0])
    pf.add_capital_item(name="Extra",cost=2500000*capex_scale_factor,depr_type="MACRS",depr_period=20,refurb=[0])
    
    #-------------------------------------- Add fixed costs--------------------------------
    pf.add_fixed_cost(name="Labor Cost",usage=1,unit='$/year',cost=labor_cost,escalation=gen_inflation)
    pf.add_fixed_cost(name="Maintenance Cost",usage=1,unit='$/year',cost=maintenance_cost,escalation=gen_inflation)
    pf.add_fixed_cost(name="Administrative Expense",usage=1,unit='$/year',cost=general_administration_cost,escalation=gen_inflation)
    pf.add_fixed_cost(name="Property tax and insurance",usage=1,unit='$/year',cost=property_tax_insurance,escalation=0.0) 
    # Putting property tax and insurance here to zero out depcreciation/escalation. Could instead put it in set_params if
    # we think that is more accurate
    
    #---------------------- Add feedstocks, note the various cost options-------------------
    pf.add_feedstock(name='Hydrogen',usage=H2_consumption,unit='kilogram of hydrogen per kilogram of ammonia',cost=levelized_cost_of_hydrogen,escalation=gen_inflation)
    pf.add_feedstock(name='Electricity',usage=electricity_usage,unit='MWh per kilogram of ammonia',cost=electricity_cost,escalation=gen_inflation)
    pf.add_feedstock(name='Cooling water',usage=cooling_water_usage,unit='Gallon per kilogram of ammonia',cost=cooling_water_cost,escalation=gen_inflation)
    pf.add_feedstock(name='Iron based catalyst',usage=iron_based_catalyist_usage,unit='kilogram of catalyst per kilogram of ammonia',cost=iron_based_catalyist_cost,escalation=gen_inflation)
    pf.add_coproduct(name='Oxygen byproduct',usage=oxygen_byproduct,unit='kilogram of oxygen per kilogram of ammonia',cost=oxygen_price,escalation=gen_inflation)
    
    #------------------------------ Sovle for breakeven price ---------------------------
    
    sol = pf.solve_price()
    
    summary = pf.summary_vals
    
    return(sol,summary)

