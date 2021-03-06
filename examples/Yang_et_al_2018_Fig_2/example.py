"""
Created at 25.11.2019

@author: Michael Olesik
@author: Sylwester Arabas
"""

import numpy as np

from PySDM.simulation.particles import Particles as Particles
from PySDM.simulation.dynamics.condensation import Condensation
from PySDM.simulation.environment.moist_lagrangian_parcel_adiabatic import MoistLagrangianParcelAdiabatic
from PySDM.simulation.physics import formulae as phys
from examples.Yang_et_al_2018_Fig_2.setup import Setup
from PySDM.simulation.initialisation.r_wet_init import r_wet_init

# TODO: the q1 logic from PyCloudParcel?


class Simulation:
    def __init__(self, setup):

        self.particles = Particles(backend=setup.backend, n_sd=setup.n_sd, dt=setup.dt)
        self.particles.set_mesh_0d()
        self.particles.set_environment(MoistLagrangianParcelAdiabatic, {
            "mass_of_dry_air": setup.mass_of_dry_air,
            "p0": setup.p0,
            "q0": setup.q0,
            "T0": setup.T0,
            "w": setup.w,
            "z0": setup.z0
        })

        v_dry = phys.volume(radius=setup.r_dry)
        r_wet = r_wet_init(setup.r_dry, self.particles.environment, np.zeros_like(setup.n), setup.kappa)
        v_wet = phys.volume(radius=r_wet)
        self.particles.create_state_0d(n=setup.n, extensive={'dry volume': v_dry, 'volume': v_wet}, intensive={})
        self.particles.add_dynamic(Condensation, {"kappa": setup.kappa})

        self.n_steps = setup.n_steps

    # TODO: make it common with Arabas_and_Shima_2017
    def save(self, output):
        cell_id = 0
        volume = self.particles.state.get_backend_storage('volume')
        volume = self.particles.backend.to_ndarray(volume)
        output["r"].append(phys.radius(volume=volume))
        output["S"].append(self.particles.environment["RH"][cell_id] - 1)
        output["qv"].append(self.particles.environment["qv"][cell_id])
        output["T"].append(self.particles.environment["T"][cell_id])
        output["z"].append(self.particles.environment["z"][cell_id])
        output["t"].append(self.particles.environment["t"][cell_id])

    def run(self):
        output = {"r": [], "S": [], "z": [], "t": [], "qv": [], "T": []}

        self.save(output)
        for step in range(self.n_steps):
            self.particles.run(1)
            self.save(output)

        return output


if __name__ == '__main__':
    Simulation(setup=Setup()).run()
