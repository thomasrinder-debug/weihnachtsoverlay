"""Alle Szenen. Jede Datei in diesem Ordner (außer basis.py) darf Szenen
enthalten; sie werden beim Start automatisch gefunden."""
import importlib
import pkgutil

from .basis import Szene


def finde_szenen():
    """{name: Klasse}, sortiert nach Szene.reihenfolge."""
    for modul in pkgutil.iter_modules(__path__):
        if modul.name != 'basis':
            importlib.import_module(f'{__name__}.{modul.name}')
    gefunden = [k for k in _alle_unterklassen(Szene) if k.name]
    gefunden.sort(key=lambda k: (k.reihenfolge, k.name))
    return {k.name: k for k in gefunden}


def _alle_unterklassen(klasse):
    for k in klasse.__subclasses__():
        yield k
        yield from _alle_unterklassen(k)
