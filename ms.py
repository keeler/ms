import os
from collections import defaultdict
cols = ['pid', 'cmd', 'total', 'res', 'shr', 'uss', 'pss', 'swp']

def read_smaps( pid ):
	smaps = open( '/proc/' + pid + '/smaps' )
	fieldmap = { 'Rss:' : 'res', 'Shared_Clean:' : 'shr', 'Shared_Dirty:' : 'shr', 'Private_Clean:' : 'uss', 'Private_Dirty:' : 'uss', 'Pss:' : 'pss', 'Size:' : 'total', 'Swap:' : 'swp' }
	mem = defaultdict( int )
	for line in smaps:
		fields = line.split()
		if fields[0] in fieldmap:
			mem[fieldmap[fields[0]]] += int( fields[1] )

	smaps.close()
	return [mem[x] for x in cols[2:]]

procs = []
for pid in [x for x in os.listdir( '/proc' ) if x.isdigit()]:
	mem = read_smaps( pid )
	cmd = open( '/proc/' + pid + '/stat' ).readline().split()[1][1:-1]
	if mem[0]: procs.append( [pid, cmd] + mem )

maxes = defaultdict( int )
for i in range( len( cols ) ):
	maxes[cols[i]] = max( [len( cols[i] )] + [len( str( x[i] ) ) for x in procs] )

for col in cols:
	print '|', col.upper().center( maxes[col] ),
print '|\n', '=' * ( sum( [maxes[col] + 3 for col in cols] ) + 1 )

procs.sort( key = lambda x: x[1] )
for p in procs:
	for i in range( len( cols ) ):
		print '|', str( p[i] ).rjust( maxes[cols[i]] ),
	print '|\n',

