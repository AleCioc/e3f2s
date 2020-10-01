sim_scenario_conf = {

	"requests_rate_factor": 1,
	"fleet_load_factor": 2,

	"time_estimation": True,
	"queuing": True,

	"alpha": 26,
	"beta": 100,
	"n_poles_n_vehicles_factor": 0.2,

	"hub": True,
	"hub_zone_policy": "manual",
	"hub_zone": 387,

	"distributed_cps": True,
	"system_cps": True,
	"cps_placement_policy": "num_parkings",
	"cps_zones_percentage": 0.1,

	"battery_swap": False,
	"avg_reach_time": 1,
	"avg_service_time": 1,

	"n_workers": 1000,
	"relocation": False,

	"user_contribution": False,
	"willingness": 0,

}
