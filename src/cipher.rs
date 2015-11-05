use random::{thread_rng, sample};
use serialize::hex::{FromHex, ToHex};

const BLOCK_SIZE_EXP: u32 = 3;      // pow(2, 3) == 8 byte blocks

pub enum Mode {
    Encrypt,
    Decrypt,
}

// Invokes the helper functions and does its shifting thing
pub fn zombify(mode: Mode, data: &Vec<u8>, key: &str) -> Vec<u8> {
    let hexed_key = key.as_bytes().to_hex();
    let mut text = data.clone();
    let amount: u8 = hexed_key
                     .as_bytes()
                     .iter()
                     .fold(0, |amt, &byte| amt.wrapping_add(byte));
    match mode {
        Mode::Encrypt => {
            // well, this won't be useful since the library is meant to only decrypt files (for now)
            text = data.to_hex().into_bytes();
            let stuff = cbc(mode, &text);
            let shifted_text = shift(&stuff, amount);
            xor(&shifted_text, &key)
        },
        Mode::Decrypt => {
            let amount = 0u8.wrapping_sub(amount);      // shift by (256 - amount) for the reverse
            let shifted_text = xor(&text, &key);
            let stuff = shift(&shifted_text, amount);
            charred(cbc(mode, &stuff))
        },
    }
}

// Hex-decoding function
fn charred(decode: Vec<u8>) -> Vec<u8> {
    // Mostly, I try to stick to immutable borrows, but from_utf8() requires Vec<u8>
    // An error means that the decryption has failed! (which should be due to wrong keys)
    match String::from_utf8(decode) {
        Ok(hexed_stuff) => match hexed_stuff.from_hex() {
            Ok(stuff) => stuff,
            Err(_) => Vec::new(),
        },
        Err(_) => Vec::new(),
    }
}

// Shifts the vector elements according to the given amount
fn shift(text: &[u8], amount: u8) -> Vec<u8> {
    text.iter()         // wrap around the boundary if the sum overflows
        .map(|byte| amount.wrapping_add(*byte))
        .collect()
}

// Byte-wise XOR of vector elements according to a given string
fn xor(text: &[u8], key: &str) -> Vec<u8> {
    let key_array = key.as_bytes();
    let (text_size, key_size) = (text.len(), key.len());
    (0..text_size).map(|i| text[i] ^ key_array[i % key_size]).collect()
}

// CBC mode as a seed to scramble the final ciphertext
fn cbc(mode: Mode, data: &Vec<u8>) -> Vec<u8> {
    let size = 2usize.pow(BLOCK_SIZE_EXP);
    // Well, there's no encryption going on here - just some fireworks to introduce randomness
    match mode {
        Mode::Encrypt => {
            let mut cbc_vec: Vec<u8> = sample(&mut thread_rng(), 1..255, size);
            let mut stuff = data.clone();
            // hex the bytes until the vector has the required length (an integral multiple of block size)
            for _ in 0..BLOCK_SIZE_EXP {
                stuff = stuff.to_hex().into_bytes();
            } cbc_vec.extend(&stuff);
            for i in size..(stuff.len() + size) {
                cbc_vec[i] = cbc_vec[i] ^ cbc_vec[i - size];
            } cbc_vec
        },
        Mode::Decrypt => {
            let mut i = data.len() - 1;
            let mut cbc_vec = data.clone();
            while i >= size {
                cbc_vec[i] = cbc_vec[i] ^ cbc_vec[i - size];
                i -= 1;
            } let mut stuff = cbc_vec[size..].to_vec();
            for _ in 0..BLOCK_SIZE_EXP {
                stuff = charred(stuff);
            } stuff
        },
    }
}
