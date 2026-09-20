"""
## qualify_s04_repair.py

## Descripción
Cualifica el gate r2 con seis contratos nuevos de evidencia y despacho simulado.

## Precondiciones
Linux Python 3.11.16, D042 autorizado y padres persistentes existentes.
Fuentes nuevas completas; no ejecuta las regresiones correctivas pendientes.

## Resultados
Una reserva, seis IDs, log, JUnit e informe portable con identidades del gate.

## Notas relevantes
Sólo usa stdlib y fixtures desechables; cero fits, builds y procesos de producto.
Un fallo o resultado desconocido consume el intento y detiene sin repetir.
=============================================================================
"""
import copy
import json
import os
from pathlib import Path
import platform
import signal
import sqlite3
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock
import xml.etree.ElementTree as ET

import repair_s04 as gate

SCRATCH=None


def xml(path,names,bad=None):
    doc=ET.Element('testsuites');suite=ET.SubElement(doc,'testsuite')
    for n in names:
        case=ET.SubElement(suite,'testcase',name=n)
        if bad:ET.SubElement(case,bad)
    path.write_bytes(ET.tostring(doc))


class Contracts(unittest.TestCase):
    def setUp(self):
        self.work=Path(tempfile.mkdtemp(prefix='case-',dir=SCRATCH))

    def fixture(self):
        out=self.work/'result'
        for n in ('evidence','logs','snapshot'):(out/n).mkdir(parents=True)
        (out/'snapshot/source.py').write_text('fixture only\n')
        sources=gate.entries(out/'snapshot',['source.py']);w=gate.boundary.witness(out/'snapshot',sources)
        gate.save(out/'snapshot/manifest.json',{'base_commit':gate.BASE,'files':sources})
        gate.save(out/'started.json',{'invocation':'fixture','pid':10})
        gate.save(out/'dispatch-result.json',{'invocation':'fixture','pid':10,'status':'finished','exit':0,'profile':'linux','seconds':1})
        (out/'logs/dispatch.log').write_text('fixture dispatch\n');(out/'evidence/suite.log').write_text('fixture suite\n')
        xml(out/'evidence/junit.xml',gate.NAMES)
        with sqlite3.connect(out/'evidence/zero-fits.sqlite') as db:
            db.executescript('CREATE TABLE policy(cap INTEGER,mode TEXT);INSERT INTO policy VALUES(0,"qualification");CREATE TABLE calls(token TEXT);')
        receipt={'status':'passed','exit':0,'profile':'linux','invocation':'fixture','fits':0,
          'runtime':{'platform':'linux','python':'3.11.16'},'required':sorted(gate.TEST+'::'+n for n in gate.NAMES),
          'before':w,'after':w,'children':0,'descendants':0,
          'artifacts':{n:gate.sha(out/'evidence'/n) for n in ('suite.log','junit.xml','zero-fits.sqlite')}}
        gate.save(out/'evidence/receipt.json',receipt)
        result={'ok':True,'profile':'linux','invocation':'fixture','sources':sources,'fits':0,'seconds':1,
         'runtime':receipt['runtime'],'artifacts':{n:gate.sha(out/n) for n in ('dispatch-result.json','started.json','logs/dispatch.log',
           'evidence/receipt.json','evidence/junit.xml','evidence/suite.log','evidence/zero-fits.sqlite','snapshot/manifest.json')}}
        return out,sources,result

    def test_exact_ids_and_profiles(self):
        path=self.work/'junit.xml';xml(path,gate.NAMES);gate.junit(path,gate.NAMES)
        for names in ((),gate.NAMES[:-1],gate.NAMES+(gate.NAMES[0],)):
            xml(path,names)
            with self.assertRaises(ValueError):gate.junit(path,gate.NAMES)
        for bad in ('error','failure','skipped'):
            xml(path,gate.NAMES,bad)
            with self.assertRaises(ValueError):gate.junit(path,gate.NAMES)
        out,sources,r=self.fixture();gate.check_result(r,out,sources,'linux','fixture')
        with self.assertRaises(ValueError):gate.check_result(r,out,sources,'win32','fixture')
        with self.assertRaises(ValueError):gate.check_result(r,out,sources,'foreign','fixture')

    def test_sources_snapshots_and_completion(self):
        out,sources,r=self.fixture();gate.check_result(r,out,sources,'linux','fixture')
        for field,value in (('status','unknown'),('exit',1),('invocation','other'),('seconds',601)):
            path=out/'dispatch-result.json';before=path.read_bytes();d=gate.read(path);d[field]=value;path.write_text(json.dumps(d))
            with self.assertRaises(ValueError):gate.check_result(r,out,sources,'linux','fixture')
            path.write_bytes(before)
        (out/'snapshot/source.py').write_text('changed\n')
        with self.assertRaises(ValueError):gate.check_result(r,out,sources,'linux','fixture')

    def test_tamper_and_missing_rejected(self):
        out,sources,r=self.fixture();path=out/'evidence/suite.log';before=path.read_bytes()
        path.write_text('tampered')
        with self.assertRaises(ValueError):gate.check_result(r,out,sources,'linux','fixture')
        path.unlink()
        with self.assertRaises(ValueError):gate.check_result(r,out,sources,'linux','fixture')
        target=self.work/'target';target.write_bytes(before);path.symlink_to(target)
        with self.assertRaises(ValueError):gate.check_result(r,out,sources,'linux','fixture')
        with self.assertRaises(ValueError):gate.artifacts(out,{'../target':'0'*64})

    def test_reservation_failure_and_unknown(self):
        root=self.work/'repo';(root/'local_state').mkdir(parents=True);parent=self.work/'external';parent.mkdir()
        out,token=gate.reserve(root,parent,'linux')
        with self.assertRaises(ValueError):gate.reserve(root,parent,'linux')
        with self.assertRaises(ValueError):gate.order(root,'win32')
        gate.save(out/'evidence/result.json',{'ok':False,'invocation':token})
        with self.assertRaises(ValueError):gate.order(root,'win32')
        for n in ('scratch','logs'):self.assertEqual(list((out/n).iterdir()),[])
        with self.assertRaises(ValueError):gate.reserve(root,root,'coder')

    def test_dispatch_boundary_and_stop(self):
        # Exercise the maintained launch/wait/preservation path using a process double.
        for mode in ('pass','fail','timeout','interrupt'):
            out=self.work/mode;(out/'logs').mkdir(parents=True)
            class Process:
                pid=42
                def wait(self,timeout):
                    if mode=='timeout':raise subprocess.TimeoutExpired('fixture',timeout)
                    if mode=='interrupt':raise KeyboardInterrupt()
                    return 0 if mode=='pass' else 1
            with mock.patch.object(subprocess,'Popen',return_value=Process()) as spawn:
                r=gate.launch(['fixture-no-execution'],out,'fixture','linux',seconds=1)
            self.assertEqual(spawn.call_count,1)
            self.assertEqual(r['status'],'unknown' if mode in ('timeout','interrupt') else 'finished')
            self.assertTrue((out/'started.json').exists());self.assertTrue((out/'logs/dispatch.log').exists())
            root=out/'repo';(root/'local_state').mkdir(parents=True)
            gate.save(gate.marker(root,'linux'),{'output':str(out),'invocation':'fixture'})
            (out/'evidence').mkdir()
            gate.save(out/'evidence/result.json',{'ok':mode=='pass','invocation':'fixture'})
            if mode=='pass':gate.order(root,'win32')
            else:
                with self.assertRaises(ValueError):gate.order(root,'win32')

    def test_phases_and_no_suite_reexecution(self):
        root=self.work/'repo';(root/'local_state').mkdir(parents=True);(root/'05_governance').mkdir()
        ledger=root/'05_governance/ledger.jsonl';ledger.write_text(json.dumps({'slice':'M008-S04','round':2,'ev':'prompt'})+'\n')
        parent=self.work/'external';parent.mkdir()
        with mock.patch.object(subprocess,'Popen',side_effect=AssertionError('no process')),mock.patch.object(os,'system',side_effect=AssertionError('no process')):
            self.assertEqual(gate.phase_next(root),'coder');gate.admitted(root,'coder')
            out,token=gate.reserve(root,parent,'coder')
            with self.assertRaises(ValueError):gate.phase_next(root)
            gate.save(out/'evidence/result.json',{'ok':True,'invocation':token})
            self.assertEqual(gate.phase_next(root),'official')
            with self.assertRaises(ValueError):gate.admitted(root,'official')
            ledger.write_text(ledger.read_text()+json.dumps({'slice':'M008-S04','round':2,'ev':'coded'})+'\n')
            gate.admitted(root,'official');gate.reserve(root,parent,'official')
            with self.assertRaises(ValueError):gate.phase_next(root)
            gate.headers(gate.ROOT);gate.historical(gate.ROOT)
        self.assertFalse(any(n in sys.modules for n in ('numpy','sklearn','rasterio','science_worker','verify_s04','verify_s02')))


class Results(unittest.TextTestResult):
    def __init__(self,*a):super().__init__(*a);self.records=[];self.unknown=False
    def addSuccess(self,t):super().addSuccess(t);self.records.append((t._testMethodName,None))
    def addFailure(self,t,e):super().addFailure(t,e);self.records.append((t._testMethodName,'failure'))
    def addError(self,t,e):
        super().addError(t,e);self.records.append((t._testMethodName,'error'));self.unknown |= issubclass(e[0],(TimeoutError,KeyboardInterrupt))
    def addSkip(self,t,r):super().addSkip(t,r);self.records.append((t._testMethodName,'skipped'))


def main():
    global SCRATCH
    gate.require(sys.platform=='linux' and platform.python_version()=='3.11.16','fixed runtime')
    gate.require(not (gate.ROOT/gate.QUAL).exists(),'report exists')
    settings=gate.read(gate.ROOT/'local_state/m008-s04-r2-config.json')
    out,token=gate.reserve(gate.ROOT,settings['linux_parent'],'qualification');SCRATCH=out/'scratch'
    sources=gate.entries(gate.ROOT,gate.NEW);start=time.monotonic();result=None;error=None
    def deadline(*args):raise TimeoutError('qualification deadline')
    signal.signal(signal.SIGALRM,deadline);signal.setitimer(signal.ITIMER_REAL,180)
    with (out/'logs/suite.log').open('x',encoding='utf-8') as log:
        try:
            gate.require(set(unittest.defaultTestLoader.getTestCaseNames(Contracts))==set(gate.QNAMES),'discovery')
            result=unittest.TextTestRunner(stream=log,verbosity=2,failfast=True,resultclass=Results).run(unittest.TestSuite(Contracts(n) for n in gate.QNAMES))
        except BaseException as exc:error=type(exc).__name__;log.write(str(exc)+'\n')
        finally:signal.setitimer(signal.ITIMER_REAL,0)
    doc=ET.Element('testsuites');suite=ET.SubElement(doc,'testsuite')
    for name,bad in result.records if result else []:
        case=ET.SubElement(suite,'testcase',name=name)
        if bad:ET.SubElement(case,bad)
    (out/'evidence/junit.xml').write_bytes(ET.tostring(doc,encoding='utf-8',xml_declaration=True))
    ok=error is None and result is not None and result.wasSuccessful() and result.testsRun==6 and not result.skipped
    ok=ok and sources==gate.entries(gate.ROOT,gate.NEW) and gate.size(out)<=64*1024**2
    report={'ok':bool(ok),'status':'passed' if ok else ('unknown' if error in ('TimeoutError','KeyboardInterrupt') or (result is not None and result.unknown) else 'failed'),'invocation':token,'tests':result.testsRun if result else 0,'fits':0,
      'sources':sources,'seconds':round(time.monotonic()-start,3),'error':error,
      'artifacts':{n:gate.sha(out/n) for n in ('logs/suite.log','evidence/junit.xml')},'size_final':gate.size(out),
      'rss_peak':'unknown','scratch_peak':'unknown','tokens':'unknown'}
    gate.save(out/'evidence/result.json',report);gate.save(gate.ROOT/gate.QUAL,report)
    print(json.dumps({k:report[k] for k in ('ok','status','invocation','tests','fits','seconds')}));return 0 if ok else 1

if __name__=='__main__':raise SystemExit(main())
