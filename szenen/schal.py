import math
import random

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QColor, QPainterPath

from zeichnen.figur import Pose
from zeichnen.figuren import Wichtel, augen
from zeichnen.grundlagen import (GOLD, GOLD_HELL, KEIN_PINSEL, KEIN_STIFT, ROT_DUNKEL, ROT_HELL, blinzeln, kreis,
                                 linear, radial, stift)

from .basis import Gehe, Gleite, Jeweils, Mit, Setze, Stehe, Szene, Tu, Wandel, Warte

STREIFEN = [QColor('#D3172E'), QColor('#FAFAFA'), QColor('#22834C'), QColor('#FAFAFA')]
BREITE = 72          # Wolltonne, Einheiten


class Schal(Szene):
    """Ein Wichtel zieht einen Schal aus dem Ärmel, immer weiter, wickelt sich hinein und
    steht schließlich als Wolltonne mit winzigen Füßen da. Seine Mütze landet obenauf und
    versinkt langsam in den Wicklungen. Dann trippelt die Tonne davon."""
    name, titel, reihenfolge = 'schal', 'Schal ohne Ende', 36

    def vorbereiten(self):
        self.zeige_figur = False
        self.w = self.dazu('w', Wichtel, groesse=0.6, muetze=True)
        self.w.richtung = self.richtung
        self.w.tempo = self.tempo * 0.8
        self.haufen = 0.0       # Schal am Boden (0..1)
        self.ziehen = False
        self.tonne = 0.0        # Höhe der Wicklung in Einheiten
        self.muetze = None      # winzige Mütze: [x, y, vy, versunken]
        self.augen_auf = False
        self.wackel = 0.0

    def ablauf(self):
        r = self.richtung
        ziehen = lambda d, u: Pose(arm_v=-70 + 40 * math.sin(u * 9), arm_h=-30 - 30 * math.sin(u * 9),  # noqa: E731
                                   arm_v_x=10, kopf_vorn=u > 1.5, sorge=0.3 if u > 1.5 else 0,
                                   auge_zu=blinzeln(d.t))

        def drehen(sz, u):
            sz.w.richtung = r if (u * 7) % 2 < 1 else -r
            sz.w.pose = Pose(arm_v=-150, arm_h=-150, mund_offen=True)
            sz.tonne = min(130, u / 1.8 * 130)
            sz.haufen = max(0.0, 1 - u / 1.8)
            if sz.tonne > 95 and sz.w.muetze:
                sz.w.muetze = False
                sz.muetze = [sz.w.x, sz.boden - 150 * sz.s, -260 * sz.s, 0.0]

        return [
            Mit('w', Gehe(bis=self.vom_rand(random.uniform(0.07, 0.1)))),
            Mit('w', Stehe(0.8)),
            Setze(ziehen=True),
            Jeweils(2.6, lambda sz, u: (setattr(sz, 'haufen', min(1.0, u / 2.4)),
                                         setattr(sz.w, 'pose', ziehen(sz.w, u)))),
            Setze(ziehen=False),
            Mit('w', Stehe(0.7, Pose(kopf_vorn=True, sorge=0.8, blick_y=0.8))),
            Jeweils(1.8, drehen),
            Mit('w', Setze(richtung=r, pose=Pose())),
            Warte(2.2),
            Setze(augen_auf=True), Warte(0.35), Setze(augen_auf=False), Warte(0.3),
            Mit('w', Gehe(bis=self.aussen(-r), tempo=0.7,
                          haltung=lambda p, d: Pose(bein_v=p.bein_v * 1.5, bein_h=p.bein_h * 1.5))),
        ]

    def schreck_ablauf(self):
        self.nebenbei.clear()
        w = self.w
        if not w.figur_sichtbar():
            return []
        if self.tonne > 60:
            seite = w.naechster_rand()
            return [Setze(augen_auf=True), Warte(0.3),
                    Mit('w', Gleite(self.aussen(seite) + seite * 80 * self.s, 0.7,
                                    Pose(bein_v=-30, bein_h=30)))]
        return [Mit('w', Setze(striche=True)), Setze(haufen=0.0, ziehen=False),
                Mit('w', Stehe(0.25, Pose(kopf_vorn=True, schreck=1.0, arm_v=-120, arm_h=-110))),
                Mit('w', Setze(striche=False)), Mit('w', Gleite(self.aussen(w.naechster_rand()), 0.8,
                                                                 Pose(bein_v=-30, bein_h=30)))]

    def weiter(self, dt):
        m = self.muetze
        if m:
            s = self.s
            oben = self.boden - (self.tonne + 4) * s
            m[0] = self.w.x
            if m[3] == 0 and (m[2] < 0 or m[1] < oben):
                m[2] += 900 * s * dt
                m[1] += m[2] * dt
                if m[1] >= oben and m[2] > 0:
                    m[1], m[3] = oben, 0.001
            elif m[3] > 0:
                m[3] = min(1.0, m[3] + dt / 2.0)
                m[1] = oben + 12 * s * m[3]
        self.wackel = math.sin(self.t * 9) * 4 if self.tonne > 60 and self.w.pose.bein_v else 0.0

    def zeichne_hinten(self, p):
        s, w = self.s, self.w
        if self.haufen > 0:
            # Schalberg am Boden neben ihm
            x = w.x + w.richtung * 40 * s
            for i in range(int(2 + self.haufen * 6)):
                p.setBrush(STREIFEN[i % 4])
                p.drawEllipse(QPointF(x + math.sin(i * 2.1) * 12 * s, self.boden - (5 + i * 3.5) * s),
                              (22 - i) * s, 6 * s)
            if self.ziehen:
                hx, hy = w.trafo().map(QPointF(8, -66)).x(), w.trafo().map(QPointF(8, -66)).y()
                pfad = QPainterPath()
                pfad.moveTo(hx, hy)
                pfad.quadTo(x, hy + 10 * s, x, self.boden - (8 + self.haufen * 20) * s)
                stil = stift(STREIFEN[0], 5 * s)
                p.setPen(stil)
                p.setBrush(KEIN_PINSEL)
                p.drawPath(pfad)
                p.setPen(KEIN_STIFT)

    def zeichne_vorn(self, p):
        s, w = self.s, self.w
        if self.tonne > 0 and w.zeige_figur:
            p.save()
            p.translate(w.x, self.boden - 8 * s)
            p.rotate(self.wackel)
            p.scale(s, s)
            h = self.tonne
            p.setClipRect(QRectF(-BREITE, -h - 4, BREITE * 2, h + 4))
            for i in range(int(h / 9) + 1):
                y = -i * 9
                p.setBrush(linear(-BREITE / 2, 0, BREITE / 2, 0, STREIFEN[i % 4].lighter(110),
                                  STREIFEN[i % 4].darker(135)))
                p.drawRoundedRect(QRectF(-BREITE / 2 - (i % 2) * 2, y - 11, BREITE + (i % 2) * 4, 12), 6, 6)
            p.setClipping(False)
            if self.augen_auf:
                p.setBrush(QColor(30, 20, 20))
                p.drawRoundedRect(QRectF(-20, -h * 0.72 - 7, 40, 14), 7, 7)
                augen(p, (-8, 8), -h * 0.72, 4.5, 5, Pose(schreck=1.0, kopf_vorn=True))
            p.restore()
        m = self.muetze
        if m and w.zeige_figur:
            p.save()
            p.translate(m[0], m[1])
            p.scale(s * 0.45, s * 0.45)
            p.setClipRect(QRectF(-60, -200, 120, 200 - 40 * m[3] if m[3] else 400))
            kegel = QPainterPath()
            kegel.moveTo(-22, 0)
            kegel.lineTo(22, 0)
            kegel.lineTo(-6, -48)
            kegel.closeSubpath()
            p.setBrush(linear(-20, -48, 20, 0, ROT_HELL, ROT_DUNKEL))
            p.drawPath(kegel)
            p.setBrush(radial(-7, -50, 6, GOLD_HELL, GOLD))
            kreis(p, -6, -50, 5)
            p.restore()

    def grenzen_extra(self):
        s, w = self.s, self.w
        k = QRectF(w.x - 90 * s, self.boden - 160 * s, 180 * s, 160 * s)
        if self.muetze:
            k = k.united(QRectF(self.muetze[0] - 20 * s, self.muetze[1] - 30 * s, 40 * s, 40 * s))
        return k if w.zeige_figur else QRectF()
