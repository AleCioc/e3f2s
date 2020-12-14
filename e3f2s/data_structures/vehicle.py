example_vehicle_config = {
	"engine_type": "gasoline",
	"fuel_capacity": 55,
	"consumption": 18.215,
	"cost_car": 24700,
	"country_energy_mix" : {
		"nuclear": 0, # %
		"natural_gas": 45, # %
		"coal": 9.3, # %
		"oil":0, # %
		"biomass": 9, # %
		"other":6.2, # %
		"hydro": 16.3, # %
		"wind":6.2, # %
		"waste":0, # %
		"solar": 8.3, # %
		"geothermal":0, # %
	}
}

lca_co2_elect_sources = {
	"nuclear":12, # g/kWh
	"natural_gas":490, # g/kWh
	"coal":910, # g/kWh
	"oil":650, # g/kWh
	"biomass":230, # g/kWh
	"other":490, # g/kWh
	"hydro":24, # g/kWh
	"wind":11, # g/kWh
	"waste":620, # g/kWh
	"geothermal": 38, # g/kWh
	"solar":11, # g/kWh
}

energy_electr_sources = {
	"nuclear": 2.9,  # MJ/MJel
	"natural_gas": 1.15,  # MJ/MJel
	"coal": 1.69,  # MJ/MJel
	"oil": 1.76,  # MJ/MJel
	"biomass": 2.985,  # MJ/MJel
	"other": 1.76,  # MJ/MJel
	"hydro": 0,  # MJ/MJel
	"wind": 0.07,  # MJ/MJel
	"waste": 0,  # MJ/MJel
	"geothermal": 0,  # MJ/MJel
	"solar": 0,  # MJ/MJel
}

class Vehicle(object):
	def __init__(self, vehicle_config):
		self.engine_type = vehicle_config["engine_type"] #gasoline, diesel, lpg, gnc, electric
		self.consumption = vehicle_config["consumption"] #km/l, km/kWh
		self.capacity = vehicle_config["fuel_capacity"] #kWh (electric), Liter (gasoline,diesel,lpg), kilograms (gnc)
		self.cost_car = vehicle_config["cost_car"] # in €

		if self.engine_type == "gasoline": # GASOLINE E5
			self.welltotank_emission = 17 #gCO2eq/MJ (pathway code COG-1)
			self.welltotank_energy = 0.24 #MJ/MJgasoline
			self.density = 745.8 # g/L
			self.lower_heating_value = 42.3 #MJ/kg
			self.carbon_content = 84.7 #%
			self.thc_limits = 100 #mg/km
			self.nox_limits = 60 #mg/km
			self.perc_ch4_limits = 5 #%
			self.perc_n2o_limits = 3 #%
			self.gwp_ch4 = 25
			self.gwp_n2o = 298
		elif self.engine_type == "diesel": # DIESEL B7
			self.welltotank_emission = 18.9 #gCO2eq/MJ (pathway code COD-1)
			self.welltotank_energy = 0.26 #MJ/MJdiesel
			self.density = 836.1 # g/L
			self.lower_heating_value = 42.7  # MJ/kg
			self.carbon_content = 85.4  # %
			self.thc_limits = 90  # mg/km
			self.nox_limits = 80  # mg/km
			self.perc_ch4_limits = 10  # %
			self.perc_n2o_limits = 5  # %
			self.gwp_ch4 = 25
			self.gwp_n2o = 298
		elif self.engine_type == "lpg":
			self.welltotank_emission = 7.8 #gCO2eq/MJ (pathway code LRLP-1 min 7.7 - max 8.3)
			self.welltotank_energy = 0.12 #MJ/MJlpg
			self.density = 550 # g/L
			self.lower_heating_value = 46  # MJ/kg
			self.carbon_content = 82.4  # %
			self.thc_limits = 100  # mg/km
			self.nox_limits = 60  # mg/km
			self.perc_ch4_limits = 5  # %
			self.perc_n2o_limits = 3  # %
			self.gwp_ch4 = 25
			self.gwp_n2o = 298
		elif self.engine_type == "cng":
			self.welltotank_emission = 11.4 #gCO2eq/MJ (pathway code GMCG-1 min 10.5  - max 12.7)
			self.welltotank_energy = 0.15 #MJ/MJcng
			self.density = 1000 #g/kg
			self.lower_heating_value = 48  # MJ/kg
			self.carbon_content = 73.5  # %
			self.thc_limits = 100  # mg/km
			self.nox_limits = 60  # mg/km
			self.perc_ch4_limits = 60  # %
			self.perc_n2o_limits = 3  # %
			self.gwp_ch4 = 25
			self.gwp_n2o = 298
		elif self.engine_type == "electric":
			tot_emission = 0
			tot_energy = 0
			for i in list(lca_co2_elect_sources.keys()):
				tot_emission = tot_emission + lca_co2_elect_sources[i] * example_vehicle_config[
					"country_energy_mix"
				][i]/100
				tot_energy = tot_energy + energy_electr_sources[i] * example_vehicle_config[
					"country_energy_mix"
				][i] / 100
			self.welltotank_emission = tot_emission  #gCO2eq/kWh
			self.welltotank_energy = tot_energy #MJ/MJelectricity
			self.tx_efficiency = 92.5 # %


	def get_charging_time_from_perc(self, actual_level_perc, flow_amount, beta=100):
		# flow_amount is generalized to represent the amount of fuel
		# loaded in the vehicle per unit of time
		# electric: kW (3.3,7.4,11,22,43,50,120)
		# gasoline,diesel,lpg: liter/min (between 30-50)
		# gnc: kg/min (between 30-70)

		if self.engine_type == "electric":
			power_output = flow_amount / 1000
			capacity_left = ((beta - actual_level_perc) / 100) * self.capacity
			return (capacity_left / power_output) * 3600
		elif self.engine_type in ["gasoline", "diesel", "lpg","cng"]:
			flow_rate = flow_amount
			capacity_left = ((beta - actual_level_perc)/100) * self.capacity
			return (capacity_left/flow_rate) * 60

	def get_percentage_from_charging_time(self, charging_time, flow_amount):
		# flow_amount is generalized to represent the amount of fuel
		# loaded in the vehicle per unit of time
		# electric: kW (3.3,7.4,11,22,43,50,120)
		# gasoline,diesel,lpg: liter/min (between 30-50)
		# gnc: kg/min (between 30-70)

		if self.engine_type == "electric":
			power_output = flow_amount / 1000
			capacity_left = power_output * (charging_time / 3600)
			return 100 * (capacity_left / self.capacity)
		elif self.engine_type in ["gasoline", "diesel", "lpg", "cng"]:
			flow_rate = flow_amount
			capacity_left = (flow_rate * charging_time)/60
			return 100 * (capacity_left / self.capacity)

	def tanktowheel_energy_from_perc(self, percentage):
		if self.engine_type == "electric":
			tanktowheel_kwh = self.percentage_to_consumption(percentage)
		elif self.engine_type in ["gasoline", "diesel", "lpg", "cng"]:
			tanktowheel_kwh = self.percentage_to_consumption(percentage) * (
					self.lower_heating_value / (1 / (self.density / 1000)) # converted lhv from MJ/kg to MJ/L
			) / 3.6
		return tanktowheel_kwh

	def welltotank_energy_from_perc(self, percentage):
		if self.engine_type == "electric":
			tanktowheel_mj = self.tanktowheel_energy_from_perc(percentage) * 3.6
			welltotank_kwh = (self.welltotank_energy * (
					1 + 0.01 * ((100 - self.tx_efficiency) / (1 - 0.01 * (100 - self.tx_efficiency)))
			) * tanktowheel_mj) / 3.6
		elif self.engine_type in ["gasoline", "diesel", "lpg", "cng"]:
			tanktowheel_mj = self.tanktowheel_energy_from_perc(percentage) * 3.6
			welltotank_kwh = (self.welltotank_energy * tanktowheel_mj) / 3.6
		return welltotank_kwh

	def from_kml_to_lkm(self):
		return 1 / self.consumption

	def from_kml_to_energyperkm(self):
		perkm_consumption = self.from_kml_to_lkm()
		return perkm_consumption * (
					self.lower_heating_value / (1 / (self.density / 1000)) # converted lhv from MJ/kg to MJ/L
			)

	def consumption_to_percentage(self, consumption):
		# x:100 = consumption : capacity
		percentage = (consumption * 100) / self.capacity
		return percentage

	def percentage_to_consumption(self, percentage):
		# x:100 = consumption : capacity
		consumption = (percentage * self.capacity) / 100
		return consumption

	def distance_to_consumption(self, distance):
		perkm_consumption = self.from_kml_to_lkm()
		tot_consumption = perkm_consumption * distance
		return tot_consumption

	def distance_to_welltotank_emission(self,distance):
		if self.engine_type in ["gasoline", "diesel", "lpg", "cng"]:
			wtt_emissions_perkm = self.welltotank_emission * self.from_kml_to_energyperkm()
		elif self.engine_type == "electric":
			wtt_emissions_perkm = self.welltotank_emission * (
					1 + 0.01 * ((100 - self.tx_efficiency) / (1 - 0.01 * (100 - self.tx_efficiency)))
			) * (1 / self.consumption)
		tot_wtt_emissions = distance * wtt_emissions_perkm
		return tot_wtt_emissions

	def distance_to_tanktowheel_emission(self,distance):
		if self.engine_type in ["gasoline", "diesel", "lpg", "cng"]:
			# TTW emission coefficient evaluated as sum of 1. co2 emissions per km,
			# 2. co2 equivalent emissions of CH4 per km,
			# 3. co2 equivalent emissions of n2o per km

			# 1. Start from C + O2 -> CO2 reaction, given moles of carbon in 1 L of fuel,
			# find the amount of oxygen needed in the combustion, then
			# the total co2 produced by 1 L of fuel is multiplied by
			# the consumption in l/km, to get emissions gCO2/km
			# 2. Amount of CH4 CO2equivalent emissions, responsible of global warming, per km
			# (see JEC TTW v5 EU report), evaluated in ttw_co2eq_emissions_ch4
			# 3. Amount of N2O CO2equivalent emissions, responsible of global warming, per km
			# (see JEC TTW v5 EU report), evaluated in ttw_co2eq_emissions_n2o

			carbon_moles = ((self.carbon_content / 100) * self.density) / 12.01
			grams_oxygen = 32 * carbon_moles
			ttw_co2_emissions_perkm = (1 / self.consumption) * (
					(self.carbon_content / 100) * self.density + grams_oxygen
			) # g/km
			ttw_co2eq_emissions_ch4 = (self.thc_limits / 1000) * (self.perc_ch4_limits / self.thc_limits) * self.gwp_ch4 # g/km
			ttw_co2eq_emissions_n2o = (self.nox_limits / 1000) * (self.perc_n2o_limits / self.nox_limits) * self.gwp_n2o # g/km
			tot_ttw_emissions = (
					ttw_co2_emissions_perkm + ttw_co2eq_emissions_ch4 + ttw_co2eq_emissions_n2o
			) * distance # gCO2
		elif self.engine_type == "electric":
			tot_ttw_emissions = 0
		return tot_ttw_emissions

# car = Vehicle(example_vehicle_config)
# distance = 1
# ttw = car.distance_to_tanktowheel_emission(distance)
# wtt = car.distance_to_welltotank_emission(distance)
# print("TTW: ", ttw)
# print("WTT: ", wtt)