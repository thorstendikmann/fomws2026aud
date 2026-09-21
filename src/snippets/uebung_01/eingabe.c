#include <stdio.h>

#include <math.h>

#if defined(__GNUC__) || defined(__clang__)
#  pragma GCC diagnostic push
#  pragma GCC diagnostic ignored "-Wunused-parameter"
#  pragma GCC diagnostic ignored "-Wunused-variable"
#endif

/**
 * a) Lesen Sie vom Benutzer zwei Zahlenwerte \f$ x,y \elem \Z \f$ ein (scanf).
 * Gebe aus: \f$ x+y \f$ sowie \f$ x^y \f$
 */
void a_zahlenwerte(void)
{
    int x;
    int y;

    // TODO
}

#ifdef UNIX
#include <sys/param.h>
#else
#define MIN(a, b) (((a) < (b)) ? (a) : (b))
#define MAX(a, b) (((a) > (b)) ? (a) : (b))
#endif
/**
 * b)	Lesen Sie vom Benutzer drei Zahlenwerte (Float) ein. Geben Sie das größte Element aus.
 */
void b_max(void)
{
    float f, g, h;

    printf("Gebe drei Fließkommazahlen ein: \n");
    // TODO
}

/** Struct für Aufgabe c) */
typedef struct ad
{
    /** Adresse - Name */
    char name[50];
    /** Adresse - Straße */
    char str[100];
    /** Adresse - Postleitzahl */
    char plz[10];
    /** Adresse - Stadt */
    char stadt[30];
} addresse;

void c_printAdresse(addresse *addr)
{
    printf("Adresse: %s, %s, %s, %s",
           addr->name, addr->str, addr->plz, addr->stadt);
}

#include <stdlib.h>
#include <string.h>
/**
 * c)	Lesen Sie vom Benutzer ein (scanf, fgets): Name, Adresse, PLZ, Stadt
 *      Legen Sie ein geeignetes struct zur Speicherung dieser Daten an. Schreiben Sie eine Funktion, die ein solches Struct als Referenz übergeben bekommt und alle Daten ausgibt.
 */
void c_adresse(void)
{
    // TODO
}

/** d)	Lesen Sie vom Benutzer drei Fließkommazahlen ein. Geben Sie an, ob sich aus diesen drei Zahlen ein Dreieck konstruieren lässt. */
void d_dreiecke(void)
{
    float x, y, z;

    // TODO
}

#if defined(__GNUC__) || defined(__clang__)
#  pragma GCC diagnostic pop
#endif

int main(void)
{
    printf("Uncomment parts in source code.\n");
    // a_zahlenwerte();
    // b_max();
    // c_adresse();
    // d_dreiecke();
    return 0;
}
