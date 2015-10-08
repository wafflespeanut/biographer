use random::{thread_rng, sample};
use serialize::hex::{FromHex, ToHex};

// Invokes the helper functions and does its shifting thing
pub fn zombify(mode: u8, data: &Vec<u8>, key: &str) -> Vec<u8> {
    let hexed_key = key.as_bytes().to_hex();
    let mut text = data.clone();
    let mut amount: u8 = hexed_key
                         .as_bytes()
                         .iter()
                         .fold(0, |amt, &byte| amt.wrapping_add(byte));

    if mode == 1 {  // encrypts the vector of bytes
        // but this won't be useful since the library is meant to only decrypt files (for now)
        text = data.to_hex().into_bytes();
        let stuff = cbc(mode, &text, 3);        // pow(2, 3) = 8 byte blocks
        let shifted_text = shift(&stuff, amount);
        xor(&shifted_text, &key)
    } else {    // decrypts the vector of bytes
        let limit: u8 = 0;
        amount = limit.wrapping_sub(amount);    // shift by (256 - amount) for the reverse process
        let shifted_text = xor(&text, &key);
        let stuff = shift(&shifted_text, amount);
        charred(cbc(mode, &stuff, 3))
    }
}

// Hex-decoding function
fn charred(decode: Vec<u8>) -> Vec<u8> {
    // Mostly, I try to stick to immutable borrows, but from_utf8() requires Vec<u8>
    match String::from_utf8(decode) {
        // unwrap the values to find if an error occurs in encoding
        Ok(stuff) => stuff.from_hex().unwrap(),
        // error means that decryption has failed! (which should be due to wrong keys)
        Err(_) => Vec::new(),
    }
}

// Shifts the vector elements according to the given amount
fn shift(text: &[u8], amount: u8) -> Vec<u8> {
    text.iter()         // wrap around the boundary if the sum overflows
        .map(|byte| amount.wrapping_add(*byte))
        .collect()      // we don't have to specify `collect::<Vec<u8>>` explicitly
}

// Byte-wise XOR of vector elements according to a given string
fn xor(text: &[u8], key: &str) -> Vec<u8> {
    let mut xorred: Vec<u8> = Vec::new();
    let key_array = key.as_bytes();
    let (mut i, mut j) = (0, 0);
    while i < text.len() {
        xorred.push(text[i] ^ key_array[j]);
        i += 1;
        j += 1;
        if j == key.len() {
            j = 0;
        }
    } xorred
}

// CBC mode as a seed to scramble the final ciphertext
fn cbc(mode: u8, data: &Vec<u8>, power: u32) -> Vec<u8> {
    let size = 2usize.pow(power);           // block size: pow(2, power)
    if mode == 1 {
        let mut cbc_vec: Vec<u8> = sample(&mut thread_rng(), 1..255, size);
        let mut stuff = data.clone();
        // hex the bytes until the vector has the required length (an integral multiple of block size)
        for _ in 0..power {
            stuff = stuff.to_hex().into_bytes();
        } cbc_vec.extend(&stuff);
        for i in size..(stuff.len() + size) {
            cbc_vec[i] = cbc_vec[i] ^ cbc_vec[i-size];      // XOR the current block with previous block
        } cbc_vec
    } else {
        let mut i = data.len() - 1;
        let mut cbc_vec = data.clone();
        while i >= size {
            cbc_vec[i] = cbc_vec[i] ^ cbc_vec[i-size];
            i -= 1;
        } let mut stuff = cbc_vec[size..].to_vec();
        for _ in 0..power {
            stuff = charred(stuff);
        } stuff
    }
}
