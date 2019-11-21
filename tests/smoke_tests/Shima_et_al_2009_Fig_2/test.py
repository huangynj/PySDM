"""
Created at 08.08.2019

@author: Piotr Bartman
@author: Sylwester Arabas
"""

import copy

from PySDM.backends.default import Default
from PySDM.simulation.particles import Particles
from PySDM.simulation.dynamics.coalescence.algorithms.sdm import SDM
from PySDM.simulation.initialisation.spectral_discretisation import constant_multiplicity
from PySDM.simulation.dynamics.coalescence.kernels.golovin import Golovin
from PySDM.simulation.initialisation.spectra import Exponential


backend = Default


# TODO seed
def test():
    # Arrange
    x_min = 4.186e-15
    x_max = 4.186e-12
    n_sd = 2 ** 13
    steps = [0, 30, 60]
    X0 = 4 / 3 * 3.14 * 30.531e-6 ** 3
    n_part = 2 ** 23  # [m-3]
    dv = 1e6  # [m3]
    dt = 1  # [s]
    norm_factor = n_part * dv

    kernel = Golovin(b=1.5e3)  # [s-1]
    spectrum = Exponential(norm_factor=norm_factor, scale=X0)
    particles = Particles(n_sd=n_sd, grid=(), size=(), dt=dt, backend=backend)
    particles.set_dv(dv)
    x, n = constant_multiplicity(n_sd, spectrum, (x_min, x_max))
    particles.create_state_0d(n=n, extensive={'x': x}, intensive={})
    particles.add_dynamics(SDM, (kernel,))

    states = {}

    # Act
    for step in steps:
        particles.run(step - particles.n_steps)
        states[particles.n_steps] = copy.deepcopy(particles.state)

    # Assert
    x_max = 0
    for state in states.values():
        assert x_max < state.max('x')
        x_max = state.max('x')

