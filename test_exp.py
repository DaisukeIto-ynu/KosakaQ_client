# -*- coding: utf-8 -*-
"""
Created on Thu Dec  1 14:52:05 2022

@author: Daisuke Ito
"""

from kosakaq_experiments.Red_calibration import *
from kosakaq_experiments.Rabi_calibration import *
from kosakaq_experiments.ODMR_calibration import *

from kosakaq_provider import *
import pprint


provider = KosakaQProvider("8c8795d3fee73e69271bc8c9fc2e0c12e73e5879")
print(provider.backends(),"\n")
# backend = provider.get_backend("Rabi")
backend = provider.backends()[0]
print(backend.name,"\n")

# # PLE
# PLE = Red_calibration(backend)
# job_PLE = PLE.run("all")


# # Rabi
# Rabi = Rabi_calibration(backend)
# job_Rabi = Rabi.run(0,10000,0.002)


# ODMR
ODMR = ODMR_calibration(backend)
job_ODMR = ODMR.run(111,120)

# result = job_PLE.result()
# pprint.pprint(result)
