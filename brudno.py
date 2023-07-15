import random


def play_game():
    # Wylosowanie 7 liczb od 1 do 12
    secret_numbers = random.sample(range(1, 13), 7)

    # Pętla trzech prób
    for i in range(3):
        # Zapytanie gracza o 7 liczb
        guess = input("Podaj 7 liczb od 1 do 12, oddzielając je spacjami: ")
        guess_numbers = [int(x) for x in guess.split()]

        # Sprawdzenie trafień
        correct = 0
        misplaced = 0
        for j in range(7):
            if guess_numbers[j] == secret_numbers[j]:
                correct += 1
            elif guess_numbers[j] in secret_numbers:
                misplaced += 1

        # Wyświetlenie wyniku próby
        print("Liczby na dobrych miejscach: ", correct)
        print("Liczby na złych miejscach: ", misplaced)

        # Sprawdzenie, czy gracz odgadł wszystkie liczby
        if correct == 7:
            print("Gratulacje! Odgadłeś wszystkie liczby.")
            return

    # Wyświetlenie informacji o przegranej
    print("Niestety nie udało się odgadnąć liczb. Wylosowane liczby to: ", secret_numbers)


# Uruchomienie gry
play_game()