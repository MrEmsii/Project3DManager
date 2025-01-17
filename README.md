# 🖨️ Project 3D Manager

## Opis

**Project 3D Manager** to aplikacja napisana w Pythonie, służąca do zarządzania projektami związanymi z drukiem 3D. Program został opracowany na zlecenie firmy i zawiera tylko wybrane funkcjonalności. Dzięki temu aplikacja umożliwia skuteczne zarządzanie projektami druku 3D przy zachowaniu prostoty i intuicyjności dla kogoś kto dopiero będzie zaczynać przygodę z projektami w druku 3D.

---

## Funkcjonalności

### Zarządzanie projektami
- Przechowywanie podstawowych informacji o projektach, takich jak:
  - Nazwa projektu
  - Rodzaj filamentu
  - Czas druku
  - Koszt druku
  - Całkowity koszt oraz czas druku (obliczany automatycznie)

### Zarządzanie elementami
- Tworzenie i przeglądanie listy elementów należących do projektu.

### Lista projektów i elementów
- Przegląd wszystkich projektów i elementów w formie czytelnej listy.
- Możliwość dodawania i edytowania projektów oraz elementów.

### Obsługa plików G-code
- Wyświetlanie listy plików G-code przypisanych do projektów.
- Otwieranie i dodawanie plików bezpośrednio z aplikacji.

---

## Wykorzystane technologie

- **Python** (importowane moduły):
  - `os`, `shutil` – zarządzanie plikami i folderami
  - `tkinter`, `tkinterdnd2` – tworzenie graficznego interfejsu użytkownika (GUI)
  - `sqlalchemy` – zarządzanie bazą danych projektów, elementów i filamentów
  - `datetime` – obsługa dat

- **Baza danych:** SQLite z wykorzystaniem ORM SQLAlchemy:
  - Modele danych: `Projekt`, `Element`, `Filament`, `Firma`, `projekt_relacja`
  - Obsługa relacji między projektami a elementami.

---

## Przeznaczenie
Aplikacja jest dedykowana firmie zlecającej, dlatego została okrojona z niektórych funkcjonalności i możliwości, które mogą być dostępne w bardziej rozbudowanych wersjach oprogramowania tego typu.

---

## Instalacja i uruchomienie

1. **Klonowanie repozytorium**
   ```bash
   git clone <URL_repozytorium>
   cd <nazwa_folderu>
   ```

2. **Instalacja zależności**
   Upewnij się, że masz zainstalowane środowisko Python (wersja 3.8 lub nowsza). Następnie zainstaluj wymagane biblioteki:
   ```bash
   pip install -r requirements.txt
   ```

3. **Uruchomienie aplikacji**
   ```bash
   python main.py
   ```

---

## Licencja
Projekt jest dostępny na licencji prywatnej i może być wykorzystywany wyłącznie przez firmę, która zleciła jego stworzenie.

---

## Plany rozwoju
- Rozszerzenie integracji z drukarkami 3D (bezpośrednie wysyłanie plików G-code).
- Wizualizacja statystyk druku (czas, koszt, wykorzystanie filamentu).
- Program będzie rozwijany o funkcjonalności, które przejdą przez weryfikacje.

Jeśli masz pytania lub potrzebujesz pomocy z obsługą programu, skontaktuj się w wiadomości prywatnej.
