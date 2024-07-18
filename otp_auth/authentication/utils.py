import random
import string

def generate_otp(length=6):
    digits = string.digits
    otp = ''.join(random.SystemRandom().choice(digits) for _ in range(length))
    return otp