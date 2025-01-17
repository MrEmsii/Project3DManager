from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import Table, Date, select
import datetime
import os

Base = declarative_base()

# Tabela pomocnicza do relacji projekt-element
projekt_relacja = Table(
    'projekt_element', Base.metadata,
    Column('projekt_id', Integer, ForeignKey('projekt.id')),
    Column('element_id', Integer, ForeignKey('element.id')),
    Column('ilosc_elem', Integer, default=1)
)

# Nowa klasa Firma
class Firma(Base):
    __tablename__ = 'firma'
    id = Column(Integer, primary_key=True)
    nazwa = Column(String)

    # Relacja jeden-do-wielu z projektami
    projekty = relationship('Projekt', back_populates='firma')

class Filament(Base):
    __tablename__ = 'filament'
    id = Column(Integer, primary_key=True)
    nazwa = Column(String)
    typ = Column(String)
    cena = Column(Integer)

class Projekt(Base):
    __tablename__ = 'projekt'
    id = Column(Integer, primary_key=True)
    nazwa = Column(String)
    firma_id = Column(Integer, ForeignKey('firma.id'))  # Klucz obcy do tabeli Firma
    firma = relationship('Firma', back_populates='projekty')  # Relacja firma-projekt
    elementy = relationship('Element', secondary=projekt_relacja, backref='projekty', cascade="all, delete")
    data = Column(Date, default=datetime.date.today)

    def oblicz_czas_druku(self):
        return sum(element.czas_druku * self.get_ilosc_elementu(element) for element in self.elementy)

    def oblicz_cene_projektu(self):
        return sum(element.oblicz_cene() * self.get_ilosc_elementu(element) for element in self.elementy)
    
    def get_ilosc_elementu(self, element, session):
        # Pobiera ilość danego elementu w projekcie
        wynik = self._get_projekt_element_miejsce(element, session)
        return wynik[2] if wynik else 1

    def _get_projekt_element_miejsce(self, element, session):
        stmt = select(projekt_relacja).where(projekt_relacja.c.projekt_id == self.id, projekt_relacja.c.element_id == element.id) # Tworzenie zapytania select
        wynik = session.execute(stmt).fetchone()
        return wynik

    def update_ilosc_elem(self, session, project, element, ilosc):
        stmt = select(projekt_relacja).where(projekt_relacja.c.projekt_id == project.id, projekt_relacja.c.element_id == element.id)
        projekt_element_record = session.execute(stmt).fetchone()
        if projekt_element_record:
            update_stmt = projekt_relacja.update().where(
                projekt_relacja.c.projekt_id == project.id,
                projekt_relacja.c.element_id == element.id
            ).values(ilosc_elem=ilosc)
            session.execute(update_stmt)

class Element(Base):
    __tablename__ = 'element'
    id = Column(Integer, primary_key=True)
    nazwa = Column(String)
    filament_id = Column(Integer, ForeignKey('filament.id'))
    waga = Column(Integer)
    filament = relationship('Filament', backref='elementy')
    czas_druku = Column(Integer)

    def oblicz_cene(self):
        if self.filament and self.waga and self.filament.cena:
            return self.waga * self.filament.cena / 1000  # Cena filamentu na gram
        return 0

def SQLconnect(dsc):
    db_path = os.path.join(dsc, '3DPP.db')
    engine = create_engine(f'sqlite:///{db_path}')
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    return Session()

# Funkcja testowa, która dodaje przykładową firmę, projekt, elementy i filamenty
def dodaj_testowy_projekt(session):
    # Tworzenie przykładowego filamentu
    filament1 = Filament(nazwa="PLA", typ="PLA", cena=100)  # Cena w groszach za gram

    # Tworzenie przykładowej firmy
    firma1 = Firma(nazwa="Firma Testowa")
    
    # Tworzenie przykładowych elementów
    element1 = Element(nazwa="Obudowa", waga=200, filament=filament1, czas_druku=120)  # Czas w minutach
    element2 = Element(nazwa="Pokrywa", waga=100, filament=filament1, czas_druku=60)
    
    # Tworzenie przykładowego projektu z przypisaną firmą
    projekt1 = Projekt(nazwa="Projekt Testowy", firma=firma1, elementy=[element1, element2])

    # Zatwierdzanie zmian w bazie danych
    session.add_all([filament1, projekt1, element1, element2, firma1])
    session.commit()
    print(f"Dodano testowy projekt: {projekt1.nazwa}, firma: {firma1.nazwa}")

if __name__ == "__main__":
    # Połączenie z bazą danych (przekaż odpowiednią ścieżkę)
    dsc = os.path.dirname(__file__) # lub inna ścieżka
    session = SQLconnect(dsc)

    # Dodanie testowego projektu
