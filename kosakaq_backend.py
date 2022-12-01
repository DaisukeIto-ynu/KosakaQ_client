# -*- coding: utf-8 -*-
"""
Created on Thu Nov 17 15:00:00 2022

@author: Yokohama National University, Kosaka Lab
"""
import warnings

import requests

from qiskit import qobj as qobj_mod
from qiskit.circuit.parameter import Parameter
from qiskit.circuit.library import IGate, XGate, YGate, ZGate, HGate, SGate, SdgGate, SXGate, SXdgGate, SYGate, SYdgGate
from qiskit.circuit.measure import Measure
from qiskit.providers import BackendV2 as Backend
from qiskit.providers import Options
from qiskit.transpiler import Target
from qiskit.providers.models import BackendConfiguration
from qiskit.exceptions import QiskitError

from . import kosakaq_job
from . import circuit_to_kosakaq

class KosakaQBackend(Backend):

    def __init__(self, provider,name,):
        super().__init__(provider=provider, name=name)
        self.url = 'https://gateway.aqt.eu/marmot/lint'
        self._configuration = BackendConfiguration.from_dict({
            'backend_name': 'aqt_innsbruck',
            'backend_version': '0.0.1',
            'url': self.url,
            'simulator': False,
            'local': False,
            'coupling_map': None,
            'description': 'Kosakaq Diamond device',
            'basis_gates': ['rx', 'ry', 'rz'],
            'memory': False,
            'n_qubits': 4,
            'conditional': False,
            'max_shots': 4096,
            'max_experiments': 1,
            'open_pulse': False,
            'gates': [
                {
                    'name': 'TODO',
                    'parameters': [],
                    'qasm_def': 'TODO'
                }
            ]
        })
        self._target = Target(num_qubits=4)
        theta = Parameter('θ')
        phi = Parameter('ϕ')
        lam = Parameter('λ')
        self._target.add_instruction(RXGate(theta))
        self._target.add_instruction(RYGate(theta))
        self._target.add_instruction(RZGate(lam))
        self._target.add_instruction(RGate(theta, phi))
        self._target.add_instruction(RXXGate(theta))
        self._target.add_instruction(Measure())
        self.options.set_validator("shots", (1, 200))

    def configuration(self):
        warnings.warn("The configuration() method is deprecated and will be removed in a "
                      "future release. Instead you should access these attributes directly "
                      "off the object or via the .target attribute. You can refer to qiskit "
                      "backend interface transition guide for the exact changes: "
                      "https://qiskit.org/documentation/apidoc/providers.html#backendv1-backendv2",
                      DeprecationWarning)
        return self._configuration

    def properties(self):
        warnings.warn("The properties() method is deprecated and will be removed in a "
                      "future release. Instead you should access these attributes directly "
                      "off the object or via the .target attribute. You can refer to qiskit "
                      "backend interface transition guide for the exact changes: "
                      "https://qiskit.org/documentation/apidoc/providers.html#backendv1-backendv2",
                      DeprecationWarning)

    @property
    def max_circuits(self):
        return 1

    @property
    def target(self):
        return self._target

    @classmethod
    def _default_options(cls):
        return Options(shots=100)

    def run(self, circuit, **kwargs):
        if isinstance(circuit, qobj_mod.PulseQobj):
            raise QiskitError("Pulse jobs are not accepted")
        for kwarg in kwargs:
            if kwarg != 'shots':
                warnings.warn(
                    "Option %s is not used by this backend" % kwarg,
                    UserWarning, stacklevel=2)
        out_shots = kwargs.get('shots', self.options.shots)
        if out_shots > self.configuration().max_shots:
            raise ValueError('Number of shots is larger than maximum '
                             'number of shots')
        kosakaq_json = circuit_to_kosakaq.circuit_to_kosakaq(
            circuit, self._provider.access_token, shots=out_shots)[0]
        header = {
            "Ocp-Apim-Subscription-Key": self._provider.access_token,
            "SDK": "qiskit"
        }
        res = requests.put(self.url, data=kosakaq_json, headers=header)
        res.raise_for_status()
        response = res.json()
        if 'id' not in response:
            raise Exception
        job = kosakaq_job.AQTJob(self, response['id'], qobj=circuit)
        return job