import json

from numpy import pi



def _experiment_to_seq(circuit):
    count = 0
    qubit_map = {}
    for bit in circuit.qubits:
        qubit_map[bit] = count
        count += 1
    ops = []
    meas = 0
    for instruction in circuit.data:
        inst = instruction[0]
        qubits = [qubit_map[bit] for bit in instruction[1]]
        if inst.name == 'rx':
            name = 'X'
        elif inst.name == 'ry':
            name = 'Y'
        elif inst.name == 'rz':
            name = 'Z'
        elif inst.name == 'measure':
            meas += 1
            continue
        elif inst.name == 'barrier':
            continue
        else:
            raise Exception("Operation '%s' outside of basis rx, ry" %
                            inst.name)
        exponent = inst.params[0] / pi
        # hack: split X into X**0.5 . X**0.5
        if name == 'X' and exponent == 1.0:
            ops.append((name, float(0.5), qubits))
            ops.append((name, float(0.5), qubits))
        else:
            # (op name, exponent, [qubit index])
            ops.append((name, float(exponent), qubits))
    if not meas:
        raise ValueError('Circuit must have at least one measurements.')
    return json.dumps(ops)


def circuit_to_KosakaQ(circuits, access_token, shots=4096):
    """Return a list of json payload strings for each experiment in a qobj

    The output json format of an experiment is defined as follows:
        [[op_string, gate_exponent, qubits]]

    which is a list of sequential quantum operations, each operation defined
    by:

    op_string: str that specifies the operation type, either "X","Y"
    gate_exponent: float that specifies the gate_exponent of the operation
    qubits: list of qubits where the operation acts on.
    """
    out_json = []
    if isinstance(circuits, list):
        if len(circuits) > 1:
            raise Exception
        circuits = circuits[0]
    seqs = _experiment_to_seq(circuits)
    out_dict = {
        'data': seqs,
        'access_token': access_token,
        'repetitions': shots,
        'no_qubits': circuits.num_qubits,
    }
    out_json.append(out_dict)
    return out_json