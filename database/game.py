import random


def play_game():
    # Wylosowanie 7 liczb od 1 do 12
    secret_numbers = random.sample(range(1, 10), 6)

    # Pętla trzech prób
    for i in range(4):
        # Zapytanie gracza o 6 liczb
        guess = input("Podaj 6 liczb od 1 do 9, oddzielając je spacjami: ")
        guess_numbers = [int(x) for x in guess.split()]

        # Sprawdzenie trafień
        correct = []
        misplaced = []
        for j in range(6):
            if guess_numbers[j] == secret_numbers[j]:
                correct.append(guess_numbers[j])
            elif guess_numbers[j] in secret_numbers:
                misplaced.append(guess_numbers[j])

        # Wyświetlenie wyniku próby
        print("Liczby na dobrych miejscach: ", correct)
        print("Liczby na złych miejscach: ", misplaced)

        # Sprawdzenie, czy gracz odgadł wszystkie liczby
        if len(correct) == 6:
            print("Gratulacje! Odgadłeś wszystkie liczby.")
            return

    # Wyświetlenie informacji o przegranej
    print("Niestety nie udało się odgadnąć liczb. Wylosowane liczby to: ", secret_numbers)


# Uruchomienie gry
play_game()