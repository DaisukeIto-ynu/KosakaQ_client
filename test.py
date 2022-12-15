# -*- coding: utf-8 -*-
"""
Created on Thu Dec  1 14:52:05 2022

@author: Daisuke Ito
"""

from qiskit.KosakaQ_client.kosakaq_provider import *
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister

provider = KosakaQProvider("8c8795d3fee73e69271bc8c9fc2e0c12e73e5879")
print(provider.backends(),"\n")
# backend = provider.get_backend("Rabi")
backend = provider.backends()[0]
print(backend.name,"\n")

#量子レジスタqを生成する。
q = QuantumRegister(1)

#古典レジスタcを生成する
c = ClassicalRegister(1)

#量子レジスタqと古典レジスタc間で量子回路を生成する。
qc = QuantumCircuit(q, c)
#1番目の量子ビットにHゲートをかける。
qc.h(q[0])
#1番目の量子ビットにXゲートをかける。
qc.x(q[0])

#1番目の量子ビットの測定値を1番目の古典ビットに渡す。
qc.measure(q[0], c[0])

qc.draw()

job = backend.run(qc)

print(job)