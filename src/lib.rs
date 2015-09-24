#![feature(scoped, cstr_memory)]
#![allow(unused_imports, deprecated)]

extern crate libc;
mod cipher;

use std::io::Read;
use std::{str, slice, thread};
use std::ffi::{CStr, CString};
use std::fs::File;
use std::sync::mpsc;
use libc::{size_t, c_char};

const NTHREADS: usize = 4;

// You'll be needing Nightly rust, because `from_ptr` is unstable and `thread::scoped` is deprecated
// and so, stable version is unhelpful (for now)

// FFI function just to kill a transferred pointer
#[no_mangle]
pub extern fn kill_pointer(p: *const c_char) {
    unsafe { CString::from_ptr(p) };     // Theoretically, Rust should take the ownership back
}   // variable goes out of scope here and the C-type string should be destroyed (at least, that's what I hope)

// FFI function to be called from Python (I've commented out some of the methods I had tried)
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
    //
    // let occurrences: Vec<String> = stuff.into_iter().map(|file_name| {
    //     count_words(&file_name, &key, &word)        // just the usual iteration (decreases the time by a factor of 100)
    // }).collect();                                   // (useful for less-intensive computations)
    //
    // let threads: Vec<_> = stuff.into_iter().map(|file_name| {
    //     thread::spawn(move || {                     // concurrency could be very helpful here
    //         count_words(&file_name, &key, &word)    // since CBC mode requires some intensive computation
    //     })       // decreases the time by a factor of 111
    // }).collect();
    // let occurrences: Vec<_> = threads.into_iter().map(|handle| handle.join().unwrap()).collect();
    //
    let stuff_per_thread = stuff.len() / NTHREADS;      // let's try parallelization
    let threads: Vec<_> = stuff.chunks(stuff_per_thread).map(|chunk| {
        thread::scoped(move || {            // `scoped` is what we want here, because
            chunk.iter()                    // it will join the threads as the thing gets dropped
                .map(|file_name| count_words(&file_name, &key, &word))
                .collect::<Vec<String>>()       // giving some chunk for each thread
        })      // decreases the time by a factor of 230
    }).collect();
    let mut occurrences = Vec::new();
    for chunk in threads { occurrences.extend(chunk.join()); }
    //
    // let (tx, rx) = mpsc::channel();
    // let threads: Vec<_> = stuff.into_iter().map(|file_name| {
    //     let tx = tx.clone();        // channels have almost the same performance
    //     thread::spawn(move || {     // send() the results as soon as it's done and recv() them later
    //         tx.send(count_words(&file_name, &key, &word)).unwrap()
    //     })       // decreases the time by a factor of 140
    // }).collect();
    // let occurrences: Vec<_> = threads.into_iter().map(|_| rx.recv().unwrap()).collect();
    //
    let count_string = occurrences.connect(" ");
    CString::new(count_string).unwrap().into_ptr()      // the FFI code should now own the memory
}

// Gives a tuple of a file's size and a vector of its contents
fn fopen(path: &str) -> (usize, Vec<u8>) {
    let file = File::open(path);
    let mut contents: Vec<u8> = Vec::new();
    // of course, assuming that there won't be any problem in reading the file
    let file_size = file.unwrap().read_to_end(&mut contents).unwrap();
    (file_size, contents)
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
fn count_words(file_name: &str, key: &str, word: &str) -> String {      // <checklist> take an array of &str instead
    let contents = fopen(&file_name).1;
    let decrypted = cipher::zombify(0, &contents, key);
    search(&decrypted, word).to_string()
}
