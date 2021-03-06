import numpy as np
from matplotlib import pyplot
import pytest
from examples.ICMW_2012_case_1.setup import Setup
from examples.ICMW_2012_case_1.example import Simulation
from examples.ICMW_2012_case_1 import plotter
from PySDM.simulation.physics.constants import si


@pytest.mark.xfail
def test_velocity_field(plot=True):
    # Arrange
    setup = Setup()
    n_cell = np.prod(np.array(setup.grid))
    setup.n_sd_per_gridbox = 1 / n_cell
    setup.steps = [setup.eddy_period()]
    for key in setup.processes.keys():
        setup.processes[key] = False
    setup.processes["advection"] = True

    simulation = Simulation(setup, None)
    assert simulation.particles.n_sd == 1

    # Act

    # Plot

    # Assert