from __future__ import print_function, division, absolute_import

import numpy as np

from openmdao.api import Group

from dymos import ODEOptions

from .log_atmosphere_comp import LogAtmosphereComp
from .launch_vehicle_2d_eom_comp import LaunchVehicle2DEOM


class LaunchVehicleODE(Group):

    ode_options = ODEOptions()

    ode_options.declare_time(units='s')

    ode_options.declare_state('x', rate_source='eom.xdot', units='m')
    ode_options.declare_state('y', rate_source='eom.ydot', targets=['atmos.y'], units='m')
    ode_options.declare_state('vx', rate_source='eom.vxdot', targets=['eom.vx'], units='m/s')
    ode_options.declare_state('vy', rate_source='eom.vydot', targets=['eom.vy'], units='m/s')
    ode_options.declare_state('m', rate_source='eom.mdot', targets=['eom.m'], units='kg')

    ode_options.declare_parameter('thrust', targets=['eom.thrust'], units='N')
    ode_options.declare_parameter('theta', targets=['eom.theta'], units='rad')
    ode_options.declare_parameter('Isp', targets=['eom.Isp'], units='s')

    def initialize(self):
        self.metadata.declare('num_nodes', types=int,
                              desc='Number of nodes to be evaluated in the RHS')

        self.metadata.declare('central_body', values=['earth', 'moon'], default='earth',
                              desc='The central graviational body for the launch vehicle.')

    def setup(self):
        nn = self.metadata['num_nodes']
        cb = self.metadata['central_body']

        if cb == 'earth':
            rho_ref = 1.225
            h_scale = 8.44E3
        elif cb == 'moon':
            rho_ref = 0.0
            h_scale = 1.0
        else:
            raise RuntimeError('Unrecognized value for central_body: {0}'.format(cb))

        self.add_subsystem('atmos',
                           LogAtmosphereComp(num_nodes=nn, rho_ref=rho_ref, h_scale=h_scale))

        self.add_subsystem('eom', LaunchVehicle2DEOM(num_nodes=nn, central_body=cb))

        self.connect('atmos.rho', 'eom.rho')