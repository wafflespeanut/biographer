### Changelog

<sup>The commits (before 0.4.0: Memento) are in the [`scripts`](https://github.com/Wafflespeanut/scripts) repository. I moved it here once the diary became somewhat appealing. In case you wanna check those out, I've provided the links for each version below.</sup>

**[v0.5.1](https://github.com/Wafflespeanut/biographer/tree/7bdbf77879bd4e33544f9d13aaaf3ecda35ab054)**: *Biographer*
- Added support for QPython in Android
- Fixed a bug that pops up while using concurrency for searching
- Search results now show a slice of the output while printing (costs some time while printing the output)

**[v0.5.0](https://github.com/Wafflespeanut/biographer/tree/c53ba745359424c991d089073bd7891f88e547d6)**: *Biographer* (stable)
- Rust library can now be used for searching (without any memory leaks). And, it's damn fast! (by a factor of ~100), even before including *concurrency* (which amplifies the factor up to ~230).
- Improved the code structure, interface & searching
- Added a variety of options from changing the password to backing up stories
- Updated the functions with an `EOFError` workaround to support the script on the Windows command prompt
- Fixed some flaws in decryption (which has decreased the searching time by 20%)
- Encryption begins with CBC mode (with blocks of 8 bytes) - just to introduce some randomness in the ciphertext

**[v0.4.1](https://github.com/Wafflespeanut/biographer/tree/6f7a80aa0ad24c299550e84e8d3ec0cf08bcbbc9)**: *Anecdote*
- Improved search to suit the methods written for both Python & Rust
- Replaced the exhaustive date & time with built-in `datetime` objects
- Hashed password & diary location is stored in a configuration file

**[0.4.0](https://github.com/Wafflespeanut/biographer/tree/efc7cd4b15b1840c6b8d0a7c494690834e987cbe)**: *Memoir*
- Fixed a major flaw in the cipher. All these days, this has been consuming more time & memory. It's now been updated to a mixup of 256-char Caesar cipher and byte-wise XOR
- No longer depends on text editors. It just prints the stories on the screen
- No longer stores passwords, but hashes them (with SHA-256) to allow authentication for a particular session (which means you have to sign-in at the start of every session). While local password storage appeals our minds, it was a *really* bad move!

**[v0.3.0](https://github.com/Wafflespeanut/scripts/tree/be3b51c14c5e708baa4003adf3346f51f5720529/Remembrancer)**: *Remembrancer*
- Smart search for specific words in stories
- Old tree-node method is now deprecated. All stories are now present in the specified directory
- Story names are hashed with MD5 (to obscure the file names)

**[v0.2.2](https://github.com/Wafflespeanut/scripts/tree/8850c831c10955b5c32d2710abfbfef916031792/Memorandum)**: *Memorandum*
- Passwords can be stored locally (after 10-layer hexing)
- Write stories for someday you've missed
- Sign-in / Sign-out options for easier use

**[v0.2.1](https://github.com/Wafflespeanut/scripts/tree/937d48dc3bc8608530253fc392594a90a4d59078/Memento)**: *Souvenir*
- View random stories
- TEMP is deleted after a timeout (to keep things safe)
- One-time password for updating stories
- Fixed a faulty code in encryption
- Can detect incorrect passwords

**[v0.2.0](https://github.com/Wafflespeanut/scripts/tree/7f2572857bbe86b2598d27ab7872017a580351ff/Memento)**: *Memento*
- Added a simple encryption method which hexes and shifts the ASCII values (to make it really "private" - further protection is of your own)
- Added a function for viewing stories on a given day
- A TEMP file is created for viewing/updating any story, leaving the original files undisturbed

**[v0.1.0](https://github.com/Wafflespeanut/scripts/tree/64a9c8dd2470ec309a439a41568778187bbe8bb7/Private%20Diary)**: *Private Diary*
- Creates timestamped folders and text files for stories
- Writes the stories for every [RETURN] stroke, which indicates a paragraph
