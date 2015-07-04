#![feature(libc)]
#![feature(cstr_memory)]
extern crate libc;
extern crate rand as random;
extern crate rustc_serialize as serialize;

use std::io::Read;
use std::{str, mem, slice};
use std::ffi::{CStr, CString};
use std::fs::File;
use libc::{size_t, c_char};
use random::{thread_rng, sample};
use serialize::hex::{FromHex, ToHex};

// You'll be needing Nightly rust, because `from_ptr` is unstable
// and so, it's unavailable in the stable version (for now)

// FFI function just to kill a transferred pointer
#[no_mangle]
pub extern fn kill_pointer(p: *const c_char) {
    unsafe { CString::from_ptr(p) };     // Theoretically, Rust should take the ownership back
}   // variable goes out of scope here and the C-type string should be destroyed (at least, that's what I hope)

// FFI function to be called from Python
#[no_mangle]
pub extern fn get_stuff(array: *const *const c_char, length: size_t) -> *const c_char {
    // get the raw pointer values to the strings from the array pointer
    let array = unsafe { slice::from_raw_parts(array, length as usize) };
    let mut stuff: Vec<&str> = array.iter()
        .map(|&p| unsafe { CStr::from_ptr(p) })         // get the C-type string from the pointer
        .map(|c_string| c_string.to_bytes())            // convert the raw thing to bytes
        .map(|byte| str::from_utf8(byte).unwrap())      // finally collect the corresponding strings
        .collect();
    let word = stuff.pop().unwrap();
    let key = stuff.pop().unwrap();
    let occurrences: Vec<String> = stuff.into_iter().map(|file_name| {
        count_words(&file_name, &key, &word)            // Parallel threads won't be helpful here
    }).collect();                                       // Since this isn't intensive computation,
    let count_string = occurrences.connect(" ");        // the overhead for launching threads are gonna cost more time
    let c_string = CString::new(count_string).unwrap().into_ptr();
    mem::forget(c_string);                  // Whee... Leaking the memory allocated by c_string
    c_string                                // the FFI code should now own the memory
}

// Hex-decoding function
fn charred(decode: Vec<u8>) -> Vec<u8> {
    // Mostly, I try to stick to immutable borrows, but from_utf8() requires Vec<u8>
    match String::from_utf8(decode) {
        // unwrap the values to find if an error occurs in encoding
        Ok(stuff) => stuff.from_hex().unwrap(),
        // error means that decryption has failed! (which should be due to wrong keys)
        Err(_) => { println!("\nWrong password!\n"); Vec::new() }
    }
}

// Gives a vector of file contents
fn fopen(path: &str) -> (usize, Vec<u8>) {
    let file = File::open(path);
    let mut contents: Vec<u8> = Vec::new();
    // of course, assuming that there won't be any problem in reading the file
    let file_size = file.unwrap().read_to_end(&mut contents).unwrap();
    (file_size, contents)
}

// Shifts the vector elements according to the given amount
fn shift(text: &Vec<u8>, amount: u8) -> Vec<u8> {
    text.iter()
        // wrap around the boundary if the sum overflows
        .map(|byte| amount.wrapping_add(*byte))
        .collect::<Vec<u8>>()
}

// Byte-wise XOR of vector elements according to a given string
fn xor(text: &Vec<u8>, key: &str) -> Vec<u8> {
    let mut xorred: Vec<u8> = Vec::new();
    let key_array = key.as_bytes();
    let (mut i, mut j) = (0, 0);
    while i < text.len() {
        xorred.push(text[i] ^ key_array[j]);
        i += 1; j += 1;
        if j == key.len() { j = 0; }
    } xorred
}

// CBC mode to scramble the text
fn cbc(mode: u8, data: &Vec<u8>, power: u32) -> Vec<u8> {
    let size = 2usize.pow(power);           // block size
    if mode == 1 {
        let mut cbc_vec: Vec<u8> = sample(&mut thread_rng(), 1..255, size);
        let mut stuff = data.clone();
        // hex the bytes until the vector has the required length (an integral multiple of block size)
        for _ in 0..power { stuff = stuff.to_hex().into_bytes(); }
        cbc_vec.extend(&stuff);
        for i in size..(stuff.len() + size) {
            cbc_vec[i] = cbc_vec[i] ^ cbc_vec[i-size];      // XOR the current block with previous block
        } cbc_vec
    } else {
        let mut i = data.len() - 1;
        let mut cbc_vec = data.clone();
        while i >= size {
            cbc_vec[i] = cbc_vec[i] ^ cbc_vec[i-size];
            i -= 1; }
        let mut stuff = cbc_vec[size..].to_vec();
        for _ in 0..power {
            stuff = charred(stuff);
        } stuff
    }
}

// Invokes the helper functions and does its shifting thing
fn zombify(mode: u8, data: &Vec<u8>, key: &str) -> Vec<u8> {
    let hexed_key = key.as_bytes().to_hex();
    let mut amount: u8 = 0;
    for byte in hexed_key.as_bytes() {
        amount = amount.wrapping_add(*byte);
    } let mut text: Vec<u8> = data.clone();
    if mode == 1 {  // encrypts the vector of bytes
        // but this won't be useful since the library is meant to only decrypt files (for now)
        text = data.to_hex().into_bytes();
        let stuff = cbc(mode, &text, 3);            // pow(2, 3) = 8 byte blocks
        let shifted_text = shift(&stuff, amount);
        xor(&shifted_text, &key)
    } else {    // decrypts the vector of bytes
        let limit: u8 = 0;
        // shift by (256 - amount) for the reverse process
        amount = limit.wrapping_sub(amount);
        let shifted_text = xor(&text, &key);
        let stuff = shift(&shifted_text, amount);
        charred(cbc(mode, &stuff, 3))
    }
}

// Checks if the big vector contains the small vector slice
fn search(text: &Vec<u8>, word: &str) -> u8 {
    let mut count: u8 = 0;
    if text.len() == 0 { return count; }        // that "Wrong password" thing
    let word_array = word.as_bytes();
    let length = text.len() - word.len() + 1;
    for i in 0..length {
        if text[i..].starts_with(&word_array) { count += 1; }
    } count
}

// This just decrypts the file and counts the word in it (just to simplify things)
fn count_words(file_name: &str, key: &str, word: &str) -> String {
    let contents = fopen(&file_name).1;
    let decrypted = zombify(0, &contents, key);
    search(&decrypted, word).to_string()
}
