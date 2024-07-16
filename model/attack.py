from Crypto.Util.number import getPrime, inverse, GCD
from Crypto.Random.random import randint

def generate_keys(bits=512):
    p = 11534899272561676244925313717014331740490094532609834959814346921905689869862264593212975473787189514436889176526473093615929993728061165964347353440008577
    g = 2
    x = 1002
    h = pow(g, x, p)
    return p, g, h, x

def encrypt(p, g, h, m):
    y = 545131
    c1 = pow(g, y, p)
    s = pow(h, y, p)
    c2 = (m * s) % p
    return c1, c2

def decrypt(p, x, c1, c2):
    s = pow(c1, x, p)
    s_inv = inverse(s, p)
    m = (c2 * s_inv) % p
    return m

def find_small_factors(n):
    factors = []
    for i in range(2, 1000):
        if n % i == 0:
            factors.append(i)
            while n % i == 0:
                n //= i
    if n > 1:
        factors.append(n)
    return factors

def chinese_remainder_theorem(equations):
    x = 0
    N = 1
    for a, n in equations:
        N *= n

    for a, n in equations:
        m = N // n
        m_inv = inverse(m, n)
        x += a * m * m_inv

    return x % N

def small_subgroup_attack(p, g, h, x, c1, c2, orders):
    private_key_parts = []
    for q in orders:
        k = (p-1) // q
        c1_prime = pow(c1, k, p)
        print(f'c1_prime (for q={q}): {c1_prime}')
        
        # Simulate decryption to observe behavior (attacker would need access to decryption)
        decrypted_m_prime = decrypt(p, x, c1_prime, c2)
        
        # In a real attack, the attacker would observe the decrypted message
        if decrypted_m_prime == 1:
            private_key_parts.append((0, q))
        else:
            private_key_parts.append((1, q))
        print(f'Decrypted m\' for q={q}: {decrypted_m_prime}, guessed x mod {q}: {private_key_parts[-1][0]}')
    
    # Combine results using Chinese Remainder Theorem
    recovered_x = chinese_remainder_theorem(private_key_parts)
    return recovered_x

# Example usage
p, g, h, x = generate_keys()
print(f'p: {p}')
print(f'g: {g}')
print(f'h: {h}')
print(f'Private key x: {x}')

# Encrypt a message
m = 42
c1, c2 = encrypt(p, g, h, m)
print(f'Encrypted message: (c1={c1}, c2={c2})')

# Decrypt the message
decrypted_m = decrypt(p, x, c1, c2)
print(f'Decrypted message: {decrypted_m}')

# Perform the attack
small_factors = find_small_factors(p-1)
print(f'Small factors of p-1: {small_factors}')

# Recover the private key using the attack
recovered_x = small_subgroup_attack(p, g, h, x, c1, c2, small_factors)
print(f'Recovered private key x: {recovered_x}')
print(f'Original private key x: {x}')
print(f'Attack successful: {recovered_x == x}')
