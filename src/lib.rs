#![feature(libc)]
extern crate libc;
extern crate rustc_serialize as serialize;

use std::io::Read;
use std::str;
use std::mem;
use std::slice;
use std::ffi::{CStr, CString};
use std::fs::File;
use libc::{size_t, c_char};
use serialize::hex::{FromHex, ToHex};

// FFI function to be called from Python
#[no_mangle]
pub extern fn get_stuff(array: *const *const c_char, length: size_t) -> *const c_char {
    // get the raw pointer values to the strings from the array pointer
    let array = unsafe { slice::from_raw_parts(array, length as usize) };
    let mut stuff: Vec<&str> = array.iter()
        .map(|&p| unsafe { CStr::from_ptr(p) })                 // get the C-type string from the pointer
        .map(|c_string| c_string.to_bytes())                    // convert the raw thing to bytes
        .map(|byte| str::from_utf8(byte).unwrap())              // finally collect the corresponding strings
        .collect();
    let word = stuff.pop().unwrap();
    let key = stuff.pop().unwrap();
    let mut occurrences = Vec::new();
    for file_name in stuff {
        let contents = fopen(&file_name).1;
        let decrypted = charred(zombify(0, &contents, key));
        let count = search(&decrypted, word);
        occurrences.push(count.to_string());
    } let count_string = occurrences.connect(" ");
    let c_string = CString::new(count_string).unwrap().as_ptr();
    println!("{:?}", "Leaking the memory...");
    mem::forget(c_string);                                      // this leaks the memory allocated by c_string
    c_string                                                    // the FFI code should now own the memory
}

// Hexing function
fn hexed(encode: &str) -> String {
    // only as a helper function
    encode.as_bytes().to_hex()
}

// Hex-decoding function
fn charred(decode: Vec<u8>) -> Vec<u8> {
    // Mostly, I try to stick to immutable borrows, but from_utf8() requires Vec<u8>
    let text = String::from_utf8(decode).unwrap();
    // unwrap the values from Ok(value)
    text.from_hex().unwrap()
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

// Invokes the helper functions and does some useful stuff
fn zombify(mode: u8, data: &Vec<u8>, key: &str) -> Vec<u8> {
    let hexed_key = hexed(key);
    let mut amount: u8 = 0;
    for byte in hexed_key.as_bytes() {
        amount = amount.wrapping_add(*byte);
    } let mut text: Vec<u8> = data.clone();
    if mode == 1 {
        // encrypt the thing
        text = data.to_hex().into_bytes();
        let shifted_text = shift(&text, amount);
        xor(&shifted_text, &key)
    } else {
        let limit: u8 = 0;
        // shift by (256 - amount) for the reverse process
        amount = limit.wrapping_sub(amount);
        let shifted_text = xor(&text, &key);
        shift(&shifted_text, amount)
    }
}

// Checks if the big vector contains the small vector slice
fn search(text: &Vec<u8>, word: &str) -> u8 {
    let mut count: u8 = 0;
    let word_array = word.as_bytes();
    let length = text.len() - word.len() + 1;
    for i in 0..length {
        if text[i..].starts_with(&word_array) {
            count += 1;
        }
    } count
}
