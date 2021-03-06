"""
Created at 25.09.2019

@author: Piotr Bartman
@author: Michael Olesik
@author: Sylwester Arabas
"""

import numpy as np

from PySDM.simulation.particles import Particles as Particles
from PySDM.simulation.dynamics.advection import Advection
from PySDM.simulation.dynamics.condensation import Condensation
from PySDM.simulation.dynamics.eulerian_advection import EulerianAdvection
from PySDM.simulation.dynamics.coalescence.algorithms.sdm import SDM
from PySDM.simulation.initialisation import spatial_sampling, spectral_sampling
from PySDM.simulation.environment.moist_eulerian_2d_kinematic import MoistEulerian2DKinematic

from examples.ICMW_2012_case_1.setup import Setup
from examples.ICMW_2012_case_1.storage import Storage


class DummyController:
    panic = False

    def set_percent(self, value): print(f"{100 * value:.1f}%")

    def __enter__(*_): pass

    def __exit__(*_): pass


class Simulation:
    def __init__(self, setup, storage):
        self.setup = setup
        self.storage = storage

    def run(self, controller=DummyController()):
        self.tmp = None # TODO!
        self.particles = Particles(n_sd=self.setup.n_sd, dt=self.setup.dt, backend=self.setup.backend)
        self.particles.set_mesh(grid=self.setup.grid, size=self.setup.size)
        self.particles.set_environment(MoistEulerian2DKinematic, {
            "stream_function": self.setup.stream_function,
            "field_values": self.setup.field_values,
            "rhod_of": self.setup.rhod
        })

        self.particles.create_state_2d(
            extensive={},
            intensive={},
            spatial_discretisation=spatial_sampling.pseudorandom,
            spectral_discretisation=spectral_sampling.constant_multiplicity,
            spectrum_per_mass_of_dry_air=self.setup.spectrum_per_mass_of_dry_air,
            r_range=(self.setup.r_min, self.setup.r_max),
            kappa=self.setup.kappa
        )

        if self.setup.processes["condensation"]:
            self.particles.add_dynamic(Condensation, {"kappa": self.setup.kappa})
        if self.setup.processes["advection"]:
            self.particles.add_dynamic(EulerianAdvection, {})
            self.particles.add_dynamic(Advection, {"scheme": 'FTBS'})
        if self.setup.processes["coalescence"]:
            self.particles.add_dynamic(SDM, {"kernel": self.setup.kernel})

        # TODO
        if self.storage is not None:
            self.storage.init(self.setup)

        with controller:
            for step in self.setup.steps:  # TODO: rename output_steps
                if controller.panic:
                    break

                for _ in range(step - self.particles.n_steps):

                    self.particles.run(1)

                self.store(self.particles, step)

                controller.set_percent(step / self.setup.steps[-1])

        return self.particles.stats

    def store(self, particles, step):
        backend = particles.backend
        eulerian_fields = particles.environment.eulerian_fields

        # allocations
        if self.tmp is None:  # TODO: move to constructor
            n_moments = 0
            for attr in self.setup.specs:
                for _ in self.setup.specs[attr]:
                    n_moments += 1
            self.moment_0 = backend.array(particles.mesh.n_cell, dtype=int)
            self.moments = backend.array((n_moments, particles.mesh.n_cell), dtype=float)
            self.tmp = np.empty(particles.mesh.n_cell)

        # store moments
        particles.state.moments(self.moment_0, self.moments, self.setup.specs)  # TODO: attr_range
        backend.download(self.moment_0, self.tmp)
        self.tmp /= particles.mesh.dv
        self.storage.save(self.tmp.reshape(self.setup.grid), step, "m0")

        i = 0
        for attr in self.setup.specs:
            for k in self.setup.specs[attr]:
                backend.download(self.moments[i], self.tmp)  # TODO: [i] will not work
                self.tmp /= particles.mesh.dv
                self.storage.save(self.tmp.reshape(self.setup.grid), step, f"{attr}_m{k}")
                i += 1

        # store advected fields
        for key in eulerian_fields.mpdatas.keys():
            self.storage.save(eulerian_fields.mpdatas[key].curr.get(), step, key)

        # store auxiliary fields
        backend.download(particles.environment['RH'], self.tmp)
        self.storage.save(self.tmp.reshape(self.setup.grid), step, "RH")


def main():
    # with np.errstate(all='raise'):
    setup = Setup()
    storage = Storage()
    simulation = Simulation(setup, storage)
    simulation.run()


if __name__ == '__main__':
    main()
