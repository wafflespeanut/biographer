### Checklist for next versions:

- [x] Statistics for stories
- [ ] Parallelize searching (and other time-consuming stuff) in Python
- [ ] Timestamp at the start of every story could compromise the cipher! (Idea: Implement AES in Python & Rust)
- [ ] Persuade the searching functions to help with pretty printing
- [ ] Update Rust library to change the password
- [ ] Add unit tests & benchmark tests

### Changelog

<sup>The commits before 0.4.0 (Memento) are in the [`scripts`](https://github.com/Wafflespeanut/scripts) repository. I moved it here once the diary became somewhat interesting & appealing. In case you wanna check those out, I've provided the links for each version below.</sup>

**[0.6.2]()**: *Biographer*
- You can now get statistics for your stories!

**[0.6.1](https://github.com/Wafflespeanut/biographer/tree/04fc89a32d6e4607244bde4919bf4975358f13c5)**: *Biographer*
- Added command-line options for everything - which means you can now invoke writing, viewing, searching or whatever you wanna do, just by passing those as another argument!

**[0.6.0](https://github.com/Wafflespeanut/biographer/tree/1715b86ef9796075a48f07e741ca8e1953c12749)**: *Biographer*
- Rewrote the entire program using objects, thereby cleaning up *seven hells* of garbage code! (I've just realized that *readability* is more important compared to performance, as the latter can always be improved)
- Fixed a number of flaws that had popped up in recent versions (especially while changing the password)
- Fixed the cipher algorithm which has reduced Python's time for searching (but, a recent deprecation in the standard Rust library has brought its searching time down - now, it's only ~100 times faster than Python)
- Added an option for printing search results in both ugly and pretty ways

**[0.5.1](https://github.com/Wafflespeanut/biographer/tree/ae9683ecfa9b97754dca6e5aed82c75408368288)**: *Biographer*
- Added support for QPython in Android
- Fixed a bug that pops up while using concurrency for searching
- Search results now show a slice of the output while printing (costs some time while printing the output)

**[0.5.0](https://github.com/Wafflespeanut/biographer/tree/36eba8decfa823b706bb1568c096643b750952a2)**: *Biographer* (stable)
- Rust library can now be used for searching (without any memory leaks). And, it's damn fast! (by a factor of ~50), even before including *concurrency* (which amplifies the factor further up to <s>~230</s> ~100).
- Improved the code structure, interface & searching
- Added a variety of options from changing the password to backing up stories
- Updated the functions with an `EOFError` workaround to support the script on the Windows command prompt
- Fixed some flaws in decryption (which has decreased the searching time by 20%)
- Encryption begins with CBC mode (with blocks of 8 bytes) - just to introduce some randomness in the ciphertext

**[0.4.1](https://github.com/Wafflespeanut/biographer/tree/4ec5ee2988456786a11236de0de5070d8107d1b6)**: *Anecdote*
- Improved search to suit the methods written for both Python & Rust
- Replaced the exhaustive date & time with built-in `datetime` objects
- Hashed password & diary location is stored in a configuration file

**[0.4.0](https://github.com/Wafflespeanut/biographer/tree/1cc5613fbf91433e5f9f4a6625599b6da984b460)**: *Memoir*
- Fixed a major flaw in the cipher. All these days, this has been consuming more time & memory. It's now been updated to a mixup of 256-char Caesar cipher and byte-wise XOR
- No longer depends on text editors. It just prints the stories on the screen
- No longer stores passwords, but hashes them (with SHA-256) to allow authentication for a particular session (which means you have to sign-in at the start of every session). While local password storage appeals our minds, it was a *really* bad move!

**[0.3.0](https://github.com/Wafflespeanut/scripts/tree/be3b51c14c5e708baa4003adf3346f51f5720529/Remembrancer)**: *Remembrancer*
- Smart search for specific words in stories
- Old tree-node method is now deprecated. All stories are now present in the specified directory
- Story names are hashed with MD5 (to obscure the file names)

**[0.2.2](https://github.com/Wafflespeanut/scripts/tree/8850c831c10955b5c32d2710abfbfef916031792/Memorandum)**: *Memorandum*
- Passwords can be stored locally (after 10-layer hexing)
- Write stories for someday you've missed
- Sign-in / Sign-out options for easier use

**[0.2.1](https://github.com/Wafflespeanut/scripts/tree/937d48dc3bc8608530253fc392594a90a4d59078/Memento)**: *Souvenir*
- View random stories
- TEMP is deleted after a timeout (to keep things safe)
- One-time password for updating stories
- Fixed a faulty code in encryption
- Can detect incorrect passwords

**[0.2.0](https://github.com/Wafflespeanut/scripts/tree/7f2572857bbe86b2598d27ab7872017a580351ff/Memento)**: *Memento*
- Added a simple encryption method which hexes and shifts the ASCII values (to make it really "private" - further protection is of your own)
- Added a function for viewing stories on a given day
- A TEMP file is created for viewing/updating any story, leaving the original files undisturbed

**[0.1.0](https://github.com/Wafflespeanut/scripts/tree/64a9c8dd2470ec309a439a41568778187bbe8bb7/Private%20Diary)**: *Private Diary*
- Creates timestamped folders and text files for stories
- Writes the stories for every [RETURN] stroke, which indicates a paragraph
