#include <stdio.h>
#include <stdlib.h>

#if defined(__GNUC__) || defined(__clang__)
#  pragma GCC diagnostic push
#  pragma GCC diagnostic ignored "-Wunused-parameter"
#endif

/**
 * a) Schreiben Sie ein Programm, welches die geraden Nummern zwischen 1 und 50 (inkl.) ausgibt.
 */
void evenNumbers(void)
{
    // TODO
}

#include <math.h>
/**
 * Checks for z being prime.
 * @param z the number to be checked
 * @return 1 if z is prime, 0 otherwise
 */
int isPrime(int z)
{
    // TODO
    return (1);
}

/**
 * Schreiben Sie ein Programm, welches die Primzahlen zwischen 2 und 1000 ausgibt.
 * Implementieren Sie hierzu eine Funktion isPrime(int), welche "herkömmlich" mit einer Schleife alle möglichen Teiler ausfindig macht.
 *
 * @param maxNumber Upper boundary to check until.
 * @param output Set to 1 for printf the result.
 */
void primeNumbers(int maxNumber, char output)
{
    // TODO
}

#include <string.h>
/**
 * c)	Schreiben Sie ein weiteres Programm, welches die Primzahlen zwischen 2 und 1000 ausgibt.
 * Verwenden Sie dieses Mal den Algorithmus „Sieb von Eratosthenes“.
 *
 * @param maxNumber Upper boundary to check until.
 * @param output Set to 1 for printf the result.
 */
void primeNumbersSieveOfEratosthenes(int maxNumber, char output)
{
    // TODO
}

#include <time.h>
/**
 * d)	Erweitern Sie c) und d) um eine Funktion zum Messen der Ausführungsgeschwindigkeit und starten sie einen Geschwindigkeitsvergleich (ohne Ausgabe!).
 */
void timeMeasurements(void)
{
    // TODO
}

#if defined(__GNUC__) || defined(__clang__)
#  pragma GCC diagnostic pop
#endif

int main(void)
{
    evenNumbers();
    primeNumbers(100, 1);
    primeNumbersSieveOfEratosthenes(100, 1);

    // Aufgabe d)
    timeMeasurements();

    return 0;
}
