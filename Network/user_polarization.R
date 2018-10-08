
#toInstall <- c("ggplot2", "scales", "R2WinBUGS", "devtools", "yaml", "httr", "RJSONIO")
#install.packages(toInstall, repos = "http://cran.r-project.org")
library(devtools)
#install_github("pablobarbera/twitter_ideology/pkg/tweetscores")
#install.packages('rjson', repos = "http://cran.r-project.org")
library(rjson)

friends_dir = '/media1/Fakenews/Twitter/crawler/TwitterAPI/Data/friends/friends/'
uid = '805211428575707136'
# load package
library(tweetscores)
# downloading friends of a user
user <- "p_barbera"
#friends <- getFriends(screen_name=user, oauth="~/Dropbox/credentials/twitter")
#friends <- getFriends()
path <- paste(friends_dir, uid, sep='')
#print(path)
friends <- fromJSON(file=path)
#print(friends)

results <- estimateIdeology2(user, friends)
#print(results)
#summary(results)

#read all files from PolarFriends folder

inputdir = 'PolarFriends/'
outputdir = 'PolarUser/'

files = list.files(path=inputdir, pattern = NULL)

friends_dir = '/media1/Fakenews/Twitter/crawler/TwitterAPI/Data/friends/friends/'
for (x in files) {
	print(x)
	path = paste(inputdir, x, sep='')
	output_path = paste(outputdir, x, sep='')

	if (file.exists(output_path)) {
		print('file exist')
		next
	}
	users <- fromJSON(file=path)
	result = 0
	for (user in users) {
		f_path = paste(friends_dir, user, sep='')
		friends <- fromJSON(file=f_path)
		#try({
		#	results <- estimateIdeology2(user, friends)
		#		print(results)
		#})
		tryCatch(
			polarity <- estimateIdeology2(user, friends),
			error = function(e) {
				polarity <- 999
			}
		)
		#print(results)
		result <- rbind(result, c(user, polarity))

	}
	#write file to PolarUser/postid
	write.csv(result, file=output_path)


}


