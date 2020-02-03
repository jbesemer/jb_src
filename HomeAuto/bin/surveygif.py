import os, re, sys, string

names= {}

# sleazy but ok for today:

rx = re.compile( '\<img\Wsrc="([^"]+)' )

def scan( filename ):
	print filename + ":",

	f = file( filename )

	for line in f:
		r = rx.search( line )
		if r:
			for g in r.groups():
				if g in names:
					names[ g ] += 1
				else:
					names[ g ] = 1
		

	f.close()

	print

for filename in sys.argv[1:]:
	scan( filename )

for name,count in names.items():
	print name, count
