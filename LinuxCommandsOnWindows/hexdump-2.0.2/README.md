HEXDUMP.EXE FOR WINDOWS
---------------------------

A simplified version of the Linux utility to display file contents in hexadecimal.

	>hexdump -h
	Usage: hexdump [OPTION]... [FILE]
	Display contents of FILE in hexadecimal.
	With no FILE, read standard input.
	 -C Canonical hex+ASCII display: add display of bytes as printable ASCII chars
	 -H add ASCII display with escaped Html entities (e.g. '&' --> '&amp;')
	 -R add display of bytes in Raw format
	 -V display version information and exit
	 -h display this help and exit
 
	>hexdump abc.txt
	000000  61 62 63

	>hexdump mexico-utf8.txt
	000000  4f 6c c3 a1 20 6d 75 6e 64 6f 20 4d c3 a9 78 69
	000010  63 6f 20 3c 26 3e 0d 0a	

The original file is the string `Olá mundo México <&>` followed by a new line.

Canonical hex + ASCII display

	>hexdump -C mexico-utf8.txt
	000000  4f 6c c3 a1 20 6d 75 6e 64 6f 20 4d c3 a9 78 69  Ol.. mundo M..xi
	000010  63 6f 20 3c 26 3e 0d 0a                          co <&>..
	
	
Do for multiple files. Here are 3 different variants of encodings and line endings.

	>for %f in (mexico*.txt) do @echo %f & hexdump -C %f
	mexico-latin1.txt
	000000  4f 6c e1 20 6d 75 6e 64 6f 20 4d e9 78 69 63 6f  Ol. mundo M.xico
	000010  20 3c 26 3e 0d 0a                                 <&>..
	mexico-utf8-bom-unix.txt
	000000  ef bb bf 4f 6c c3 a1 20 6d 75 6e 64 6f 20 4d c3  ...Ol.. mundo M.
	000010  a9 78 69 63 6f 20 3c 26 3e 0a                    .xico <&>.
	mexico-utf8.txt
	000000  4f 6c c3 a1 20 6d 75 6e 64 6f 20 4d c3 a9 78 69  Ol.. mundo M..xi
	000010  63 6f 20 3c 26 3e 0d 0a                          co <&>..
	
In a batch file, replace `%f` with `%%f`.
	
Escape HTML entities in canonical display

Useful if you are copying and pasting into an HTML web page

	>hexdump -H mexico-utf8.txt
	000000  4f 6c c3 a1 20 6d 75 6e 64 6f 20 4d c3 a9 78 69  Ol.. mundo M..xi
	000010  63 6f 20 3c 26 3e 0d 0a                          co &lt;&amp;&gt;..

Display raw bytes

	>hexdump -R mexico-latin1.txt
	000000  4f 6c e1 20 6d 75 6e 64 6f 20 4d e9 78 69 63 6f  Olß mundo MÚxico
	000010  20 3c 26 3e 0d 0a                                 <&>..

This displays the raw bytes on the right, which may not display so good on a Windows console, but you can redirect to a new file.

	hexdump -R mexico-latin1.txt > mexico-latin1.out
	
Read from standard input

	>type 1-23.txt
	12345678901234567890123

	>type 1-23.txt | hexdump -C
	000000  31 32 33 34 35 36 37 38 39 30 31 32 33 34 35 36  1234567890123456
	000010  37 38 39 30 31 32 33                             7890123

	>echo abc | hexdump -C
	000000  61 62 63 20 0a                                   abc .

Note the extra LF character added by `echo` in Windows.
	
	
David Ireland  
DI Management Services Pty Ltd  
Australia  
<http://www.di-mgt.com.au/contact/>  
First published 2010-05-10. Version 2.0.2 compiled 2021-06-28.	
