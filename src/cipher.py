import os

BLOCK_SIZE_EXP = 3      # 2 ** 3 == 8 byte blocks

def hexed(text):                    # Hexing function
    return map(lambda i: format(ord(i), '02x'), text)

def char(text):                     # Hex-decoding function
    return text.decode('hex')

def CXOR(text, key):                # Byte-wise XOR
    def xor(char_1, char_2):
        return chr(ord(char_1) ^ ord(char_2))
    text_size, key_size = len(text), len(key)
    return ''.join([xor(text[i], key[i % key_size]) for i in range(text_size)])

def shift(text, amount):            # Shifts the ASCII value of the chars
    return ''.join(chr((ord(ch) + amount) % 256) for ch in text)

def CBC(mode, data):         # Splits & chains into blocks (for some randomness)
    size = 2 ** BLOCK_SIZE_EXP
    if mode == 'e':
        for i in range(BLOCK_SIZE_EXP):     # Each step of hexing doubles the bytes
            data = ''.join(hexed(data))
        blocks = [os.urandom(size)] + [data[i:i+size] for i in range(0, len(data), size)]
        for i in range(1, len(blocks)):
            blocks[i] = CXOR(blocks[i - 1], blocks[i])
        return ''.join(blocks)
    elif mode == 'd':
        blocks = [data[i:i+size] for i in range(0, len(data), size)]
        for i in range(1, len(blocks))[::-1]:
            blocks[i] = CXOR(blocks[i - 1], blocks[i])
        data = ''.join(blocks[1:])
        for i in range(BLOCK_SIZE_EXP):
            data = char(data)
        return data

def zombify(mode, data, key):           # Linking helper function (it can encrypt only once!)
    hexed_key = ''.join(hexed(key))     # further encryption might render decryption impossible!
    ch = sum((ord(i) for i in hexed_key))   # (due to a newline compromise I had to do for cross-platforms)
    if mode == 'e':
        text = CBC('e', ''.join(hexed(data)))
        return CXOR(shift(text, ch), key)   # CBC encode, shift and XOR
    elif mode in ('d', 'w'):
        try:
            text = shift(CXOR(data, key), 256 - ch)
            return char(CBC('d', text))     # do the reverse
        except TypeError:
            return None
