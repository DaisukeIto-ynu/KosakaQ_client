# -*- coding: utf-8 -*-
"""
Created on Thu Dec  1 14:52:05 2022

@author: Daisuke Ito
"""

from qiskit.KosakaQ_client.kosakaq_provider import *

provider = KosakaQProvider("8c8795d3fee73e69271bc8c9fc2e0c12e73e5879")
print(provider.backends())
backend = provider.get_backend("Rabi")
print(backend)