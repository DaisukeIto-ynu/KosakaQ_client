# -*- coding: utf-8 -*-
"""
Created on Thu Nov 17 15:00:00 2022

@author: Yokohama National University, Kosaka Lab
"""
import time

import requests
from qiskit.providers import JobV1
from qiskit.providers import JobError
from qiskit.providers import JobTimeoutError
from qiskit.providers.jobstatus import JobStatus
from qiskit.result import Result


class KosakaQJob(JobV1):
    def __init__(self, backend, job_id, access_token=None, qobj=None):
        """Initialize a job instance.
        Parameters:
            backend (BaseBackend): Backend that job was executed on.
            job_id (str): The unique job ID.
            access_token (str): The AQT access token.
            qobj (Qobj): Quantum object, if any.
        """
        super().__init__(backend, job_id)
        self._backend = backend
        self.access_token = access_token
        self.qobj = qobj
        self._job_id = job_id
        self.memory_mapping = self._build_memory_mapping()

    def _wait_for_result(self, timeout=None, wait=5):
        if wait < 5:
            raise JobError('Wait time must be 5 or more')
        start_time = time.time()
        result = None
        header = {
            "Authorization": "Token "+self.access_token
        }
        while True:
            elapsed = time.time() - start_time
            if timeout and elapsed >= timeout:
                raise JobTimeoutError('Timed out waiting for result')
            result = requests.get(
                self._backend.url + ('/job/'),
                headers=header,
                params={"jobid": self._job_id}
            ).json()
            if result['joblist'][0]['jobstatus'] == 'FINISHED':
                break
            if result['joblist'][0]['jobstatus'] == 'ERROR':
                raise JobError('API returned error:\n' + str(result))
            if result['joblist'][0]['jobstatus'] == 'QUEUED':        
                pass
            time.sleep(wait)
        return result

    def _build_memory_mapping(self):
        qu2cl = {}
        qubit_map = {}
        count = 0

        # If a list of quantum circuits use the first element
        # since we only can have a maximum of a single
        # circuit per job.
        if isinstance(self.qobj, list):
            self.qobj = self.qobj[0]

        for bit in self.qobj.qubits:
            qubit_map[bit] = count
            count += 1
        if count >= 2:
            raise JobError('This system is not accepted for 2 or more qubits.')
        clbit_map = {}
        count = 0
        for bit in self.qobj.clbits:
            clbit_map[bit] = count
            count += 1
        for instruction in self.qobj.data:
            if instruction[0].name == 'measure':
                for index, qubit in enumerate(instruction[1]):
                    qu2cl[qubit_map[qubit]] = clbit_map[instruction[2][index]]
        return qu2cl

    def result(self,
               timeout=None,
               wait=5):
        """Get the result data of a circuit.
        Parameters:
            timeout (float): A timeout for trying to get the counts.
            wait (float): A specified wait time between counts retrival
                          attempts.
        Returns:
            Result: Result object.
        """
        result = self._wait_for_result(timeout, wait)
        results = [
            {
                'success': True,
                'shots': result['qobjlist'][0][0]['shots'],
                'data': {'counts': {'0x0': result['qobjlist'][0][0]['result'][:3], '0x1': result['qobjlist'][0][0]['result'][4:7]}},
                'header': {'memory_slots': self.qobj.num_clbits,
                           'name': self.qobj.name,
                           'metadata': self.qobj.metadata}
            }]
        qobj_id = id(self.qobj)

        return Result.from_dict({
            'results': results,
            'backend_name': self._backend.name,
            'backend_version': '0.0.1',
            'qobj_id': qobj_id,
            'success': True,
            'job_id': self._job_id,
        })

    def get_counts(self, circuit=None, timeout=None, wait=5):
        """Get the histogram data of a measured circuit.
        Parameters:
            circuit (str or QuantumCircuit or int or None): The index of the circuit.
            timeout (float): A timeout for trying to get the counts.
            wait (float): A specified wait time between counts retrival
                          attempts.
        Returns:
            dict: Dictionary of string : int key-value pairs.
        """
        return self.result(timeout=timeout, wait=wait).get_counts(circuit)

    def status(self):
        """Query for the job status.
        """
        header = {
            "Authorization": "Token "+self.access_token
        }
        result = requests.get(
            self._backend.url + ('/job/'),
            headers=header,
            params={"jobid": self._job_id}
        )
        code = result.status_code

        if code == 100:
            status = JobStatus.RUNNING
        elif code == 200:
            status = JobStatus.DONE
        elif code in [201, 202]:
            status = JobStatus.INITIALIZING
        else:
            status = JobStatus.ERROR
        return status

    def submit(self):
        """Submits a job for execution.
        :class:`.AQTJob` does not support standalone submission of a job
        object. This can not be called and the Job is only submitted via
        the ``run()`` method of the backend
        :raises NotImplementedError: This method does not support calling
            ``submit()``
        """
        raise NotImplementedError
    
    def backend(self):
        return self._backend
