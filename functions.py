'''
This module contains axiliary functions used for the project in
the course Integrated Energy Grids
'''

import numpy as np

dollar2euro = 0.9239 # [€/$] -- https://www.valutakurser.dk - 25/03-25

def annuity(n, r):
    """ Calculate the annuity factor for an asset with lifetime n years and
    discount rate  r """

    if r > 0:
        return r/(1. - 1./(1.+r)**n)
    return 1/n

def load_generator_data(techs_labels):
    ''' Define data needed to setup the generators in the Pypsa network '''

    ''' unit conversion constants and universal constants'''
    kJ2MWh = 1/(10**3 * 60**2) # [MWh/kJ]
    MMBtu2MWh = 0.293 # [MWh / MMBtu]
    coal_energy_density = 24 / 60**2 * 10**3 # [MJ/kg] -> [MWh/t]
    '''
    # From Teknologikataloget (Version 2025: 2030-values): https://ens.dk/analyser-og-statistik/teknologikatalog-produktion-af-el-og-fjernvarme, pp. 209, 260, and 361/371 
        # technology: wind, solar, OCGT, coal, biomass
        # metric:     capital costs(wind, solar, OCGT, biomass), efficiencies (OCGT, biomass), lifetime

    # https://iopscience.iop.org/article/10.1088/1748-9326/11/11/114010/meta -- their gas numbers match ours nicely
        # technology: coal
        # metric:     capital costs

    # https://ourworldindata.org/grapher/coal-prices
        # technology: coal
        # metric:     fuel costs

    # https://ourworldindata.org/grapher/natural-gas-prices
        # technology: gas
        # metric:     fuel costs

    # https://www.gevernova.com/gas-power/resources/articles/2018/come-hele-or-high-water
        # technology: coal
        # metric:     efficiency

    # https://www.sciencedirect.com/science/article/pii/S1364032121001301
        # technology: nuclear
        # metric:     capital costs, fuel/variable costs

    # https://www.iaea.org/sites/default/files/29402043133.pdf
        # technoklogy: nuclear
        # metric:      lifetime

    # https://www.sciencedirect.com/science/article/pii/S0196890422001297?via%3Dihub
        # technology: biomass
        # metric:     fuel costs
        # the price is given as 41 $/tonne and LHV in kJ/kg, so the conversion is a little tricky as may be noticed below
    '''
    lifetimes = [30, 25, 25, 15, 40, 25] # years

    capital_costs = np.array([1.333, 0.26, 0.435, 1.75, 9, 3.1]) * 10**6 # €/MW, originally in M€/MW, pp. 209,260,371
    '''# https://backend.orbit.dtu.dk/ws/portalfiles/portal/158807620/OffshoreOnshore_Energy_Policy_August_revision_28_8.pdf
        # More optimistic onshore wind capital costs -- without these the results are still interesting, though'''
    #capital_costs[0] = 0.8e6
    dict_capital_costs_annualized = {tech:annuity(lifetime, 0.07)*cost*(1+0.03) for tech,cost,lifetime in zip(techs_labels,capital_costs,lifetimes)}

    efficiencies = np.array([1, # [MW_e/MW_th]
                            1,
                            0.43,
                            0.4,
                            1,
                            0.305])
    dict_efficiencies = {tech:eff for tech,eff in zip(techs_labels, efficiencies)}

    gas_co2_emissions = 52.91/10**3 # kg_CO2/kWh_th -> t_CO2/kWh_th -- from https://www.eia.gov/environment/emissions/co2_vol_mass.php
    coal_co2_emissions = 95.99/10**3 # kg_CO2/kWh_th -> t_CO2/kWh_th

    fuel_costs_dollars = np.array([0,  # -,-,$/MWh_th, $/MWh_th, $/MWh_e, $/MWh_th
                                0,
                                41.97, 
                                129.54/coal_energy_density, # $/t -> $/MWh_th 
                                10.11,
                                41/10**3/19970 / kJ2MWh]) # originally 41 $/tonne, HHV=19970 kJ/kg
    fuel_costs = (fuel_costs_dollars
                * np.array([0, 0, dollar2euro, dollar2euro, dollar2euro, dollar2euro])) # €/MWh_th, MWh_e for nuclear
    dict_fuel_costs = {tech:cost for tech,cost in zip(techs_labels, fuel_costs)}

    dict_marginal_costs = {tech:dict_fuel_costs[tech] / dict_efficiencies[tech] for tech in techs_labels} # €/MWh_e

    CO2_emissions = [0, # CO2_emissions [kgCO2/kWh_th=tCO2/MWh_th] for each carrier
                    0,
                    gas_co2_emissions/MMBtu2MWh,
                    coal_co2_emissions/MMBtu2MWh,
                    0,
                    0]  # biomass is assumed to be sourced sustainably...
    
    return (dict_capital_costs_annualized,
            dict_marginal_costs,
            dict_efficiencies,
            CO2_emissions)

def load_storage_units_data(techs_labels_storageunits):
    # All capital costs are from the 2025 version of the 
    # Technology Catalogue for 'Energy Storage' (DEA)
    # https://ens.dk/en/analyses-and-statistics/technology-catalogues

    # StorageUnits:
    # Molten salt carnot battery '143b'
    # Li-ion '180'
    # Vanadium redox battery '181'

    Crates = np.array([120/800, 3.5/7, 0.5/2]) # MW / MWh
    capital_costs_storageunits_MWh = np.array([0.063, 0.66, 0.37]) * 1e6 # M€/MWh
    capital_costs_storageunits = capital_costs_storageunits_MWh / Crates # M€/MW
    lifetimes_storageunits = np.array([25, 25, 20]) # years
    dict_capital_costs_annualized_storageunits = {
        storage:annuity(lifetime, 0.07)*cost*(1+0.03)
        for storage, cost, lifetime in zip(techs_labels_storageunits,
                                        capital_costs_storageunits,
                                        lifetimes_storageunits)
        }

    efficiencies_in = {storage: eff for storage, eff in zip(techs_labels_storageunits,
                                                            [np.sqrt(0.3),
                                                            np.sqrt(0.92),
                                                            np.sqrt(0.78)])}
    efficiencies_out = {storage: eff for storage, eff in zip(techs_labels_storageunits,
                                                            [np.sqrt(0.3),
                                                            np.sqrt(0.92),
                                                            np.sqrt(0.78)])}
    hourly_losses = {storage: loss for storage, loss in zip(techs_labels_storageunits,
                                                            np.array([0.9,
                                                                    0.1,
                                                                    0.0])/100/24)}
    # the above units are converted [%/day] * 1/100/24 -> [p.u./h]
    # no standing losses are given for the Vanadium redox flow battery...
    return (dict_capital_costs_annualized_storageunits,
            efficiencies_in,
            efficiencies_out,
            Crates,
            hourly_losses)

def load_hydro_cost(): # Costs of hydro: https://www.irena.org/-/media/Files/IRENA/Agency/Publication/2022/Jul/IRENA_Power_Generation_Costs_2021.pdf
    capital_cost_hydro = 1628 * dollar2euro * 10**3 #  $/kW -> €/MW -- using rather big plants from pp. 144^^
    lifetime_hydro = 75  # middle of 50-100 year interval from https://www.eia.gov/energyexplained/hydropower/hydropower-and-the-environment.php
    capital_cost_hydro_annualized = annuity(lifetime_hydro, 0.07)*capital_cost_hydro*(1+0.03)  # €/MW/a
    return capital_cost_hydro_annualized
