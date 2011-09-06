
def uglyParse(needle, haystack, occurence = 0):
	i = -1
	if (len(needle) != 1):
		for (index, byte) in enumerate(haystack):
			if (byte == needle[0] and (haystack[index+1] == needle[1])):
				i += 1
				if (i == occurence):
					return haystack[index+3:haystack[index+2]+index+3]
	else:
		for (index, byte) in enumerate(haystack):
			if (byte == needle[0]):
				i += 1
				if (i == occurence):
					return haystack[index+2:haystack[index+1]+index+2]
	return []
				
		