extern crate rustc_serialize as serialize;

use std::io::Read;
use std::fs::File;
use std::collections::HashMap;
use serialize::hex::{FromHex, ToHex};

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
    let mut shifted_text = Vec::new();
    let mut shift_by: u8 = 0;
    for byte in text {
        // wrap around the boundary if the sum overflows
        shift_by = amount.wrapping_add(*byte);
        shifted_text.push(shift_by);
    } shifted_text
}

// Byte-wise XOR of vector elements according to a given string
fn xor(text: &Vec<u8>, key: &str) -> Vec<u8> {
    let mut xorred: Vec<u8> = Vec::new();
    let key_vector = key.to_string().into_bytes();
    let (mut i, mut j) = (0, 0);
    while i < text.len() {
        xorred.push(text[i] ^ key_vector[j]);
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
        text = data.to_hex().into_bytes();
    } else if mode == 0 || mode == 2 {
        // yep, this overflows and that's where wrapping_sub() comes in
        let limit: u8 = 256;
        // shift by (256 - amount) for the reverse process
        amount = limit.wrapping_sub(amount);
    } shift(&text, amount)
}

fn main() {
    let mut months = HashMap::new();
    // sigh, no other efficient way...
    months.insert("01", "January");
    months.insert("02", "February");
    months.insert("03", "March");
    months.insert("04", "April");
    months.insert("05", "May");
    months.insert("06", "June");
    months.insert("07", "July");
    months.insert("08", "August");
    months.insert("09", "September");
    months.insert("10", "October");
    months.insert("11", "November");
    months.insert("12", "December");

    let text: Vec<u8> = vec![104, 101, 108, 108, 111];
    let put_in = zombify(1, &text, "pass123");
    println!("{:?}", put_in);
    let got_back = charred(zombify(0, &put_in, "pass123"));
    println!("{:?}", got_back);
    let xor1 = xor(&text, "pass123");
    println!("{:?}", xor1);
    let xor2 = xor(&xor1, "pass123");
    println!("{:?}", xor2);
}
