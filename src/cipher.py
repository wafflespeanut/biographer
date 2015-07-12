def hexed(text):                    # Hexing function
    return map(lambda i: format(ord(i), '02x'), list(text))

def char(text):                     # Hex-decoding function
    split = [text[i:i+2] for i in range(0, len(text), 2)]
    try:
        return ''.join(i.decode('hex') for i in split)
    except TypeError:
        return None

def CXOR(text, key):                # Byte-wise XOR
    def xor(char1, char2):
        return chr(ord(char1) ^ ord(char2))
    out = ''
    i, j = 0, 0
    while i < len(text):
        out += xor(text[i], key[j])
        (i, j) = (i + 1, j + 1)
        if j == len(key):
            j = 0
    return ''.join(out)

def shift(text, amount):            # Shifts the ASCII value of the chars
    try:
        shiftedText = (chr((ord(ch) + amount) % 256) for ch in text)
    except TypeError:
        return None
    return ''.join(shiftedText)

def CBC(mode, data, power):         # Splits & chains into blocks (for some randomness)
    size = 2 ** power               # Each step of hexing doubles the bytes
    if mode == 'e':
        for i in range(power):
            data = ''.join(hexed(data))
        blocks = [os.urandom(size)] + [data[i:i+size] for i in range(0, len(data), size)]
        for i in range(1, len(blocks)):
            blocks[i] = CXOR(blocks[i-1], blocks[i])
        return ''.join(blocks)
    elif mode in ('d', 'w'):
        blocks = [data[i:i+size] for i in range(0, len(data), size)]
        for i in range(1, len(blocks))[::-1]:
            blocks[i] = CXOR(blocks[i-1], blocks[i])
        data = ''.join(blocks[1:])
        for i in range(power):
            try:
                data = char(data)
            except TypeError:
                return None
        return data

def zombify(mode, data, key):       # Linking helper function (it can encrypt only once!)
    hexedKey = ''.join(hexed(key))  # further encryption might render decryption impossible!
    ch = sum((ord(i) for i in hexedKey))    # (due to a newline compromise I had to do for cross-platforms)
    if mode == 'e':
        text = CBC('e', ''.join(hexed(data)), 3)        # (2 ** 3 == 8) byte blocks
        return CXOR(shift(text, ch), key)           # CBC encode, shift and XOR
    elif mode in ('d', 'w'):
        text = shift(CXOR(data, key), 256 - ch)
        return char(CBC('d', text, 3))              # do the reverse
