import binascii
import hmac
import hashlib

def emulate_hmac(slot_id, serial, key, challenge):
    """
    slot_id 0..15
    serial 8 bytes
    key, challenge 32 bytes
    """
    serial = binascii.unhexlify(serial if len(serial) % 2 == 0 else '0' + serial)
    challenge = binascii.unhexlify(challenge)
    key = binascii.unhexlify(key)
    message = '\0' * 32
    message += challenge
    message += '\x11\x24' + chr(slot_id) + '\0' + serial + '\0\0\0\xEE\0\0\0\0\x01\x23\0\0'
    # 0000000000000000000000000000000000000000000000000000000000000000
    # cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc
    # 1124ss00SSSSSSSSSSSSSSSS000000EE0000000001230000
    return binascii.hexlify(hmac.new(key, message, hashlib.sha256).digest())
