## Biographer (v0.5.0)

This is a little project of mine - an utility to remember everyday memories. For now, it puts your stories (with a MD5-hashed filename) into a directory for later viewing. It supports some basic encryption. I've used a simple algorithm to hex and shift the ASCII values in the files, which is similar to a *hexed* 256-char Vigenere cipher using byte-wise XOR and my modified CBC<sup>[1]</sup> (which can also detect incorrect passwords).

Once stored, it doesn't disturb the original story (unless you play around). It decrypts to a temporary file for viewing, which also gets deleted almost immediately. While updating the stories, it just appends your story to the previous story.

There's a SHA-256 hashing function which hashes the password into a local file, so that instead of typing the password every time you write/view some story, you can save it by signing in, but it requires at least one sign-in per session. And, the cool part - you can search through your stories for a specific word (between a range of dates) either using Python or the provided Rust library. Regarding cross-platforms, I've tested it on Windows 8 and Ubuntu, but I'm not sure about other OS (I guess it works for them just as well).

<sup>[1]: **It's not at all secure!**, but that's not my goal either! (at least, not for now). We need confidentiality, not integrity. So, this is just to prevent people from peeking into the stories using text editors. Protecting the stories however, is *(always)* on your side. Well, if someone's really involved, then he'll be able to crack it in a few days.</sup>

### Usage

**The script runs best on Linux terminal** (by which I mean the display, speed, and specifically `KeyboardInterrupt`, which is necessary for navigation throughout the program). Running on IDEs isn't recommended as they expose your password, do it at your risk.

As for Windows users, since your command prompts suck, things work quite (slowly and) differently for you. For example, a `KeyboardInterrupt` almost always terminates the program. So, I had to make use of `EOF` to work around it, which means you have to use <kbd>Ctrl</kbd>+<kbd>Z</kbd> and <kbd>Enter</kbd> instead of <kbd>Ctrl</kbd>+<kbd>C</kbd>.

**Note to the users:** Since I haven't covered all the possible problems that arrive with an user's input, you should try to read everything carefully before you break things up! (like, losing your stories)

### Installation

- Clone the repo.
- It'd be best if you have `python` in your path variable. You can just `cd` into the repo and execute `python Diary.py`.
- If you're really interested in using the Rust library for searching (which is gonna be useful only if you have an appreciable amount of stories already), then download the [nightly version of Rust](http://www.rust-lang.org/install.html) (v1.3.0), `cd` into the folder and run `cargo build --release` and make sure that you're compiling from & for the right architecture (i.e., 32-bit Rust for 32-bit Python)
