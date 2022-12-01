import json



def _experiment_to_seq(circuit):
    """
    Use with two or more qubits
    
    count = 0
    qubit_map = {}
    for bit in circuit.qubits:
        qubit_map[bit] = count
        count += 1
    """
    if circuit.qubits >= 2:
        raise Exception("Only one qubit can be used")
    ops = []
    meas = 0
    for instruction in circuit.data:
        inst = instruction[0]
        """
        Use with two or more qubits
        
        qubits = [qubit_map[bit] for bit in instruction[1]]
        """
        if inst.name == 'i':
            name = 'I'
        elif inst.name == 'x':
            name = 'X'
        elif inst.name == 'y':
            name = 'Y'
        elif inst.name == 'z':
            name = 'Z'
        elif inst.name == 'h':
            name = 'H'
        elif inst.name == 's':
            name = 'S'
        elif inst.name == 'sdg':
            name = 'Sdg'
        elif inst.name == 'sx':
            name = 'SX'
        elif inst.name == 'sxdg':
            name = 'SXdg'
        #elif inst.name == 'sy':
        #   name = 'SY'
        #elif inst.name == 'sydg':
        #   name = 'SYdg'
        elif inst.name == 'measure':
            meas += 1
            continue
        elif inst.name == 'barrier':
            continue
        else:
            raise Exception("Operation '%s' outside of basis i, x, y, z, h, s, sdg, sx, sxdg, measure" %inst.name)
        """
        use with xr gate 
        
        exponent = inst.params[0] / pi
        # hack: split X into X**0.5 . X**0.5
        if name == 'X' and exponent == 1.0:
            ops.append((name, float(0.5), qubits))
            ops.append((name, float(0.5), qubits))
        else:
        """
        """
        use with two or more qubits
        
            # (op name, exponent, [qubit index])
            ops.append((name, float(exponent), qubits))
        """
        ops.append(name)
        
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