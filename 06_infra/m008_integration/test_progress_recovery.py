"""
## test_progress_recovery.py

## Descripción
Cubre avances consecutivos exclusivos, finalización y fallo de un cotejo sintético.

## Precondiciones
Linux y directorios persistentes de prueba; no usa ciencia ni lectores científicos.

## Resultados
Un contrato comprueba archivos independientes y diagnóstico conservado sin retry.

## Notas relevantes
Invoca sólo recovery_attempt con callbacks sintéticos; cero fits y builds.
=============================================================================
"""
from pathlib import Path
import pytest
import qualify_integration_gate as q
import verify_s02 as v


def test_progress_sequence(tmp_path, monkeypatch):
    import subprocess
    monkeypatch.setattr(subprocess, 'Popen', lambda *a, **k: pytest.fail('no child allowed'))
    root=tmp_path/'owner';(root/'local_state').mkdir(parents=True)
    parent=tmp_path/'outputs';parent.mkdir()
    timeouts=[];original=q.timed_call
    def timed(action, seconds):
        timeouts.append(seconds)
        return original(action, seconds)
    monkeypatch.setattr(q, 'timed_call', timed)
    for number, fail in ((3, False), (4, True)):
        def action(progress):
            progress('qualification')
            progress('science-evidence')
            if fail:
                raise RuntimeError('controlled diagnostic')
            return {'synthetic': True}
        if fail:
            with pytest.raises(RuntimeError, match='controlled diagnostic'):
                v.recovery_attempt(root,parent,'coder',number,'synthetic-resolution',action)
        else:
            result=v.recovery_attempt(root,parent,'coder',number,'synthetic-resolution',action)
            assert result['ok'] is True and result['fits_executed']==0
        marker=root/f'local_state/m008-s02-recovery-r{number}-coder.json'
        out=Path(q.read(marker)['output'])
        assert sorted(p.name for p in out.glob('progress*.json'))==['progress-0001.json','progress-0002.json']
        advances=[q.read(out/f'progress-{i:04d}.json') for i in (1,2)]
        assert [p['sequence'] for p in advances]==[1,2]
        assert [p['stage'] for p in advances]==['qualification','science-evidence']
        assert 0<=advances[0]['elapsed']<=advances[1]['elapsed']
        assert (out/'result.json').exists() is (not fail)
        assert (out/'failure.json').exists() is fail
        if fail:
            diagnostic=q.read(out/'failure.json')
            assert diagnostic['stage']=='science-evidence'
            assert diagnostic['error']=='RuntimeError'
            assert diagnostic['message']=='controlled diagnostic'
            assert 'RuntimeError: controlled diagnostic' in diagnostic['traceback']
            assert diagnostic['seconds']>=advances[1]['elapsed'] and diagnostic['pid']>0
        else:
            assert q.read(out/'result.json')==result
        preserved={p.name:p.read_bytes() for p in out.iterdir()}
        marker_bytes=marker.read_bytes()
        with pytest.raises(ValueError,match='reservation consumed'):
            v.recovery_attempt(root,parent,'coder',number,'synthetic-resolution',action)
        assert marker.read_bytes()==marker_bytes
        assert {p.name:p.read_bytes() for p in out.iterdir()}==preserved
    assert timeouts==[120,120]
