from abc import ABC, abstractmethod
from datetime import datetime

# --- 1. FŐ OSZTÁLYOK ---

class Jarat(ABC):
    """Absztrakt ősosztály a járatoknak."""
    def __init__(self, jaratszam, celallomas, jegyar):
        self._jaratszam = jaratszam
        self._celallomas = celallomas
        self.jegyar = jegyar  # A setteren keresztül állítjuk be a validáció miatt

    @property
    def jaratszam(self):
        return self._jaratszam

    @property
    def celallomas(self):
        return self._celallomas

    @property
    def jegyar(self):
        return self._jegyar

    @jegyar.setter
    def jegyar(self, ertek):
        if ertek <= 0:
            raise ValueError("A jegyár csak pozitív összeg lehet.")
        self._jegyar = ertek

    @abstractmethod
    def jarat_info(self):
        """Absztrakt metódus, melyet a leszármazottaknak kötelező implementálni."""
        pass


class BelfoldiJarat(Jarat):
    """Belföldi járat, jellemzően olcsóbb."""
    def __init__(self, jaratszam, celallomas, jegyar):
        super().__init__(jaratszam, celallomas, jegyar)

    def jarat_info(self):
        return f"[Belföldi] {self.jaratszam} -> {self.celallomas} ({self.jegyar} Ft)"


class NemzetkoziJarat(Jarat):
    """Nemzetközi járat, magasabb jegyárral."""
    def __init__(self, jaratszam, celallomas, jegyar):
        super().__init__(jaratszam, celallomas, jegyar)

    def jarat_info(self):
        return f"[Nemzetközi] {self.jaratszam} -> {self.celallomas} ({self.jegyar} Ft)"


class LegiTarsasag:
    """Légitársaság osztály, amely összefogja a járatokat."""
    def __init__(self, nev):
        self._nev = nev
        self._jaratok = []

    @property
    def nev(self):
        return self._nev

    @property
    def jaratok(self):
        # A tokozás (encapsulation) védelme érdekében másolatot adunk vissza
        return self._jaratok.copy()

    def jarat_hozzaadasa(self, jarat):
        if not isinstance(jarat, Jarat):
            raise TypeError("Csak Jarat típusú objektum adható hozzá.")
        self._jaratok.append(jarat)


class JegyFoglalas:
    """Egy adott foglalást reprezentáló osztály."""
    def __init__(self, jarat, utas_neve, datum):
        self._jarat = jarat
        self._utas_neve = utas_neve
        self._datum = datum

    @property
    def jarat(self):
        return self._jarat

    @property
    def utas_neve(self):
        return self._utas_neve

    @property
    def datum(self):
        return self._datum


# --- 2. RENDSZER ÉS FUNKCIÓK ---

class FoglalasiRendszer:
    """A foglalásokat kezelő és validáló rendszer."""
    def __init__(self, legitarsasag):
        self._legitarsasag = legitarsasag
        self._foglalasok = []

    def jegy_foglalasa(self, jaratszam, utas_neve, datum_str, csendes=False):
        """Lefoglal egy jegyet, ha az adatok érvényesek, és visszaadja az árat."""
        try:
            # 1. Dátum validáció (múltbeli időpont kiszűrése)
            datum = datetime.strptime(datum_str, "%Y-%m-%d")
            if datum.date() < datetime.now().date():
                raise ValueError("A foglalás időpontja nem lehet a múltban.")
            
            # 2. Járat validáció (létezik-e)
            kivalasztott_jarat = next((j for j in self._legitarsasag.jaratok if j.jaratszam == jaratszam), None)
            if not kivalasztott_jarat:
                raise ValueError(f"Nem létező járat: {jaratszam}")
            
            # 3. Duplikáció szűrése (van-e már ilyen foglalás)
            for f in self._foglalasok:
                if f.utas_neve == utas_neve and f.jarat.jaratszam == jaratszam and f.datum.date() == datum.date():
                    raise ValueError("Erre a járatra ezen a napon már van rögzített foglalása ennek az utasnak.")

            # Foglalás létrehozása
            uj_foglalas = JegyFoglalas(kivalasztott_jarat, utas_neve, datum)
            self._foglalasok.append(uj_foglalas)
            
            if not csendes:
                print(f"\n✅ Sikeres foglalás! Utas: {utas_neve}, Járat: {jaratszam}. Fizetendő: {kivalasztott_jarat.jegyar} Ft.")
            return kivalasztott_jarat.jegyar
            
        except ValueError as e:
            if not csendes:
                print(f"\n❌ Hibás adat: {e}")
            return None

    def foglalas_lemondasa(self, utas_neve, jaratszam):
        """Lemondja a foglalást az utas neve és a járatszám alapján."""
        for foglalas in self._foglalasok:
            if foglalas.utas_neve == utas_neve and foglalas.jarat.jaratszam == jaratszam:
                self._foglalasok.remove(foglalas)
                print(f"\n✅ A(z) {jaratszam} számú járatra szóló foglalás ({utas_neve}) sikeresen lemondva.")
                return True
        
        print("\n❌ Hiba: Nem található ilyen foglalás a rendszerben. (Ellenőrizd a nevet és a járatszámot!)")
        return False

    def foglalasok_listazasa(self):
        """Kiírja a konzolra az összes aktív foglalást."""
        print(f"\n--- Aktuális foglalások ({self._legitarsasag.nev}) ---")
        if not self._foglalasok:
            print("Jelenleg nincs egyetlen aktív foglalás sem.")
            return

        for i, f in enumerate(self._foglalasok, 1):
            print(f"{i}. Utas: {f.utas_neve} | Járat: {f.jarat.jaratszam} -> {f.jarat.celallomas} | Dátum: {f.datum.strftime('%Y-%m-%d')} | Ár: {f.jarat.jegyar} Ft")
        print("-----------------------------------")


# --- 3. ELŐKÉSZÍTÉS ÉS FELHASZNÁLÓI INTERFÉSZ ---

def adatok_elokeszitese():
    """Rendszer inicializálása 1 légitársasággal, 3 járattal és 6 foglalással."""
    wizzair = LegiTarsasag("WizzAir")
    
    # 3 járat létrehozása (1 belföldi, 2 nemzetközi)
    wizzair.jarat_hozzaadasa(BelfoldiJarat("W6101", "Debrecen", 15000))
    wizzair.jarat_hozzaadasa(NemzetkoziJarat("W6202", "London", 45000))
    wizzair.jarat_hozzaadasa(NemzetkoziJarat("W6303", "Párizs", 55000))
    
    rendszer = FoglalasiRendszer(wizzair)
    
    # Későbbi dátum megadása a tesztadatokhoz
    jovo_datum = "2026-12-01"
    
    # 6 előre betöltött foglalás
    rendszer.jegy_foglalasa("W6101", "Kovács Péter", jovo_datum, csendes=True)
    rendszer.jegy_foglalasa("W6101", "Nagy Anna", jovo_datum, csendes=True)
    rendszer.jegy_foglalasa("W6202", "Szabó Gábor", jovo_datum, csendes=True)
    rendszer.jegy_foglalasa("W6202", "Tóth Eszter", jovo_datum, csendes=True)
    rendszer.jegy_foglalasa("W6303", "Kiss Zoltán", jovo_datum, csendes=True)
    rendszer.jegy_foglalasa("W6303", "Varga Edit", jovo_datum, csendes=True)
    
    return rendszer, wizzair

def main():
    rendszer, legitarsasag = adatok_elokeszitese()
    
    while True:
        print("\n" + "="*40)
        print("   REPÜLŐJEGY FOGLALÁSI RENDSZER")
        print("="*40)
        print("1. Elérhető járatok megtekintése")
        print("2. Jegy foglalása")
        print("3. Foglalás lemondása")
        print("4. Aktuális foglalások listázása")
        print("5. Kilépés")
        
        valasztas = input("\nVálassz egy menüpontot (1-5): ")
        
        if valasztas == "1":
            print(f"\n--- {legitarsasag.nev} Elérhető Járatai ---")
            for jarat in legitarsasag.jaratok:
                # Most már használhatjuk a polimorfizmust a kiíratásra
                print(jarat.jarat_info())
                
        elif valasztas == "2":
            utas_neve = input("Kérem az utas nevét: ")
            jaratszam = input("Kérem a járatszámot (pl. W6101): ")
            datum = input("Kérem a foglalás dátumát (ÉÉÉÉ-HH-NN formátumban): ")
            rendszer.jegy_foglalasa(jaratszam, utas_neve, datum)
            
        elif valasztas == "3":
            utas_neve = input("Kérem az utas nevét a lemondáshoz: ")
            jaratszam = input("Kérem a lemondandó járatszámot: ")
            rendszer.foglalas_lemondasa(utas_neve, jaratszam)
            
        elif valasztas == "4":
            rendszer.foglalasok_listazasa()
            
        elif valasztas == "5":
            print("\nKöszönjük, hogy a mi rendszerünket használta! Viszontlátásra.")
            break
            
        else:
            print("\n❌ Érvénytelen választás. Kérlek, 1 és 5 közötti számot adj meg.")

if __name__ == "__main__":
    main()