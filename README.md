simple-ci
=========

A single-user continuous integration tool for OS X.

While reading James Grenning's ["Test Driven Development for Embedded
C"][embtdd] I noticed a line that said something to the effect of

> every time I save a file, my IDE runs my tests

Well, I loathe IDEs, but I thought this sounded like a pretty cool idea. I
happened to also be playing around with [pymacadmin's `crankd.py`][pymacadmin]
at the same time and realized I could steal some code from there to make a
very simple script that would invoke my `Makefile` every time I saved a file
in [TextMate][tm]. `simple-ci` is the result. It uses OS X's `FSEvents`
facility to watch a directory for changes.

The cleanest way to use it is to add a target to your `Makefile`, like thus:

    ci:
    	/path/to/simple_ci.py . make test

Then invoke the `ci` target in a terminal window. Any time you save a file
anywhere in your project, the `test` target will be invoked.

    ==> Running: make test
    compiling usi_serial.c
    Building archive ../build/lib/libiswba.a
    r - ../build/objs/../main/src/8bit_tiny_timer0.o
    r - ../build/objs/../main/src/ibus_button_adapter.o
    r - ../build/objs/../main/src/ibus_message_parser.o
    r - ../build/objs/../main/src/mute_button.o
    r - ../build/objs/../main/src/relay.o
    r - ../build/objs/../main/src/usi_serial.o
    Linking iswba_tests
    Running iswba_tests
    ....................
    OK (20 tests, 20 ran, 46 checks, 0 ignored, 0 filtered out, 1 ms)
    
    ==> SUCCESS
    ==> ready

I went a little further and added a wrapper script that calls `make test` and
displays a [Growl][growl] alert if the tests fail:

    #!/bin/bash

    make test

    if [ $? -ne 0 ]; then
        growlnotify -a Xcode -n simple-ci -d bravo5.simpleci -t CI -m "BUILD FAILED" 
    fi

You can use this with any project, not just make-driven ones. Run your Python
tests with `nose` or JUnit tests with Maven every time you save a file!

Dependencies
------------

I got carried away and added color. You need the [colorama][colorama] Python
package; just do `sudo easy_install colorama`.

[pymacadmin]: http://code.google.com/p/pymacadmin/ "A collection of Python utilities for Mac OS X system administration"
[embtdd]: http://pragprog.com/titles/jgade/test-driven-development-for-embedded-c "Test Driven Development for Embedded C by James W. Grenning"
[tm]: http://macromates.com/ "the missing editor"
[growl]: http://growl.info/ "Growl"
[colorama]: http://pypi.python.org/pypi/colorama "colorama: Cross-platform colored terminal text."