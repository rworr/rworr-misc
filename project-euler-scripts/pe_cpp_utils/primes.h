// Utility functions and classes related to prime numbers

#include <cmath>
#include <cstring>
#include <cstdint>
#include <iostream>
#include <exception>

using namespace std;

namespace Primes {
    // Class encapulating a list of prime numbers
    // Methods to generate primes, and checking if numbers are primes
    template <class T = int>
    class PrimeList {
        public:
            // Constructors and Destructors
            PrimeList(T val, bool max = false, int len = DEFAULT_CAPACITY);
            ~PrimeList();

            // Get number of primes in the list
            int count() {
                return length;
            }

            // Get value of highest prime in the list
            T highest() {
                if(length > 0) {
                    return primes[length-1];
                } else {
                    return 0;
                }
            }

            // Get value of a prime at index idx
            T value(int idx) {
                if(idx < 0 || idx >= length) {
                    throw new exception();
                }
                return primes[idx];
            }

            // Generate new prime in list
            void genNext();

            // Check if a number is prime
            bool isPrime(T num);

            // Print to std::cout
            void print() {
                for(int i = 0; i < length-1; ++i) {
                    cout << value(i) << ", ";
                }
                cout << value(length-1) << endl;
            }

        private:
            static const int DEFAULT_CAPACITY = 128; // default list size
            
            int length;  // Number of primes in the list
            T* primes;   // Array containing primes
            int size;    // Capacity of the primes array

            // Binary search through the list
            bool inList(T num);

            // Add a number to the list
            void insert(T num);
    };

    // Construtor for Prime List
    // if max is true, generate all primes up to and including val
    // if max is false, generate the first val primes
    template <class T>
    PrimeList<T>::PrimeList(T val, bool max, int capacity) {
        // Instantiate the list of primes
        if(val < 1 || (val == 1 && max) || capacity < 1) {
            throw new exception();
        }
        length = 0;
        size = capacity;
        primes = new T[size];
        // Insert 2, then insert all odd prime numbers
        insert(2);
        if(max) {
            // to generate primes up to a maximum, use the sieve of Eratosthenes
            int root = sqrt(val); // optimized to start from squares
            int range = (val - 1) >> 1; // optimized to skip even numbers (2 already included in primes)
            bool* primelist = new bool[range];
            // first step: set all possible numbers to true
            // starting from 3 (index i corresponds to number 2i + 3)
            for(int i = 0; i < range; ++i) {
                primelist[i] = true;
            }
            // second step: start from the square of the number in question, 
            // and cross off all multiples of the number (skipping even numbers, so increment by 2i)
            for(int i = 3; i < root; i += 2) {
                int inc = i << 1; // skip even numbers
                for(int j = i*i; j <= val; j += inc) {
                    // Cross off multiples of i
                    primelist[(j >> 1) - 1] = false;
                }
            }
            // final step: read the list of prime numbers off the sieve
            for(int i = 0; i < range; ++i) {
                if(primelist[i]) {
                    insert((i << 1) + 3);
                }
            }
            // clean up memory!
            delete primelist;
        } else { 
            // generate the list of primes up to the specified length
            for(T i = 3; length < val; i += 2) {
                if(isPrime(i)) {
                    insert(i);
                }
            }
        }
    }

    // Destructor for Prime List
    template <class T>
    PrimeList<T>::~PrimeList() {
        delete primes;
    }

    // Generate next prime in a Prime List
    template <class T>
    void PrimeList<T>::genNext() {
        for(T i = highest() + 2;; i += 2) {
            if(isPrime(i)) {
                insert(i);
                return;
            }
        }
    }

    // Check if a number is prime using the Prime List
    template <class T>
    bool PrimeList<T>::isPrime(T num) {
        // Easy check: even numbers are not prime
        if(!(num & 1)) {
            return false;
        }
        if(highest() > num) {
            // Check if the number is in the list
            return inList(num);
        } else {
            // Otherwise, check for factors
            int root = sqrt(num);
            for(int i = 0; value(i) <= root; ++i) {
                if(!(num % value(i))) {
                    return false;
                }
            }
            return true;
        }
    }

    // Search through the list for a number using a binary search
    template <class T>
    bool PrimeList<T>::inList(T num) {
        int end = length;
        int start = 0;
        while(start != end) {
            int idx = (end - start) >> 1;
            if(value(idx) == num) {
                return true;
            } else if(value(idx) > num) {
                // need to search lower in the list
                end = idx;
            } else {
                // need to search higher in the list
                start = idx;
            }
        }
        return false;
    }

    // Insert a number into the Prime List
    template <class T>
    void PrimeList<T>::insert(T num) {
        primes[length++] = num;
        if(length == size) {
            // need to increase the size of the list
            int n_size = size << 1;
            T* n_primes = new T[n_size];
            memcpy(n_primes, primes, sizeof(T)*length);
            delete primes;
            primes = n_primes;
            size = n_size;
        }
    }

    // Check if a number is prime without any given list
    bool isPrime(int num) {
        if(!(num & 1)) {
            return false;
        } else {
            int root = sqrt(num);
            for(int i = 3; i <= root; i += 2) {
                if(!(num % i)) {
                    return false;
                }
            }
        }
        return true;
    }
}
