import random

from .basis import Erschrecke, Gehe, Renne, Schaue, Szene


class Spaziergang(Szene):
    """Läuft am unteren Rand herein, bemerkt die Zuschauer, erschrickt und rennt davon."""
    name, titel, reihenfolge = 'laufen', 'Spaziergang', 1

    def ablauf(self):
        self.x = self.aussen(-self.richtung)
        return [Gehe(bis=self.vom_rand(random.uniform(0.12, 0.22))),
                Schaue(1.9),
                Erschrecke(0.45, hoehe=30),
                Renne(zum='zurueck', tempo=2.6)]
