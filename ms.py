import os
from collections import defaultdict
from optparse import OptionParser

cols = ['pid', 'cmd', 'vsz', 'res', 'shr', 'uss', 'pss', 'swp']

def read_smaps( pid ):
	smaps = open( '/proc/' + str( pid ) + '/smaps' )
	fieldmap = { 'Rss:' : 'res', 'Shared_Clean:' : 'shr', 'Shared_Dirty:' : 'shr', 'Private_Clean:' : 'uss', 'Private_Dirty:' : 'uss', 'Pss:' : 'pss', 'Size:' : 'vsz', 'Swap:' : 'swp' }
	mem = defaultdict( int )
	for line in smaps:
		fields = line.split()
		if fields[0] in fieldmap:
			mem[fieldmap[fields[0]]] += int( fields[1] )

	smaps.close()
	return [mem[x] for x in cols[2:]]

def get_overall_stats():
	totalMem = 0
	freeMem = 0
	sharedMem = 0
	for line in open( '/proc/meminfo' ):
		fields = line.split()
		if fields[0] == 'MemTotal:': totalMem = int( fields[1] )
		elif fields[0] == 'MemFree:': freeMem = int( fields[1] )
		elif fields[0] == 'Shmem:': sharedMem = int( fields[1] )

	return [totalMem, freeMem, sharedMem]

def get_processes():
	procs = []
	for pid in [int( x ) for x in os.listdir( '/proc' ) if x.isdigit()]:
		mem = read_smaps( pid )
		cmd = open( '/proc/' + str( pid ) + '/stat' ).readline().split()[1][1:-1]
		if mem[0]: procs.append( [pid, cmd] + mem )
	return procs

def print_processes( procs ):
	maxes = defaultdict( int )
	for i in range( len( cols ) ):
		maxes[cols[i]] = max( [len( cols[i] )] + [len( str( x[i] ) ) for x in procs] )

	for col in cols:
		print '|', col.upper().center( maxes[col] ),
	print '|\n', '=' * ( sum( [maxes[col] + 3 for col in cols] ) + 1 )

	for p in procs:
		for i in range( len( cols ) ):
			print '|', str( p[i] ).rjust( maxes[cols[i]] ),
		print '|\n',

def print_overall_usage( procs ):
	totalMem = 0
	freeMem = 0
	for line in open( '/proc/meminfo' ):
		fields = line.split()
		if fields[0] == 'MemTotal:': totalMem = int( fields[1] )
		elif fields[0] == 'MemFree:': freeMem = int( fields[1] )

	print 'Total:', totalMem, 'kB'
	print 'Free:', freeMem, 'kB'
	print 'In use:', totalMem - freeMem, 'kB'
	sharedMem = sum( [x[cols.index( 'shr' )] for x in procs] )
	print 'Shared:', sharedMem, 'kB'
	print 'Non-shared:', totalMem - freeMem - sharedMem, 'kB'

if __name__ == '__main__':
	usage = 'usage: %prog [options]\nGet process memory statistics.'
	parser = OptionParser( usage = usage )
	parser.add_option( '-s', '--sort', metavar = 'STATISTIC',
					   help = 'Sort entries based on a particular statistic. Available options are pid, cmd, vsz, res, shr, uss, pss, and swp. Append a + or - to sort ascending or descending order, respectively.' )

	( options, args ) = parser.parse_args()
	if options.sort:
		if len( options.sort ) == 4 and options.sort[:3] in cols and options.sort[-1] in ['+', '-']:
			col = options.sort[:3]
			order = options.sort[-1]
			procs = get_processes()
			procs.sort( key = lambda x: x[cols.index( col )], reverse = False if order == '+' else True )
			print_overall_usage( procs )
			print_processes( procs )
		else:
			parser.print_help()
	else:
		parser.print_help()

