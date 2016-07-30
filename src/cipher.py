import os

BLOCK_SIZE_EXP = 3      # 2 ** 3 == 8 byte blocks


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
            data = data.encode('hex')
        blocks = [os.urandom(size)] + [data[i:i+size] for i in range(0, len(data), size)]
        for i in range(1, len(blocks)):
            blocks[i] = CXOR(blocks[i - 1], blocks[i])
        return ''.join(blocks)
    elif mode == 'd':
        blocks = [data[i:i+size] for i in range(0, len(data), size)]
        for i in reversed(range(1, len(blocks))):
            blocks[i] = CXOR(blocks[i - 1], blocks[i])
        data = ''.join(blocks[1:])
        for i in range(BLOCK_SIZE_EXP):
            data = data.decode('hex')
        return data


def zombify(mode, data, key):           # Linking helper function (it can encrypt only once!)
    hexed_key = key.encode('hex')       # further encryption might render decryption impossible!
    ch = sum((ord(i) for i in hexed_key))   # (due to a newline compromise I had to do for cross-platforms)
    if mode == 'e':
        text = CBC('e', data.encode('hex'))
        return CXOR(shift(text, ch), key)   # CBC encode, shift and XOR
    elif mode == 'd':
        try:
            text = shift(CXOR(data, key), 256 - ch)
            return CBC('d', text).decode('hex')     # do the reverse
        except TypeError:
            return None
