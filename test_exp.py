# -*- coding: utf-8 -*-
"""
Created on Thu Dec  1 14:52:05 2022

@author: Daisuke Ito
"""

from kosakaq_experiments.Red_calibration import *
from kosakaq_provider import *


provider = KosakaQProvider("8c8795d3fee73e69271bc8c9fc2e0c12e73e5879")
print(provider.backends(),"\n")
# backend = provider.get_backend("Rabi")
backend = provider.backends()[0]
print(backend.name,"\n")

PLE = Red_calibration(backend)

job = PLE.run("all")

