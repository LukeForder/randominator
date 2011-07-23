import urllib2, sys, re, pprint, BeautifulSoup, urllib
script_name = sys.argv[0]	#holds the script name

#function:		performs debug printing
def printDebug():
	print('%%%% After processing the program parameters having the following values %%%%')
	print('output = ' + output)
	print('generator = ' + generator_url)

	if (config == {}):
		print('config = ' + 'empty')
	else:
		print('config:')
		pprint.pprint(config)
		
	print('behaviour = ' + behaviour)

#function:	flattens cmd vars to string then process with reg ex
def getSwitches():
	args = ' '.join(sys.argv[1:])
	
	space_regex = re.compile(r'\s{1:}')
	regex = re.compile(r'-[gocnb] [\w\.\: ]+')
	
	matches = regex.findall(args)
	for idx in range(0,len(matches)):
		matches[idx] =  space_regex.sub(' ', matches[idx]).strip(' ')
	return matches

#function 	<obselete>	validates data
#param		<list>		list of data to validate (length > 1)
def isDataValid(list):
	if (debug):
		print(';;'.join(list))
		
	return False if (len(list) < 2) else True	

#function:			prints message to terminal
#param	<msgList>	list of messages to print to terminal
def printMsg(msgList):
	print('%% {msg}'.format(msg=msgList[0]))
	for additional in msgList[1:]:
		print('%% {msg}'.format(msg=additional))
	
#function:		prints a warning to terminal
#param	<msg>	list of strings to print to terminal
def warning(msg):
	msg[0] = 'Warning:: {msg}'.format(msg=msg[0])
	printMsg(msg)

#function:		prints error to terminal and exits script
#param	<msg>	list of strings to print to terminal
def exitWithError(msg):
	msg[0] = 'Error:: {msg}'.format(msg=msg[0])
	printMsg(msg)
	sys.exit(1)

#writes result to appriorite stream
def writeOutput(stream, msg):
	if (debug):
		print "writeOutput" 
		print msg 
		print

	if (stream == 'console'):
		for line in msg:
			print(line)
	else:
		try:
			with open(stream) as f:
				for line in msg:
					f.write("{line}\n".format(line=line))
		except IOError as e:
			exitWithError(e)

def buildResults(html, number):
	result_set = re.split('<P>|<BR>', html.find('textarea', {'name':'printholder'}).contents[0])
	
	result_set = [ x.strip() for x in result_set]
	result_set = set(result_set)
	result_set = [x for x in result_set if not x is u'' ]  
	return result_set
	
#Main method starts here
generator_url = 'animepower'
output = 'console'
behaviour = 'none'
config = {}
debug = False

if (len(sys.argv) > 1 and ('/d' in sys.argv)):
	debug = True
	sys.argv.remove('/d')

if (len(sys.argv) > 1 and ('/?' in sys.argv or '-h' in sys.argv or '-help' in sys.argv)):
	print('%%%	Command Line access for http://www.seventhsanctum.com	%%%')
	print('Flags:')
	print(' -g <generator>: the generator to use -- default: animepower')
	print(' -o <outfile>: the path to write to -- default: console')
	print('	-c <configParam1, configParam2...> -- default: no params')
	print('	-n <numberToGenerate> -- default: 1')
	print(' -b [error|warn|none]\n\t-- behaviour when config param mismatch occurs; default: none')	
	print(' example: scraper.py -g vampnamer -n 5 -c selGenType:SEEDM -b error ')
	print('\tGenerate 5 Modern - Male vampire names')
	sys.exit(1)

for switch in getSwitches():
	switch = switch.split(' ')
	
	#this should never execute as the regex should filter out all switches without data -- here for completeness
	if (not isDataValid(switch)):
		warning(['You used the switch {switch} but did not specify a valid argument\n\t--run {script} /? for more information'.format(switch=switch[0], script=script_name)])
		continue
		
	if ('-g' in switch):
		generator_url = switch[1]
		
	elif ('-o' in switch):
		output = switch[1]
		
	elif('-n' in switch):
		try:
			if (debug):
				print 'processing -n'
				
			config['selGenCount'] = switch[1]
		except ValueError:
			warning(
				[	'Failed to convert {switch} parameter "{data}" to integer'.format(switch=switch[0], data=switch[1]),
					'%% Using default: 1\n'
				])
			config['selGenCount'] = 1
			
	elif('-b' in switch):
		behaviour_enum = ['none','error','warning']
		if (not switch[1] in behaviour_enum):
			warning(['Value {data} is not a valid behaviour'.format(data=switch[1]),
			 'Valid behaviours include: {enum}'.format(enum=' '.join(behaviour_enum)),
			 'Using "none" behaviour\n'
			])
		
	elif('-c' in switch):
		config_options = {}
		for option in switch[1:]:
			(key, param) = option.split(':')[0:2]
			if (key is None):
				warning(['The option, "{option}", has an empty key, "{key}"'.format(option=option, key=key)])
				continue
			if (option is None):
				warning(['The option, "{option}", has an empty setting, "{setting}"'.format(option=option, setting=param)])
				continue
			config_options[key] = param
		config.update(config_options)
		
if (debug):
	printDebug()
	print('\nBeginning web request')
	
try:
	full_url = "http://www.seventhsanctum.com/generate.php?Genname={generator}".format(generator=generator_url)
	request = urllib2.Request(full_url)
	response = urllib2.urlopen(request)
	
	html = 	BeautifulSoup.BeautifulSoup(str(response.read())) 	#deal with the encoding error
	if ('Error finding configurations.' in html):
			exitWithError(["Couldn't find generator with name, {gen_name}".format(gen_name=generator_url)])
	
	# successfully got a get response from the server, so start parsing the result page
	generation_options = {}						#holds select html options for the POST data
	
	selects = html.findAll('select')
	
	if (debug):
		pprint.pprint([x['name'] for x in selects])
	
	#construct a dictionary holding the default generation options from the web page
	for generation_param in selects:
		name = generation_param['name']
		if (debug):
			print("name = {name:15}".format(name = name))
			
		selected_option = generation_param.find('option', selected="selected")
		if (selected_option == None):
			selected_option = generation_param.find('option')
		if (debug):
			print ("selection_option = {option:15}".format(option = str(selected_option)))
		
		if (selected_option != None):
			selected_option_value = selected_option['value']
			if (debug):
				print("selected_option_value = {value:15}".format(value = selected_option_value))
				print
		else:
			warning(["Couldn't find the selected option for param, {param}, skipping set".format(param = name)])
			continue
		generation_options[name] = selected_option_value
	
	if (debug):
		pprint.pprint(generation_options)
		print
		
	#replace default values in dictionary with those specified in -c switch
	for key in config.keys():
		#config option is not in generation options
		if (not key in generation_options.keys()):
			error_msg =['Attempting to configure request with invalid param, {param}, valid options are {params}'.format(param=key, params=', '.join(generation_options.keys()))]
			if (behaviour == 'error'):
				exitWithError(error_msg)
			else:
				warning(error_msg)
				continue
		
		generation_options[key] = config[key] #override the default with the users
	
	
	#construct the POST data for the query
	post_data = urllib.urlencode(generation_options)
	
	if (debug):
		print(post_data)
	
	#run the query
	request = urllib2.Request(full_url, post_data)
	response = urllib2.urlopen(request)
	html = BeautifulSoup.BeautifulSoup(response.read())
	
	#parse the result
	result_set = buildResults(html, config['selGenCount'])
	
	#write the result to file
	writeOutput(output, result_set)
	
except urllib2.URLError, e:
	exitWithError([e])