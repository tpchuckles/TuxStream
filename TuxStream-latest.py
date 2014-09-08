# -*- coding: iso-8859-15 -*-
#version: 1.16. fixed "°" symbol. 
import urllib, time, re, sys, subprocess, platform, random, os
from os import listdir
baseurl = ['tuxtunes.us.to/']
global url
url = list(baseurl)
global runlocally 
runlocally = False
basefilepath = ['/','media/','Media/','Music/']
history = []
nameplay = False #must enable to play songs by filename, rather than only entering directories by name

#find vlcpath based on OS.
if platform.system() == "Linux":
	vlcpath="vlc"
	from BeautifulSoup import BeautifulSoup
elif platform.system() == "Windows": #for windows, the program file directory is determined
	import os
	vlcpath=os.environ['PROGRAMFILES']+"/VideoLAN/VLC/vlc.exe"
	from bs4 import BeautifulSoup
else:
	vlcpath="vlc"
print vlcpath
playlist=[]

#make_audiolist method. makes and returns a list of song urls (minus http://), given a list of folder/file names and indices, by filtering out urls which are not songs. uses the is_audio method. 
def make_audiolist(index1,index2,links):
	tunes=[]
	for x in xrange(index1, index2):
		if is_audio(links[x]):
			tunes.append("".join(url)+links[x] ) #audio files' names are added to the end of the url, and added to the tunes list
	return tunes

#is_audio method. checks a folder/file name for endings indicative of them being audio files. use of is_audio method is prefered for ease of consistent addition of file formats. 	
def is_audio(string):
	if string[-4:] == ".mp3" or string[-4:] == ".MP3" or string[-4:] == "flac" or string[-4:] == ".wav" or string[-4:] == ".m4a" or string[-4:] == ".ogg":
		return True
	return False	

#get_vlccommandlist method. passed a list of tune urls (minus http://), and gets a list of arguments for a command which will be executed. ex. vlc http://url1.mp3 http://url2.mp3 etc. 
def get_vlccommandlist(vlcpath,tunes):
	encoded_urls_command=[vlcpath]
	prefix=""
	for n in range(0, len(tunes)):
		if not runlocally:
			encoded_urls_command.append("http://"+urllib.quote(tunes[n], safe="/"))
		else:
			encoded_urls_command.append((tunes[n]))
	return encoded_urls_command

#print_list method. prints contents of a list. 
def print_list(passedlist):
	for n in range(0,len(passedlist)):
		print str(n+1)+" : "+passedlist[n]

#is_number method. returns true if a string is a number.
def is_number(string):
	try:
		float(string)
		return True
	except ValueError:
		return False

#web page is retrieved and a list of links is extracted from the html
def getlinks(passedurl):
	if runlocally:
		try:
			links = []
			if not passedurl == basefilepath:
				links.append("Parent Directory")
			lines=os.listdir("".join(passedurl))
			lines=sorted(lines)
			
			for file in lines:
				if os.path.isdir("".join(passedurl)+file):
					file=file+"/"
				links.append(file)
			for link in links:
				if link.startswith("."):
					links.remove(link)
		except OSError:
			goodresponse=False
			while not goodresponse:
				subchoice = raw_input('error, '+"".join(passedurl)+' not found, use server mode (S), quit (Q), or change filepath (F)\n').lower()
				if subchoice == "q":
					sys.exit()
				elif subchoice == "s":
					print "using default server: " + "".join(baseurl)
					togglelocal()
					links=getlinks(url)
					goodresponse=True
				elif subchoice == "f":
					desiredurl=raw_input('enter your desired filepath (use absolute path)\n')
					seturl(desiredurl)
					links=getlinks(url)
					goodresponse=True
				else:
					print "that was not an option"
	else:
		try:
			web_page = urllib.urlopen("http://"+urllib.quote("".join(passedurl)))
			page_html = web_page.read()
			web_page.close()
			soup = BeautifulSoup("".join(page_html))
			lines = soup.findAll("a")
			links = []
			i=0
			for href in lines:
				href = str(href)
				href = href[href.find('">')+2:href.find('</')]
				if href != "Name" and href != "Last modified" and href != "Size" 			and href != "Description":
					#special characters are managed
					href = resub(href)
					links.append(href)
		except IOError:
			goodresponse=False
			while not goodresponse:
				subchoice = raw_input('error, '+"".join(passedurl)+' not found, use local mode (L), quit (Q), or change Url (U)\n').lower()
				if subchoice == "q":
					sys.exit()
				elif subchoice == "l":
					print "using default filepath: " + "".join(basefilepath)
					togglelocal()
					links=getlinks(url)
					goodresponse=True
				elif subchoice == "u":
					desiredurl=raw_input('enter your desired url (ignore http://)\n')
					seturl(desiredurl)
					links=getlinks(url)
					goodresponse=True
				else:
					print "that was not an option"
			#done
	return links

def seturl(desiredurl):
	global basefilepath
	global url
	global baseurl
	desiredurl=desiredurl.split('/')
	newurl=[]
	for line in desiredurl:
		newurl.append(str(line)+"/")
	if runlocally:
		basefilepath=list(newurl)
		url=list(basefilepath)
	else:
		baseurl=list(newurl)
		url=list(baseurl)

def togglelocal():
	global url
	global runlocally
	global playlist
	runlocally = not runlocally
	playlist = []
	if runlocally:
		url=list(basefilepath)
	else:
		url=list(baseurl)

#catalog method, returns a list of urls for all song files in a folder, including all subfolders
def catalog(passedurl):
	urls=[]
	links=getlinks(passedurl)
	#links.reverse()response = urllib2.urlopen('http://www.example.com/')
	for n in range(0,len(links)):
		urls.append("".join(passedurl)+links[n])
	dellist=[]
	for n in range(len(urls)-1,-1,-1):
		if urls[n][-1:] != "/" and not is_audio(urls[n]):
			del urls[n]
	for n in range(0,len(urls)):
		#print urls[n]
		if not is_audio(urls[n]):
			print "Folder "+urls[n]+" found, running inside"
			subdir=urls[n]
			dellist.append(n)
			subdircat=catalog(subdir)
			for i in range(0,len(subdircat)):
				urls.append(subdircat[i])
	for n in range(len(urls)-1,-1,-1):
		if n in dellist:
			del urls[n]
	#print_list(urls)
	return urls

#resub method, handles all special characters.
def resub(passedhref):
	passedhref = re.sub('&amp;','&',passedhref)
	passedhref = re.sub('채','ä',passedhref)
	passedhref = re.sub('ĂŠ','é',passedhref)
	passedhref = re.sub('ยบ','º',passedhref)
	passedhref = re.sub('째','°',passedhref)
	return passedhref


print "Welcome to TuxStream! this tool can stream music to your computer from any http server. press \".h\" for command list.\n"
while True: #main while loop continues indefinitely, repeating ach time as users cycle through directory tree and play music etc. 
	print "getting web page..."
	print "".join(url), "\n"	
	links=getlinks(url)
	for i in range(0,len(links)):
		print str(i+1)+" : "+links[i]
	if len(links) == 0:
		print "error. there are no links here. this is likely because of a special character that was not handled properly in the url. please report this to tux.\n"
		subchoice = raw_input('would you like to \"r\" - return up 1 directory, \"b\" - navigate to the base directory, or \"m\" - switch modes (to local file mode)\n').lower()
		if subchoice == "m":
			togglelocal()
		elif subchoice == "r" and len(url) > 1:
			del url[-1]
		elif subchoice == "q":
			sys.exit()
		else:
			print "returning to base directory"
			if runlocally:
				url = list(basefilepath) 
			else:
				url = list(baseurl)
		choice = "fake"
	else:
		choice = raw_input('\n enter your command (\".h\" for help, \".q\" to quit)\n').lower()
	#if user chooses to quit, program is exited. (this is the only way the main while loop is exited
	if choice == ".q" or choice == "quit": 
		sys.exit()
	#if user enters ".h", help dialogue is printed. 
	elif choice == ".h" or choice == "help": 
		print "Standard Commands:\nTo play a song and all of the songs that follow it, simply enter the number of the song.\nTo enter a directory, simply enter the number of the directory or begin typing it's name (if multiple folders beginning with or contain what you entered exist, the first one will be entered). please note that you can enable playing files by typing their name as well, but it is not done by default (type .np to enable it, or edit the nameplay variable to set it permanently). also please be aware of designated commands. \n\n\"1-{n}\" - go up by {n} in the directory tree. the absense of an n value will cause TuxStream to go to the top.\n\".A\" - Album: plays the entire album, ie, all songs in the current directory (same as entering the number of the first song). \n\".s\" - song: plays a single song. you will be prompted again for the song's number. \n\".PA\" - Playlist,Album: adds Album to a playlist. Playlist is not immediately played; you must use the option \".Pp\" to play it. \n\".Ps\" - Playlist,song: adds individual song to playlist. you will be prompted again for the song's number. Playlist is not immediately played; you must use the option \".Pp\" to play it. \n\".PF\" - Playlist,Folder: adds all songs within a folder and all songs within all subfolders to the playlist. Playlist is not immediately played; you must use the option \".Pp\" to play it. \n\".Pm\" - Playlist,modify: enters the playlist modification tool which allows you to delete songs off a playlist, to filter the playist by filetype, or to randomize a playlist\n\".Pl\" - Playlist,list: lists the contents of the playlist\n\".Pp\" - Playlist,play: plays playlist\n\".Pi\" - Playlist,import: import playlist from an m3u file. note that the file must be in the directory of this python script, otherwise the full path must be specified\n\".Pe\" - Playlist,export: export playlist to a file\n\".Pc\" - Playlist,clear: remove all songs from the playlist\n\".pd\" - Playlist,download: download all the files in the playlist\n\".hl\" - history,list: prints history of all files played. this includes those played as part of a playlist\n\".hc\" - history clear: clears history\n\".h\" - help: prints out this help message \n\".q\" - quit.\nSpecial Commands:\n\".m\" - mode. toggles between http mode (streaming off server) and local mode (playing off local files).\n\".np\" - nameplay: sets the nameplay variable to True, allowing files to be played by typing entering their name.\n\".url\" - set url or filepath\n\".Pz\" - does the same thing as executing .PF, .PM(f(flac),r,s).\n"
	#if user chooses to play the entire album, all music files are played. an audio list of all present music files is made. if it has no entries, there is no music, and the user is informed. otherwise, the vlc command is made from the list of audio files and executed.
	elif choice == ".m":
		togglelocal()
	elif choice == ".a":
		tunes=make_audiolist(0,len(links),links)
		if len(tunes) == 0:
			print "there are no recognized audio files here\n"
		else:
			print "Playing entire album:"
			encoded_urls_command=get_vlccommandlist(vlcpath,tunes)
			subprocess.Popen(encoded_urls_command)
			history.extend(tunes)
	#if a user chooses to play a single song, the user is prompted again for the song they wish to play. then their input is used to play the song. they are also given the option to instead choose to go back (accidentally pressed "s"?), and nothing happens (they are returned to the main menu at it's location in the directory structure). otherwise, their choice is checked if it is an audio file. if not, they are informed, and if so, a single-entry tunes list is made, a vlc command is made from it, and executed.  
	elif choice	== ".s":
		subchoice = raw_input('\nenter the index of the song you would like to play, b to go back\n')
		if subchoice != "b":
			if is_number(subchoice) and int(subchoice) <= len(links) and int(subchoice) > 0:
				if is_audio(links[int(subchoice)-1]):
					tunes=make_audiolist(int(subchoice)-1,int(subchoice),links)
					encoded_urls_command=get_vlccommandlist(vlcpath,tunes)
					subprocess.Popen(encoded_urls_command)
					history.extend(tunes)
			else:
				found = False
				for i in range(0,len(links)):
					if (subchoice in links[i].lower()) and is_audio(links[i]):
						print "match"
						tunes=make_audiolist(i,i+1,links)
						encoded_urls_command=get_vlccommandlist(vlcpath,tunes)
						subprocess.Popen(encoded_urls_command)
						history.extend(tunes)
						found = True
						break
				if not found:
					print "that is not a valid option or number, returning to main menu."
				
	#if a user chooses to add an entire album to a playlist, the same actions as if they had chosen to play the album are done, except rather than a vlc command made and executed from the created tunes list, another list (titled playlist) is given each entry of the tunes list. 
	elif choice == ".pa":
		tunes=make_audiolist(0,len(links),links)
		if len(tunes) == 0:
			print "there are no audio files here to add to the playlist\n"
		else:
			print "adding all songs to playlist:"
			tunes=make_audiolist(0,len(links),links)
			for tune in range(0,len(tunes)):
				print "adding "+tunes[tune]+" to playlist"
				playlist.append(tunes[tune])
	#if a user chooses to add a single song to a playlist, the same actions as if they had chosen to play a single song are done, except rather than a vlc command made and execuded fron the created single-entry tunes list, another list (titles playlist) is given the entry of the tunes list.
	elif choice == ".ps":
		subchoice = raw_input('\nenter the index of the song you would like to add to the playlist, b to go back\n')
		if subchoice != "b":
			if is_number(subchoice)  and int(subchoice) <= len(links) and int(subchoice) > 0:
				if is_audio(links[int(subchoice)-1]):
					print "adding "+links[int(subchoice)-1]+" to playlist"
					playlist.append(make_audiolist(int(subchoice)-1,int(subchoice),links)[0])
				else:
					print "that is not an audio file. going back\n"	
			else:
				print "that is not a valid option or number, returning to main menu."
	#if a user chooses PF, to play a folder, songs within a folder, including those in subfolder, are added to a the playlist
	elif choice == ".pf":
		playlist.extend(catalog(url))
		#print_list(playlist)
	#if a user chooses to modify the playlist, they are shown the contents of the playlist, and prompted for the index of the song. when the index is entered, the song is removed from the playlist list, or if "q" is entered, the "playlist modification tool" is closed. 
	elif choice == ".pm":
		print "modifying playlist. \nthis is for deleting songs from the playlist. to add songs, use the \"Ps\" option.\n"
		modifying = True
		while modifying:
			print_list(playlist)
			subchoice=raw_input('please enter the number of the song you would like to delete, or \"s\" to shuffle playlist, \"R\" to remove repeats, \"F\" to filter by filetype, or \"q\" to quit playlist modification utility.\n')
			if subchoice == "q":
				modifying=False
			elif subchoice == "r" or subchoice == "R":
				songlist=[]
				for n in range(len(playlist)-1,-1,-1):
					if str(playlist[n].split("/",-1)[-1]) in songlist:
					#	print "removing "+str(playlist[n].split("/",-1)[-1])
						del playlist[n]
					else:
					#	print "adding "+str(playlist[n].split("/",-1)[-1])
						songlist.append(str(playlist[n].split("/",-1)[-1]))
				print_list(songlist)
			elif subchoice == "s" or subchoice == "S":
				random.shuffle(playlist)
			elif subchoice == "f" or subchoice == "F": 
				subsubchoice=raw_input('please enter the filetype you would like to remove from the playlist (last 4 characters. ex \"flac\", or \".mp3\").\n')
				for n in range(len(playlist)-1,-1,-1):
					if playlist[n][-4:] == subsubchoice:
						del playlist[n]
			elif is_number(subchoice):
				if int(subchoice) < len(playlist) and int(subchoice) > 0:
					print "removing "+playlist[int(subchoice)-1]
					del playlist[int(subchoice)-1]
				else:
					print "that number is out of range"
			else:
				print "that is not an option"
	elif choice == ".pd":
		for n in range(len(playlist)-1,-1,-1):
			print "saving: http://"+urllib.quote(playlist[n], safe="/")+" to: "+playlist[n].split("/")[-1]
			if not os.path.isfile(playlist[n].split("/")[-1]):
				urllib.urlretrieve("http://"+urllib.quote(playlist[n], safe="/"), playlist[n].split("/")[-1])
			else:
				print "skipping "+playlist[n]+", file exists"
	elif choice[:2] == "1-":
		if not is_number(choice.split("-")[1]):
			print "navigating to top of directory tree"
			if runlocally:
				url = list(basefilepath) 
			else:
				url = list(baseurl)
		else:
			if len(url) > int(choice.split("-")[1]):
				print "going up directory structure by " + choice.split("-")[1] + "."
				for n in range(0,int(choice.split("-")[1])):
					del url[-1]
			else:
				print "can't go up by " + choice.split("-")[1] + ", navigating to top of directory tree."
				url = list(baseurl)
				
	#special hidden option that does the same as PF, PM(f(flac),r,s). 
	elif choice == ".pz":
		print "executing PF"
		playlist.extend(catalog(url))
		print "executing PM(f(flac))"
		subsubchoice="flac"
		for n in range(len(playlist)-1,-1,-1):
			if playlist[n][-4:] == subsubchoice:
				del playlist[n]
		print "executing PM(r)"
		songlist=[]
		for n in range(len(playlist)-1,-1,-1):
			if str(playlist[n].split("/",-1)[-1]) in songlist:
				del playlist[n]
			else:
				songlist.append(str(playlist[n].split("/",-1)[-1]))
		print "executing PM(s)"
		random.shuffle(playlist)
	#if a user chooses to have the contents of the playlist displayed, they are, by calling the print_list method on the playlist list. 	
	elif choice == ".pl":
		print "Playlist consists of the following files:"
		print_list(playlist)
		print ""
	#if a user chooses to play the playlist, the playlist is checked. if it is not empty, a vlc command is made from it (same as playing the tunes list for default and Album actions) and executed. if the playlist is empty, the user is informed. 
	elif choice == ".pp":
		if len(playlist) != 0:
			print "playing playlist"
			encoded_urls_command=get_vlccommandlist(vlcpath,playlist)
			subprocess.Popen(encoded_urls_command)
			history.extend(playlist)
		else:
			print "there are no songs in the playlist\n"
	#if a user chooses to import a playlist, they are prompted to enter a file name. this file is then opened, and all urls from inside it are added to the playlist list (minus http://).
	elif choice == ".pi":
		filename=raw_input('\neimporting playlist, enter the full name of the m3u file. not that if it is note in the same folder as this python file, you will need to specify the path to it.\n')
		try:
			f = open(filename)
			lines = f.readlines()
			f.close()
			for n in range(0,len(lines)):
				if lines[n][:4] == "http":
					playlist.append(urllib.unquote(lines[n][7:][:-1]))
		except IOError:
			print "error, that file does not exist"
	#if a user choosed to export a playlist, they are promted to enter a file name. this file is then made and the urls (with http://) are dumped into it. this file will be a .m3u file, and should be able to be played with vlc at any time.	
	elif choice == ".pe":
		#print "to export a playlist, simply play the playlist, and then in vlc, you can save the playlist as a .m3u file. once saved, this playlist can be opened up again at any time with vlc alone.\n"
		filename=raw_input('\nexporting playlist, enter your desired full name for the playlist file\n')+".m3u"
		f = open(filename, 'w')
		f.write("#EXTM3U")
		f.write("\n".join(get_vlccommandlist("",playlist)))
		f.close()
		print "playlist exported to "+filename+", you can play it at any time with vlc"
	#if a user chooses to clear the playlist, a new playlist list is made. this simply overwrites the old playlist list. 
	elif choice == ".pc":
		print "Clearing Playlist"
		playlist=[]
	#if a user chooses to list the play history, the history playlist is plrinted
	elif choice == ".hl":
		print "play history:\n"
		print_list(history)	
	elif choice == ".hc":
		print "Clearing History"
		history = []	
	#if a user chooses to change the url or filepath, they are allowed to enter a new one, which is set as the url or filepath
	elif choice == ".url":
		subchoice=raw_input('local mode: ' + str(runlocally) +'\nenter desired url (or filepath if in local mode). (ignore http://, or use absolute path')
		seturl(subchoice)
	elif choice == ".np":
		nameplay = not nameplay
	#if no special commands are made, the default action is done. if the selection was a directory (as distinguished by ending in a slash), the url is appended with the link on the end of it, entering that directory the next time the main while loop progresses. if the selection was "Parent Directory", the last entry of the url list is removed, moving up a directory the next time the main while loop progresses. If the selection is a file, it is checked to be a music file. if not, the user is informed, and if so, that file, along with any following files are added to a tunes list, which is then played. note that selecting the first audio file in a directory is effectively the same thing as pressing A.
	elif is_number(choice) and int(choice) <= len(links) and int(choice) > 0:
		if links[ int(choice) - 1 ][-1:] == "/":
			url.append( links[ int(choice) - 1 ] )
		else:
			if links[ int(choice) -1 ] == "Parent Directory":
				del url[-1]
			else:
				print links[ int(choice) - 1 ]
				if is_audio(links[int(choice) - 1]):
					tunes=make_audiolist(int(choice)-1,len(links),links)
					encoded_urls_command=get_vlccommandlist(vlcpath,tunes)
					subprocess.Popen(encoded_urls_command)
					history.extend(tunes)
				else:
					print "this is not a music file or directory. try again\n"
	else:
		found = False
		for i in range(0,len(links)):
		#	print "checking: "+links[i]
			if (choice in links[i].lower()) and links[i][-1:] == "/":
				print "found matching folder"
				url.append(links[i])
				found = True
				break
			if (choice in links[i].lower()) and is_audio(links[i]) and nameplay:
				print "found matching file: " + links[i]
				found = True
				print "making tunes between "+str(i)+" "+str(len(links))
				tunes=make_audiolist(i,len(links),links)
				encoded_urls_command=get_vlccommandlist(vlcpath,tunes)
				subprocess.Popen(encoded_urls_command)
				history.extend(tunes)
				break
		if not found:
			print "that is not a valid command/input or folder name\n"
			
		
	


