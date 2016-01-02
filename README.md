## Biographer (v0.6.2)

A command-line utility to remember everyday memories. This is an on-going project of mine, and so it's unstable. I play with it during my free time (or whenever I get a new idea)...

### How it works?

It puts your stories (with a MD5-hashed filename) into a directory for later viewing. Once stored, it never disturbs the original story (unless you play around). While updating the stories, it just appends your story to the previous story.

It supports some basic encryption. I've used a simple algorithm to hex and shift the ASCII values in the files, which can be "phrased" as a *hexed* 256-char Vigenère cipher using byte-wise XOR along with [CBC](https://en.wikipedia.org/wiki/Block_cipher_mode_of_operation#Cipher_Block_Chaining_.28CBC.29)<sup>[1]</sup> (which can detect incorrect passwords).

A local file has a SHA-256 hash of the original password, so that instead of typing the password every time you interact with the application, you can simply sign in and do your stuff. Basically, it asks you for your password at least once in every session *(of course!)*.

The cool part is that you can search through your stories for a specific word (between a range of dates) either using Python (which takes some time, depending on the number of stories you have) or the provided Rust library ([which amplifies the performance by a factor of ~100](https://wafflespeanut.github.io/blog/2015/07/08/a-pythonist-getting-rusty-these-days-dot-dot-dot-part-2/)). Note that it's just a basic (case-sensitive) search.

Regarding cross-platforms, I've tested it on Windows 8 and Ubuntu, but I'm not sure about other OS (I guess it works for them just as well). Oh, and it also runs on Android (if you've got [QPython](https://play.google.com/store/apps/details?id=com.hipipal.qpyplus)) installed.

<sup>[1]: **It's not much secure!**, but that's not my goal either! We need confidentiality, not integrity. So, this is just to prevent people from peeking into the stories using text editors. Protecting the stories however, is *(always)* on your side. Well, if someone's really involved, then he'll be able to crack it in a few days.</sup>

### Installation

- Clone the repo (or download the zip). **Note that you'll need Python first!**
- It'd be best if you have `python` in your path environment variable. You can just execute `python /path/to/biographer`.
- If you're really interested in using the Rust library for searching (which is gonna be useful only if you have some appreciable amount of stories already), then download the [nightly version of Rust](http://www.rust-lang.org/install.html), `cd` into the folder and run `cargo build --release` and make sure that you're compiling from and for the right architecture (i.e., 32-bit Rust for 32-bit Python)
- It supports all the options in command-line, if you wanna do everything in the fly! Try running `python /path/to/biographer --help`

### Note on usage

**The script runs best on Linux terminal** (by which I mean the display, speed, and specifically `KeyboardInterrupt`, which is necessary for navigation throughout the program). Running on IDEs isn't recommended as they may echo your password (even IDLE does that), and so [do it at your own risk!](https://en.wikipedia.org/wiki/Shoulder_surfing_%28computer_security%29)

As for Windows users, since your command prompt *sucks*, things are quite *weird* for you. For example, when you're about to write in the command prompt, the usual `KeyboardInterrupt` with <kbd>Ctrl</kbd>+<kbd>C</kbd> almost always terminates the program (as they're being *asynchronous*). So, I had to make use of `EOFError` to work around it, which means you have to use <kbd>Ctrl</kbd>+<kbd>Z</kbd> and <kbd>Enter</kbd> instead of <kbd>Ctrl</kbd>+<kbd>C</kbd> once you've finished writing.
