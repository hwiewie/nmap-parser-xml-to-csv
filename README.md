### Script for parsing nmap xml output to csv format
	This script originally by Didier Stevens, modified by Sumedt Jitpukdebodin, changed to a SAX parser by liamosaur
### Version
- 0.1
		- Change some display and fix the bug of parser multiple ports and hosts
- 0.2
		- Rearrange columns and add end time column into output csv.
- 0.3 liamosaur
		- Rewritten to use a SAX XML parser instead of a DOM parser, so it doesn't explode and run out of memory if used on large XML files (from scanning Class B blocks etc)

### How to use
1. Normal usage for display result
./nmap-xml-script-output-modify.py test.xml
2. Change default delimiter(;) to ,
./nmap-xml-script-output-modify.py test.xml -s ,
3. Output to test.csv
./nmap-xml-script-output-modify.py test.xml -s , -o test.csv

For sanity, you may want to filter out "filtered" ports, which I'll probably add a script option for at some stage

Also, since the parser conversion, this hasn't been widely tested on a bunch of environments, so probably contains bugs. 
