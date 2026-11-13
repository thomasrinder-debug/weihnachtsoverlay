import math

from PyQt6.QtCore import QRectF

from zeichnen.figur import Pose
from zeichnen.grundlagen import KEIN_STIFT
from zeichnen.tiere import Schneeeule, ast_y, zeichne_ast, zeichne_einzelfeder

from .basis import Jeweils, Mit, Nebenbei, Setze, Stehe, Szene, Tu, Wandel, Warte, WarteNebenbei
from .tier_gemeinsam import FEDERN, Flug, wegfliegen

AST_L = 240          # Einheiten
EULE_G = 0.85


class DuenneAst(Szene):
    """Eine dicke Schneeeule landet auf einem dünnen Ast am Seitenrand, der sich tief durchbiegt.
    Zweimal hüpft sie näher an den Stamm, der Ast biegt sich trotzdem weiter. Erleichtert breitet
    sie die Flügel aus – da schnellt der Ast hoch und katapultiert sie kopfüber an die obere
    Bildkante, wo sie zerzaust hängen bleibt. Zum Schluss segelt eine einzelne Feder herab,
    und unter ihr biegt sich der Ast bis zum Anschlag."""
    name, titel, reihenfolge = 'tier_eule', 'Dünner Ast', 730

    def vorbereiten(self):
        self.zeige_figur = False
        self.seite = -self.richtung
        self.wand = self.geo.left() if self.seite < 0 else self.geo.right()
        self.dir = -self.seite
        self.ay = self.oben + self.geo.height() * 0.3
        self.bieg = 8.0
        self.schwing = 0.0
        self.deck = 0.0
        self.auf_ast = False
        self.pos = AST_L * 0.9
        self.feder = None
        o = self.o = self.dazu('o', Schneeeule, groesse=EULE_G, fluegel=0.0, flattern=0.0, zerzaust=0.0,
                               muede=0.0, fliegt=False)
        o.richtung = self.dir
        o.x, o.y = self.wand + self.dir * AST_L * 0.6 * self.s, self.oben - 150 * self.s

    def ast_punkt(self, pos):
        b = self.bieg + self.schwing
        return self.wand + self.dir * pos * self.s, self.ay + ast_y(pos, AST_L, b) * self.s

    def weiter(self, dt):
        o = self.o
        if self.auf_ast:
            o.x, o.y = self.ast_punkt(self.pos)
        if o.fliegt:
            o.fluegel, o.flattern = 0.75, 45 * math.sin(self.t * 26)
        if self.feder:
            fx, fy, ziel = self.feder
            zx, zy = self.ast_punkt(AST_L * 0.8)
            zy -= 4 * self.s
            fy = min(zy, fy + 150 * self.s * dt)
            rest = max(0.0, min(1.0, (zy - fy) / (120 * self.s)))
            fx = zx + math.sin(self.t * 3) * 30 * self.s * rest
            self.feder = (fx, fy, ziel)

    def hupf(self, nach):
        """Hüpfer der Eule auf dem Ast an die Stelle 'nach' (Einheiten von der Wand)."""
        def ziel(o):
            return self.ast_punkt(nach)
        return [Setze(auf_ast=False),
                Mit('o', Setze(richtung=-self.dir)),
                Mit('o', Flug(ziel, 0.32, hoehe=30, pose=Pose(sorge=1.0))),
                Setze(pos=nach, auf_ast=True)]

    def ablauf(self):
        d, s = self.dir, self.s
        knarren = lambda sz: sz.streue(*sz.ast_punkt(AST_L * 0.25), 6, [__import__('PyQt6.QtGui', fromlist=['QColor'])  # noqa: E731
                                       .QColor('#5A3E28')], tempo=60, dauer=0.6, r=(1.5, 3), schwer=True)
        return [
            Wandel(0.3, deck=1.0),
            Mit('o', Setze(fliegt=True)),
            Mit('o', Flug(lambda o: self.ast_punkt(self.pos), 0.8, hoehe=-40)),
            Mit('o', Setze(fliegt=False, fluegel=0.0, flattern=0.0)),
            Setze(auf_ast=True),
            Wandel(0.18, bieg=95.0),
            Wandel(0.2, bieg=80.0),
            Mit('o', Stehe(0.45, Pose(blick_y=1.0, schreck=0.6))),
            # 1. näher zum Stamm
            *self.hupf(AST_L * 0.6),
            Tu(knarren),
            Wandel(0.3, bieg=100.0),
            Mit('o', Stehe(0.45, lambda o, u: Pose(blick_x=-d * 0.0, blick_y=0.2, sorge=0.8,
                                                    auge_zu=0.2 < u < 0.3))),
            # 2. noch näher
            *self.hupf(AST_L * 0.3),
            Tu(knarren),
            Wandel(0.3, bieg=122.0),
            Mit('o', Stehe(0.35, Pose(blick_y=1.0, sorge=1.0))),
            # erleichtert – Pause – der Ast schnellt hoch
            Mit('o', Wandel(0.3, fluegel=1.0)),
            Mit('o', Stehe(0.7, Pose(auge_zu=True))),
            Setze(auf_ast=False),
            Wandel(0.07, bieg=-60.0),
            Nebenbei(Jeweils(1.6, lambda sz, u: setattr(sz, 'bieg', 10 - 70 * math.cos(u * 18) * math.exp(-u * 3)))),
            Mit('o', Setze(fluegel=0.0, zerzaust=1.0)),
            Tu(lambda sz: sz.streue(sz.o.x, sz.o.y - 50 * sz.s, 12, FEDERN, tempo=150, dauer=1.0, r=(3, 7))),
            Mit('o', Flug((self.wand + d * 70 * s, self.oben), 0.45, hoehe=60, neigung=540,
                          pose=Pose(schreck=1.0))),
            Mit('o', Setze(neigung=180.0)),
            Tu(lambda sz: sz.streue(sz.o.x, sz.oben + 8 * sz.s, 8, FEDERN, tempo=80, dauer=0.8, r=(3, 6))),
            Mit('o', Setze(muede=0.55)),
            Mit('o', Stehe(0.8, lambda o, u: Pose(blick_y=-1.0, auge_zu=0.5 < u < 0.62))),
            # die letzte Feder
            Tu(lambda sz: setattr(sz, 'feder', (sz.o.x, sz.ay - 170 * sz.s,
                                                lambda: sz.ast_punkt(AST_L * 0.8)[1] - 4 * sz.s))),
            WarteBisFeder(),
            Wandel(0.3, bieg=135.0),
            Mit('o', Stehe(0.7, lambda o, u: Pose(blick_y=-0.2, auge_zu=0.3 < u < 0.42))),
            Mit('o', Setze(muede=0.0)),
            Nebenbei(wegfliegen(self, 'o', 0.8, hoch=-120)),
            Wandel(0.6, deck=0.0),
            WarteNebenbei(),
        ]

    def schreck_ablauf(self):
        self.nebenbei.clear()
        self.auf_ast = False
        o = self.o
        neu = []
        if o.figur_sichtbar():
            o.zerzaust, o.muede = 1.0, 0.0
            o.pose = Pose(schreck=1.0)
            self.streue(o.x, o.y - 50 * self.s, 8, FEDERN, tempo=120, dauer=0.6, r=(3, 6))
            neu.append(Nebenbei(wegfliegen(self, 'o', 0.6)))
        else:
            o.zeige_figur = False
        return neu + [Wandel(0.4, deck=0.0), WarteNebenbei()]

    def zeichne_hinten(self, p):
        p.save()
        p.setOpacity(self.deck)
        p.translate(self.wand, self.ay)
        p.scale(self.s * self.dir, self.s)
        p.setPen(KEIN_STIFT)
        zeichne_ast(p, AST_L, self.bieg + self.schwing)
        p.restore()
        if self.feder:
            fx, fy, _ = self.feder
            p.save()
            p.setOpacity(self.deck)
            p.translate(fx, fy)
            p.scale(self.s, self.s)
            p.setPen(KEIN_STIFT)
            zeichne_einzelfeder(p, 0, 0, 10 * math.sin(self.t * 3), 34)
            p.restore()

    def grenzen_extra(self):
        s = self.s
        x0 = self.wand if self.dir > 0 else self.wand - (AST_L + 30) * s
        k = QRectF(x0, self.ay - 80 * s, (AST_L + 30) * s, 230 * s)
        if self.feder:
            fx, fy, _ = self.feder
            k = k.united(QRectF(fx - 20 * s, fy - 20 * s, 40 * s, 40 * s))
        return k


class WarteBisFeder(Warte):
    def __init__(self):
        super().__init__(0)

    def fertig(self, sz, u):
        return not sz.feder or sz.feder[1] >= sz.feder[2]() - 0.5 or u > 4
