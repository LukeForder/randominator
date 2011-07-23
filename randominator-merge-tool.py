import sys, re, pprint

def emptyRow(columns):
	return [None for x in range(0,columns)]

def normalise(row, columnCount):
	if (len(row) == columnCount):
		return row
	else:
		#truncate the extra columns or pad with None for missing columns
		return row[:columnCount] if  len(row) > columnCount else row.extend(emptyRow(columnCount - len(row)))

def unpackRow(packedRow, delimiter):
	return packedRow.split(delimiter)

def unpackFile(filePath):
	try:
		row_sets = []
		with open(filePath) as f:
			row_sets = [unpackRow(x, delimiter) for x in f.readlines()]
		
		#get the max number of columns in the rowset
		max_row_length = max( [ len(x) for x in row_sets ] )
		
		if (debug):
			pprint.pprint(row_sets)
		
		#return the normalised rows
		return [ normalise(x, max_row_length) for x in row_sets ]	
		
	except IOError, e:
		print '%% Error: error opening file, {file}, message => {msg}'.format(file=filePath, msg=e)
		sys.exit(1)

def mergeRows(rows):
	merged_row = []
	for row in rows:
		merged_row.extend(row)
	return merged_row

def mergeRowSets(sets):
	#ensure that all the sets are the same size
	max_set_size = max ([len(x) for x in sets])
	
	for set in sets:
		set_size = len(set)
	
		if set_size != max_set_size:
			row_columns = 1 if len(set) == 0 else len(set[0])
			set.extend([emptyRow(row_columns) for x in range(0,int(max_set_size - set_size))])
	
	#merge rows of each set
	resultant_set = []
	
	for idx in range(0,max_set_size):
		resultant_row = []
		for set in sets:
			resultant_row.extend(set[idx])
		resultant_set.append(resultant_row)	#meh	
	
	return resultant_set
	
def getSwitches(argStr):

	space_regex = re.compile(r'\s{1:}')
	regex = re.compile(r'-[fo] (?:[\w\.\:\- ]+ (?!-))+')
	
	matches = regex.findall(argStr)
	for idx in range(0,len(matches)):
		matches[idx] =  space_regex.sub(' ', matches[idx]).strip(' ')
	return matches

def strip_line(line):
	return [x.strip() if x != None else '' for x in line]
	
def write_result(result, output, delimiter):
	if output == 'console':	
		for line in result:
			print delimiter.join(strip_line(line))
	else:
		try:
			with open(output) as f:
				for line in result:
					f.write(delimiter.join(strip_line(line)))
		except IOError,e:
			print "Error: couldn't open fille for output, message => {message}".format(message=e)
	
def help():
	print '%%%		Command Line tool for merging csv files		%%%'
	print 'usage 	{script} -f file1 file3... [ -o output -s delimiter ] '.format(script=sys.argv[0])
	print '-f: List of files to merge'
	print '-o: Output location, default: terminal'	
	print '-s: Item seperator, default: ;'
	sys.exit(1)

#Processing of the files starts here

debug = False

args   = ' '.join(sys.argv)
output = 'console'
files  = []
result = []
delimiter = ";"

if (len(sys.argv) > 1 and ('/d' in sys.argv)):
	debug = True
	sys.argv.remove('/d')
	
if (len(sys.argv) > 1 and ('/?' in sys.argv or '-h' in sys.argv or '-help' in sys.argv)):
	help()

if not '-f' in args:
	help()

if (debug):
	print 'switches = ', getSwitches(args)
	
for switch in getSwitches(args):
	if debug:
		pprint.pprint(switch)

	switch_list = switch.split(' ')
	if '-f' in switch_list:
	
		for file in switch_list[1:]:
			files.append(unpackFile(file))
		result = mergeRowSets(files)
	
	elif '-o' in switch_list:
		output = switch_list[1]
	
write_result(result, output, delimiter)