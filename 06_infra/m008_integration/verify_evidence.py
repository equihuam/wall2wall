"""
## verify_evidence.py

## Descripción
Valida JUnit e identidades de un recibo de preparación y presupuestos previos.

## Precondiciones
Fuentes inventariadas, runtime fijo y evidencia externa persistente.

## Resultados
Rechaza identidades o contratos incompletos; conserva el intento sin reintentos.

## Notas relevantes
Preparación de infraestructura sin fits; no acredita integración científica.
No mata procesos al vencer un plazo.
=============================================================================
"""

import json
from pathlib import Path
import xml.etree.ElementTree as ET


def check(receipt, invocation, entries, evidence, sha, ids):
    if (receipt.get('invocation') != invocation or receipt.get('status') != 'passed'
            or receipt.get('exit') != 0 or receipt.get('fits') != 0
            or receipt.get('before') != entries or receipt.get('after') != entries):
        raise ValueError('invalid or stale integration receipt')
    for name in ('suite.log','junit.xml'):
        if sha(Path(evidence)/name) != receipt['artifacts'][name]:
            raise ValueError('artifact changed')
    cases=ET.parse(Path(evidence)/'junit.xml').getroot().findall('.//testcase')
    if (len(cases)!=len(ids) or {x.attrib['name'] for x in cases}!={x.split('::')[-1] for x in ids}
            or any(x.find(tag) is not None for x in cases for tag in ('failure','error','skipped'))):
        raise ValueError('JUnit discovery differs')


def admit_fits(planned, remaining):
    if type(planned) is not int or type(remaining) is not int or planned < 0 or planned > remaining:
        raise ValueError('fit budget before launch')
    return remaining-planned
