### Changelog

<sup>The commits (before 0.4.0: Memento) are in the [`scripts`](https://github.com/Wafflespeanut/scripts) repository. I moved it here once the diary became somewhat appealing. In case you wanna check those out, I've provided the links for each version below.</sup>

v0.5.0: Biographer
- Rust library can now be used for searching (without any memory leaks). And, it's damn fast! (by a factor of ~100), even after neglecting *concurrency* (which takes that factor up to ~350 times).
- Added some messages and improved the code structure and interface
- Added options for changing the password and for backing up stories
- Updated the functions with an `EOFError` workaround to support the script on the Windows command prompt
- Fixed some flaws in decryption (which has decreased the searching time by 20%)
- Encryption begins with CBC mode (with blocks of 8 bytes) - just to introduce some randomness in the ciphertext

v0.4.1: [Anecdote](https://github.com/Wafflespeanut/anecdote/tree/6f7a80aa0ad24c299550e84e8d3ec0cf08bcbbc9)
- Improved search to suit the methods written for both Python & Rust
- Replaced the exhaustive date & time with built-in `datetime` objects
- Hashed password & diary location is stored in a configuration file

v0.4.0: [Memoir](https://github.com/Wafflespeanut/Memoir/tree/efc7cd4b15b1840c6b8d0a7c494690834e987cbe)
- Fixed a major flaw in the cipher. All these days, this has been consuming more time & memory. It's now been updated to a mixup of 256-char Caesar cipher and byte-wise XOR
- No longer depends on text editors. It just prints the stories on the screen
- No longer stores passwords, but hashes them (with SHA-256) to allow authentication for a particular session (which means you have to sign-in at the start of every session). While local password storage appeals our minds, it was a *really* bad move!

v0.3.0: [Remembrancer](https://github.com/Wafflespeanut/scripts/tree/be3b51c14c5e708baa4003adf3346f51f5720529/Remembrancer)
- Smart search for specific words in stories
- Old tree-node method is now deprecated. All stories are now present in the specified directory
- Story names are hashed with MD5 (to obscure the file names)

v0.2.2: [Memorandum](https://github.com/Wafflespeanut/scripts/tree/8850c831c10955b5c32d2710abfbfef916031792/Memorandum)
- Passwords can be stored locally (after 10-layer hexing)
- Write stories for someday you've missed
- Sign-in / Sign-out options for easier use

v0.2.1: [Souvenir](https://github.com/Wafflespeanut/scripts/tree/937d48dc3bc8608530253fc392594a90a4d59078/Memento)
- View random stories
- TEMP is deleted after a timeout (to keep things safe)
- One-time password for updating stories
- Fixed a faulty code in encryption
- Can detect incorrect passwords

v0.2.0: [Memento](https://github.com/Wafflespeanut/scripts/tree/7f2572857bbe86b2598d27ab7872017a580351ff/Memento) *(has some bugs)*
- Added a simple encryption method which hexes and shifts the ASCII values (to make it really "private" - further protection is of your own)
- Added a function for viewing stories on a given day
- A TEMP file is created for viewing/updating any story, leaving the original files undisturbed

v0.1.0: [Private Diary](https://github.com/Wafflespeanut/scripts/tree/64a9c8dd2470ec309a439a41568778187bbe8bb7/Private%20Diary)
- Creates timestamped folders and text files for stories
- Writes the stories for every [RETURN] stroke, which indicates a paragraph
