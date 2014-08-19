# Utility functions related to prime numbers

import math

def is_prime(num, primes=[]):
    """Returns True if the number is prime, else False"""
    # use the square root of the number to cut off testing
    sqrt = math.sqrt(num)
    # given a list of primes, use the list to check factors
    if len(primes) > 0:
        for prime in primes:
            if prime > sqrt:
                return True
            if num % prime == 0:
                return False
    # given no list, check 2, odd numbers as factors
    else:
        if num % 2 == 0:
            return False
        for i in range(3, sqrt, 2):
            if num % i == 0:
                return False
    return False

def gen_primes_sieve(max):
    """Generates a list of primes up to max using the sieve of Eratosthenes"""
    # Optimized implementation: squares
    sqrt = int(math.sqrt(max))
    nums = range(2, sqrt)
    primes = range(2, max)
    for num in nums:
        for i in range(num*num, max, num):
            if i in primes:
                primes.remove(i)
    return primes