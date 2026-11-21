#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define WORD_LEN 5

/**
 * Checks whether two words share at least one letter by comparing every letter pair with loops.
 * @return 1 if a common letter exists, otherwise 0
 * @param a first word (WORD_LEN lowercase letters)
 * @param b second word (WORD_LEN lowercase letters)
 */
int shareLetterLoop(const char *a, const char *b)
{
    for (int i = 0; i < WORD_LEN; i++)
    {
        for (int j = 0; j < WORD_LEN; j++)
        {
            if (a[i] == b[j])
            {
                return 1;
            }
        }
    }
    return 0;
}

#if defined(__GNUC__) || defined(__clang__)
#  pragma GCC diagnostic push
#  pragma GCC diagnostic ignored "-Wunused-parameter"
#endif

/**
 * Converts a word to a bitmask: bit 0 is set if the word contains 'a', bit 1 for 'b', ...
 * @return the bitmask of the word
 * @param w word (WORD_LEN lowercase letters)
 */
unsigned int toMask(const char *w)
{
    unsigned int mask = 0;

    // TODO
    // turn the word into a bitmask and save the result in 'mask'.

    return mask;
}

#if defined(__GNUC__) || defined(__clang__)
#  pragma GCC diagnostic pop
#endif

/**
 * Checks whether two words share at least one letter using their bitmasks.
 * @return non-zero if a common letter exists, otherwise 0
 */
int shareLetterMask(unsigned int maskA, unsigned int maskB)
{
    return (maskA & maskB) != 0;
}

/** Fills a word with random lowercase letters. */
void randomWord(char *w)
{
    for (int i = 0; i < WORD_LEN; i++)
    {
        w[i] = 'a' + rand() % 26;
    }
}

/**
 * Benchmarks the loop comparison against the bitmask comparison.
 * The bitmasks are precomputed once per word, as in the real problem.
 */
void benchmarkWordCompare(void)
{
    printf("- %s, %d\n", __func__, __LINE__);

    // You can change the number of words to test with, but keep it reasonable for the benchmark.
    int words_count = 1000;
    // Number of times the full pairwise comparison is repeated.
    int repetitions = 20;

    char(*words)[WORD_LEN] = malloc(sizeof(char[WORD_LEN]) * words_count);
    unsigned int *masks = malloc(sizeof(unsigned int) * words_count);
    if (words == NULL || masks == NULL)
    {
        fprintf(stderr, "Out of memory\n");
        free(words);
        free(masks);
        return;
    }

    srand(42);
    for (int i = 0; i < words_count; i++)
    {
        randomWord(words[i]);
        masks[i] = toMask(words[i]);
    }

    clock_t t_start, t_stop;
    double runtime;
    long countLoop = 0, countMask = 0;

    printf("Starting benchmark ... \n");

    // ------------- a) loops

    t_start = clock();
    for (int rep = 0; rep < repetitions; rep++)
    {
        for (int i = 0; i < words_count; i++)
        {
            for (int j = 0; j < words_count; j++)
            {
                countLoop += shareLetterLoop(words[i], words[j]);
            }
        }
    }
    t_stop = clock();

    runtime = ((double)t_stop - t_start) / CLOCKS_PER_SEC;
    printf("Runtime %lf for loop comparison \n", runtime);

    // ------------- b) bitmask

    t_start = clock();
    for (int rep = 0; rep < repetitions; rep++)
    {
        for (int i = 0; i < words_count; i++)
        {
            for (int j = 0; j < words_count; j++)
            {
                countMask += shareLetterMask(masks[i], masks[j]);
            }
        }
    }
    t_stop = clock();

    runtime = ((double)t_stop - t_start) / CLOCKS_PER_SEC;
    printf("Runtime %lf for bitmask comparison \n", runtime);

    printf("Pairs sharing a letter: loop=%ld, mask=%ld (must be equal ;))\n", countLoop, countMask);

    free(words);
    free(masks);
}

int main(void)
{
    benchmarkWordCompare();
    return 0;
}
