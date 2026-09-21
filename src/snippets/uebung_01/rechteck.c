#include <stdio.h>

#if defined(__GNUC__) || defined(__clang__)
#  pragma GCC diagnostic push
#  pragma GCC diagnostic ignored "-Wunused-parameter"
#endif

/** Datenstruktur zum Speichern eines Rechtecks. */
typedef struct rechteck
{
    /** Breite */
    float breite;
    /** Länge */
    float laenge;
} rechteck;

/** Gebe den Umfang des übergebenen rechtecks aus. */
void calcAndPrintUmfang(rechteck *r)
{
   // TODO
}
/** Gebe die Fläche des übergebenen rechtecks aus. */
void calcAndPrintFlaeche(rechteck *r)
{
    // TODO
}

#if defined(__GNUC__) || defined(__clang__)
#  pragma GCC diagnostic pop
#endif

int main(void)
{
    rechteck reck;
    reck.breite = 10.0;
    reck.laenge = 5.0;

    printf("Rechteck: Länge: %f, Breite: %f\n", reck.laenge, reck.breite);

    calcAndPrintUmfang(&reck);
    calcAndPrintFlaeche(&reck);
    return 0;
}
