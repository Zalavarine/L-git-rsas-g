import abc
import json
from datetime import datetime

class Jarat(abc.ABC):
    def __init__(self, jaratszam, celallomas, ar):
        self.jaratszam = jaratszam
        self.celallomas = celallomas
        self.ar = ar
        self.foglalt_szekek = []

    @abc.abstractmethod
    def jegy_ar(self):
        pass

    def szabad_szekek(self):
        return [szek for szek in range(1, 51) if szek not in self.foglalt_szekek]

    def __str__(self):
        return f"{self.jaratszam} - {self.celallomas}"

class BelfoldiJarat(Jarat):
    def jegy_ar(self):
        return self.ar

    def __str__(self):
        return f"Belföldi járat {self.jaratszam} - {self.celallomas} | Ár: {self.jegy_ar():,} HUF"

class NemzetkoziJarat(Jarat):
    def __init__(self, jaratszam, celallomas, ar, repteri_dij):
        super().__init__(jaratszam, celallomas, ar)
        self.repteri_dij = repteri_dij

    def jegy_ar(self):
        return self.ar + self.repteri_dij

    def __str__(self):
        return f"Nemzetközi járat {self.jaratszam} - {self.celallomas} | Ár: {self.jegy_ar():,} HUF"

class JegyFoglalas:
    def __init__(self, foglalas_id, utas_neve, jarat, szek_szam):
        self.foglalas_id = foglalas_id
        self.utas_neve = utas_neve
        self.jarat = jarat
        self.szek_szam = szek_szam
        self.foglalas_ideje = datetime.now()
        self.statusz = "Aktív"

class Legitarsasag:
    def __init__(self, nev):
        self.nev = nev
        self.jaratok = []
        self.foglalasok = []

    def alapadatok_betoltese(self):
        self.jaratok = []
        self.foglalasok = []
        self.jarat_hozzaadas(BelfoldiJarat("W62201", "London Luton", 50000))
        self.jarat_hozzaadas(NemzetkoziJarat("DL9694", "Amsterdam", 80000, 15000))
        self.jarat_hozzaadas(BelfoldiJarat("FR1234", "Budapest", 30000))
        kezdeti_foglalasok = [
            ("Kiss János", "W62201", 12),
            ("Kovács Péter", "W62201", 13),
            ("Nagy Éva", "DL9694", 15),
            ("Tóth Anna", "DL9694", 16),
            ("Szabó István", "FR1234", 5),
            ("Molnár Edit", "FR1234", 6)
        ]
        for nev, jaratszam, szek in kezdeti_foglalasok:
            try:
                self.foglalas(nev, jaratszam, szek)
            except Exception as e:
                print(f"Hiba a foglalásnál: {e}")

    def jarat_hozzaadas(self, jarat):
        self.jaratok.append(jarat)

    def foglalas(self, utas_neve, jaratszam, szek_szam):
        for jarat in self.jaratok:
            if jarat.jaratszam == jaratszam:
                if szek_szam in jarat.szabad_szekek():
                    foglalas_id = f"F{len(self.foglalasok)+1:04d}"
                    uj_foglalas = JegyFoglalas(foglalas_id, utas_neve, jarat, szek_szam)
                    jarat.foglalt_szekek.append(szek_szam)
                    self.foglalasok.append(uj_foglalas)
                    return uj_foglalas
                raise ValueError("A szék már foglalt")
        raise ValueError("Nem létező járat")

    def foglalas_lemondas(self, foglalas_id):
        for foglalas in self.foglalasok:
            if foglalas.foglalas_id == foglalas_id and foglalas.statusz == "Aktív":
                foglalas.jarat.foglalt_szekek.remove(foglalas.szek_szam)
                foglalas.statusz = "Lemondva"
                return True
        return False

    def foglalasok_listazasa(self):
        aktivak = [f for f in self.foglalasok if f.statusz == "Aktív"]
        if not aktivak:
            print("Nincsenek aktív foglalások.")
            return
        print("\nAktív foglalások:")
        for foglalas in aktivak:
            print(f"{foglalas.foglalas_id}: {foglalas.utas_neve} - {foglalas.jarat} | Ülés: {foglalas.szek_szam}")

    def adatok_mentese(self, fajlnev="adatok.json"):
        with open(fajlnev, "w") as f:
            json.dump({
                "jaratok": [
                    {
                        "tipus": "Belfoldi" if isinstance(j, BelfoldiJarat) else "Nemzetkozi",
                        "jaratszam": j.jaratszam,
                        "celallomas": j.celallomas,
                        "ar": j.ar,
                        "repteri_dij": j.repteri_dij if isinstance(j, NemzetkoziJarat) else 0
                    } for j in self.jaratok
                ],
                "foglalasok": [
                    {
                        "foglalas_id": f.foglalas_id,
                        "utas_neve": f.utas_neve,
                        "jaratszam": f.jarat.jaratszam,
                        "szek_szam": f.szek_szam,
                        "statusz": f.statusz
                    } for f in self.foglalasok
                ]
            }, f)

    def adatok_betoltese(self, fajlnev="adatok.json"):
        try:
            with open(fajlnev, "r") as f:
                adatok = json.load(f)
                self.jaratok = []
                for j in adatok["jaratok"]:
                    if j["tipus"] == "Belfoldi":
                        jarat = BelfoldiJarat(j["jaratszam"], j["celallomas"], j["ar"])
                    else:
                        jarat = NemzetkoziJarat(j["jaratszam"], j["celallomas"], j["ar"], j["repteri_dij"])
                    self.jaratok.append(jarat)
                self.foglalasok = []
                for f in adatok["foglalasok"]:
                    jarat = next(j for j in self.jaratok if j.jaratszam == f["jaratszam"])
                    foglalas = JegyFoglalas(
                        f["foglalas_id"],
                        f["utas_neve"],
                        jarat,
                        f["szek_szam"]
                    )
                    foglalas.statusz = f["statusz"]
                    self.foglalasok.append(foglalas)
                    if f["statusz"] == "Aktív":
                        jarat.foglalt_szekek.append(f["szek_szam"])
            if len(self.jaratok) < 3 or len(self.foglalasok) < 6:
                self.alapadatok_betoltese()
        except (FileNotFoundError, json.JSONDecodeError, StopIteration):
            self.alapadatok_betoltese()

def felhasznaloi_interfesz(legitarsasag):
    while True:
        print("\n=== Repülőjegy Foglalási Rendszer ===")
        print("1. Jegy foglalása")
        print("2. Foglalás lemondása")
        print("3. Foglalások listázása")
        print("4. Kilépés")
        valasztas = input("Válasszon műveletet (1-4): ")
        if valasztas == '1':
            try:
                print("\nElérhető járatok:")
                for i, jarat in enumerate(legitarsasag.jaratok, 1):
                    print(f"{i}. {jarat}")
                jarat_index = int(input("Válasszon járatot (sorszám): ")) - 1
                jarat = legitarsasag.jaratok[jarat_index]
                print(f"Szabad ülések: {jarat.szabad_szekek()}")
                szek = int(input("Válasszon ülésszámot: "))
                nev = input("Utas neve: ")
                legitarsasag.foglalas(nev, jarat.jaratszam, szek)
                print("Sikeres foglalás!")
            except (ValueError, IndexError) as e:
                print(f"Hiba: {e}")
            except Exception as e:
                print(f"Váratlan hiba: {e}")
        elif valasztas == '2':
            azon = input("Foglalási azonosító: ").strip()
            if legitarsasag.foglalas_lemondas(azon):
                print("Sikeres lemondás!")
            else:
                print("Érvénytelen azonosító vagy már lemondott foglalás!")
        elif valasztas == '3':
            legitarsasag.foglalasok_listazasa()
        elif valasztas == '4':
            legitarsasag.adatok_mentese()
            print("Köszönjük, hogy a GDE légitársaságot választotta!")
            break
        else:
            print("Érvénytelen választás!")

if __name__ == "__main__":
    gde_airlines = Legitarsasag("GDE Airlines")
    gde_airlines.adatok_betoltese()
    felhasznaloi_interfesz(gde_airlines)
