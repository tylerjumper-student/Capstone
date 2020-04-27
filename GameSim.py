import csv
import sys
import pandas as pd
from enum import Enum
from numpy.random import choice

class Algo(Enum):
    bean = 1
    wiss = 2
    wood = 3
    none = 4

class Batter():
    def __init__(self):
        self.name=""
        self.PA=""  
        self.pSingle=""
        self.pDouble=""
        self.pTriple=""
        self.pHR=""
        self.pTw=""
        self.pK=""
        self.pOut=""
        self.totBags="" 
        self.avg="" 
        self.sb=""  

class Pitcher():
    def __init__(self):
        self.name=""
        self.TBF=""
        self.pSingle=""
        self.pDouble=""
        self.pTriple=""
        self.pHR=""
        self.pTw=""
        self.pK=""
        self.pOut=""

        #reads csvfiles and puts the data into a pandas dataframe
        #returns the three dataframes
def readData():
    batterDF = pd.read_csv("BatterStats.csv")
    batterDF = batterDF.set_index("Name")
    batterCols = ["PA", "1B", "2B", "3B", "HR", "BB", "IBB", "HBP", "SO", "AVG", "SB"]
    batterDF[batterCols] = batterDF[batterCols].apply(pd.to_numeric,
                                                            errors="ignore")

    pitcherDF = pd.read_csv("PitcherStats.csv")
    pitcherDF = pitcherDF.set_index("Name")
    pitcherCols = ["TBF", "H", "2B", "3B", "HR", "BB", "IBB", "HBP", "SO"]
    pitcherDF[pitcherCols] = pitcherDF[pitcherCols].apply(pd.to_numeric, 
                                                                errors="ignore")
    #wasn't an option for singles for pitchers so I just took 
    #hits minus all other hit possibilities
    pitcherDF["1B"] = pitcherDF["H"] - (pitcherDF["2B"] + pitcherDF["3B"]  
                                  + pitcherDF["HR"])

    leagueDF = pd.read_csv("LeagueStats.csv")
    leagueDF = leagueDF.set_index("Season")
    leagueDF[batterCols] = leagueDF[batterCols].apply(pd.to_numeric,
                                                                errors="ignore")
    return (batterDF, pitcherDF, leagueDF)

#creates batting lineups from the input .txt files
# and gets the stats associated with each player in the lineup
# returns two lineups****************************************
def createLineups(filename1, filename2, batterDF, pitcherDF):
    lineup1, lineup2 = [None] * 11, [None] * 11
    lineupList = [lineup1, lineup2]
    fileList = [filename1, filename2]

    for lineup, filename in zip(lineupList, fileList):
        #checks to see if the file is valid
        if not filename.lower().endswith(".txt"):
            sys.exit("Lineupfile"+ fileName+"must be in a .txt file")

        file = open(filename, "r")
        tmpLineup = [s.strip() for s in file.readline().split(",")]

        for i in range(11):
            if i == 0:
                lineup[i] = tmpLineup[i]
            elif i> 0 and i < 10:
                #if the batter is not in the index
                if not tmpLineup[i] in batterDF.index:
                    sys.exit("batter, " + tmpLineup[i] + ", in " + filename + 
					        (" does not exist in the FanGraphs database. "
					        "Please check the spelling of the player's "
					        "name."))
                #if the batter is in the index
                lineup[i] = Batter()
                lineup[i].name = tmpLineup[i]
            else:
                #The only other condition is that i would 
                #be greater than or equal to 10 which means 
                #it is time to put the pitcher in the lineup

                #if the Pitcher is not in the index
                if not tmpLineup[i] in pitcherDF.index:
                    sys.exit("pitcher, " + tmpLineup[i] + ", in " + filename + 
						     (" does not exist in the FanGraphs database. "
						      "Please check the spelling of the player's "
						      "name."))
                #if the pitcher is in the index
                lineup[i] = Pitcher()
                lineup[i].name = tmpLineup[i]
        file.close()
    return (lineup1, lineup2)

#fills and returns attributes for pitcher and batters in the lineup
def fillStatline(batterDF, pitcherDF, leagueDF, lineup1, lineup2, algo):
    lineupList = [lineup1, lineup2]

    #loop that populates the probabilities for each thing happening to each starter
    for lineup in lineupList:
        for i in range (1, 11):
            player = lineup[i]

            if i < 10:
                row = batterDF.loc[player.name]
                PA = row["PA"]
                player.AB = row["SB"]
            else:
                row = pitcherDF.loc[player.name]
                PA = row["TBF"]

            player.pSingle = row["1B"] /PA
            player.PA      = PA
            player.avg     = row["AVG"]
            player.totBags = (row["1B"] + (2*row["2B"]) + (3*row["3B"]) + (4*row["HR"]))
            player.pDouble = row["2B"] /PA
            player.pTriple = row["3B"] /PA
            player.pHR     = row["HR"] /PA
            player.pTw     =(row["BB"] + row["HBP"] + row["IBB"]) /PA
            player.pK      = row ["SO"] /PA
            player.pOut    =((PA -row["1B"] - row["2B"] - row["3B"] - row["HR"] 
                              -row["BB"] - row["IBB"] - row["HBP"] - row["SO"]) /PA)
            player.AB      = (row["1B"] + row["2B"] + row["3B"] + row["HR"] + row["BB"] + row["HBP"] + row["IBB"] + row["SO"] + player.pOut)
            
            

    # for the league numbers and probabilities
    PA = leagueDF.loc[2019, "PA"]
    leagueDF.loc[2019, "pSingle"] = leagueDF.loc[2019, "1B"] / PA
    leagueDF.loc[2019, "pDouble"] = leagueDF.loc[2019, "2B"] / PA
    leagueDF.loc[2019, "pTriple"] = leagueDF.loc[2019, "3B"] / PA
    leagueDF.loc[2019, "pHR"] = leagueDF.loc[2019, "HR"] / PA
    leagueDF.loc[2019, "pTw"] = (leagueDF.loc[2019, "BB"] 
                                        + leagueDF.loc[2019, "HBP"]
                                         + leagueDF.loc[2019, "IBB"] ) / PA

    leagueDF.loc[2019, "pK"] = leagueDF.loc[2019, "SO"] / PA
    leagueDF.loc[2019, "pOut"] = ((PA -leagueDF.loc[2019, "1B"] 
                                         - leagueDF.loc[2019, "2B"] 
                                         - leagueDF.loc[2019, "3B"]
                                         - leagueDF.loc[2019, "HR"] 
                                         - leagueDF.loc[2019, "BB"]
                                         - leagueDF.loc[2019, "IBB"] 
                                         - leagueDF.loc[2019, "HBP"]
                                         - leagueDF.loc[2019, "SO"]) / PA)

    #based on whichever algo is chosen 
    #the lineup will be sent to the 
    #different lineup setting algorithms
    if algo == Algo.bean:
        lineup1 = beanModel(lineup1, Algo.bean)
    if algo == Algo.wood:
        lineup1 = woodardsAlgorithm(lineup1, Algo.wood)
    if algo == Algo.wiss:
       lineup1 = wissingerMethod(lineup1, Algo.wiss)
    if algo == Algo.none:
        print("\nNo certain order\n")
        for player in lineup1:
            if type(player) != str:
                print(player.name)

    return (lineup1, lineup2, leagueDF)

#This algorithm will sort the batting lineup by OBP, *************
#aka the Billy Bean Model
def beanModel(lineup, algo):
   count = 0
   for player in lineup:
       for j in range(0, len(lineup) - count - 1):
           #player = lineup[j]
           if type(lineup[j]) != str:
               if lineup[j].pTw + lineup[j].pSingle + lineup[j].pDouble + lineup[j].pTriple + lineup[j].pHR < lineup[j+1].pTw + lineup[j+1].pSingle + lineup[j+1].pDouble + lineup[j+1].pTriple + lineup[j+1].pHR:
                    lineup[j], lineup[j+1] = lineup[j+1], lineup[j]

       count = count+1 
   if algo == Algo.bean:
       print("\nBean Model\n")
       for player in lineup:
           if type(player) != str:
               print(player.name)
               count = count
   return lineup

#This algorithm will order the lineup acording to woodard's algorithm
#*Main takeaways from the algorithms*
#two lineups of half the size, two leadoff hitters in the 1 and 5 spot, and more ****************
def woodardsAlgorithm(lineup, algo):
    newLineup = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    newLineup.insert(0, lineup[0])

    #begin placing people in the lineup
    #these are called in a specific order
    #different spots in the lineup are looking for different things 

    #at spot one because it is returning the first player
    tmpPlayer = beanModel(lineup, Algo.wood)[1]
    newLineup[1] = tmpPlayer #1st in lineup, call 1st
    lineup.remove(tmpPlayer)

    tmpPlayer = maxOBPS(lineup)
    newLineup[2] = tmpPlayer #2nd in lineup
    lineup.remove(tmpPlayer)

    tmpPlayer = maxAVG(lineup)
    newLineup[3] = tmpPlayer #3th in lineup
    lineup.remove(maxAVG(lineup))

    tmpPlayer = maxSlg(lineup)
    newLineup[4] = tmpPlayer #4th in lineup
    lineup.remove(tmpPlayer)

    tmpPlayer = beanModel(lineup, Algo.wood)[1]
    newLineup[5] = tmpPlayer #5th in lineup
    lineup.remove(tmpPlayer)

    tmpPlayer = maxOBPS(lineup)
    newLineup[6] = tmpPlayer #6th in lineup
    lineup.remove(tmpPlayer)

    tmpPlayer = maxAVG(lineup)
    newLineup[7] = tmpPlayer #7th in lineup
    lineup.remove(tmpPlayer)

    tmpPlayer = maxSlg(lineup)
    newLineup[8] = tmpPlayer #8th in lineup
    lineup.remove(tmpPlayer)

    tmpPlayer = maxAVG(lineup)
    newLineup[9] = tmpPlayer #9th in lineup
    lineup.remove(tmpPlayer)

    tmpPlayer = lineup[len(lineup)-1]
    newLineup[10]  = tmpPlayer
    lineup.remove(tmpPlayer)

    print("\nWoodards Algorithm\n")
    for player in newLineup:
        if type(player) != str:
            print(player.name)

    return(newLineup)

#this algorithm will sort the lineup in the "traditional" way*************************
#according to longtime coach Andrew Wissinger
#*Main takeaways*
#highest obp in 1 spot
#highest slg in 4, etc 
def wissingerMethod(lineup, algo):


    newLineup = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    newLineup.insert(0, lineup[0])

    #begin placing people in the lineup
    #these are called in a specific order
    #different spots in the lineup are looking for different things 

    tmpPlayer = beanModel(lineup, Algo.wiss)[1]
    newLineup[1] = tmpPlayer #1st in lineup
    lineup.remove(tmpPlayer)

    tmpPlayer = maxSlg(lineup)
    newLineup[4] = tmpPlayer #4th in lineup
    lineup.remove(tmpPlayer)

    tmpPlayer = maxOBPS(lineup)
    newLineup[3] = tmpPlayer #3th in lineup
    lineup.remove(tmpPlayer)

    tmpPlayer = maxAVG(lineup)
    newLineup[2] = tmpPlayer #2th in lineup
    lineup.remove(tmpPlayer)

    tmpPlayer = maxSlg(lineup)
    newLineup[5] = tmpPlayer #5th in lineup
    lineup.remove(tmpPlayer)

    tmpPlayer = maxAVG(lineup)
    newLineup[6] = tmpPlayer #6th in lineup
    lineup.remove(tmpPlayer)

    tmpPlayer = maxSlg(lineup)
    newLineup[7] = tmpPlayer #7th in lineup
    lineup.remove(tmpPlayer)

    tmpPlayer = maxAVG(lineup)
    newLineup[9] = tmpPlayer #9th in lineup
    lineup.remove(tmpPlayer)

    tmpPlayer = maxAVG(lineup)
    newLineup[8] = tmpPlayer #8th in lineup
    lineup.remove(tmpPlayer)

    tmpPlayer = lineup[len(lineup)-1]
    newLineup[10]  = tmpPlayer
    lineup.remove(tmpPlayer)

    print("\nWissinger Method\n")
    for player in newLineup:
        if type(player) != str:
            print(player.name)

    return(newLineup)

#creates and returns a dataframe containing 
#the baserunning probabilities for each state
def fillBaserunning():
    playFIle = open("AllPlays2019.txt")         ##******all plays data used here
    playData = list(csv.reader(playFIle))

    #a list of the 24 possible states a baseball game can be in 
    #the first number is number of outs and there is a 1 if there 
    #is a runner on that base (1st, 2nd, or 3rd)
    # and 4 plays that impact baserunning
    states = ["0,000","0,100","0,010","0,001","0,110","0,011","0,101","0,111",
			  "1,000","1,100","1,010","1,001","1,110","1,011","1,101","1,111",
			  "2,000","2,100","2,010","2,001","2,110","2,011","2,101","2,111"]
    
    plays = ["1B","2B","3B","OUT"]

    #initalizing dataframes with empty dics
    emptyDics = [[{} for x in range(4)] for y in range(24)]
    brDF = pd.DataFrame(emptyDics, index=states, columns=plays)

    for index, row in enumerate(playData):
        play = row[5]
        if play =="2":
            play = "OUT"
        elif play == "20":
            play == "1B"
        elif play == "21":
            play = "2B"
        elif play == "22":
            play = "3B"

        #these are only considered if play is 
        #equal to 1B, 2B, 3B, or OUT
        if play == "OUT" or play == "1B" or play == "2B" or play == "3B":
            #find out the current state
            out = row[0]
            if row[1] == "":
                base1 = "0"
            else:
                base1 = "1"
            if row[2] == "":
                base2 = "0"
            else:
                base2 = "1"
            if row[3] == "":
                base3 = "0"
            else:
                base3 = "1"
            state = out + "," + base1 + base2 + base3
         
            #this updates the out and count
            newOut = int(out)
            if row[6] == "0":
              newOut +=1
            if base1 =="1" and row[7] == "0":
                newOut += 1
            if base2 == "1" and row[8] == "0":
                newOut += 1
            if base3 == "1" and row[9] == "0":
                newOut += 1

            #this updates the bases count and runs scored 
            #if any did
            newBase1 = "0"
            newBase2 = "0"
            newBasse3 = "0"
            newRuns = 0

            for base in row[6:]:
                if base == "1":
                    newBase = "1"
                elif base == "2":
                    newBase = "1"
                elif base == "3":
                    newBase3 = "1"
                elif base == "4" or base == "5" or base == "6":
                    newRuns += 1
            newState = (str(newOut) + "," + newBase1 + newBase2 + newBase3
			            + "," + str(newRuns))
            
            # update the number of occurrences of new state in the dictionaries
            brDict = brDF.loc[state, play]
            if "total" in brDict:
                brDict["total"] += 1
            else:
                brDict["total"] = 1

            if newState in brDict:
                    brDict[newState] += 1
            else:
                brDict[newState] = 1
    return brDF

# calculates and returns the list of probabilities
#  of each a plate apperance
def calcOdds(batter, pitcher, leagueDF):
    #calculations that every plate outcome will happen
    if type(batter) == str or type(pitcher) == str:
        return

    oddsSingle = ((batter.pSingle / (1-batter.pSingle)) * (pitcher.pSingle / (1-pitcher.pSingle)) 
                  / (leagueDF.loc[2019, "pSingle"] / (1-leagueDF.loc[2019, "pSingle"])))
    oddsDouble = ((batter.pDouble / (1-batter.pDouble)) * (pitcher.pDouble / (1-pitcher.pDouble)) 
                  / (leagueDF.loc[2019, "pDouble"] / (1-leagueDF.loc[2019, "pDouble"])))
    oddsTriple = ((batter.pTriple / (1-batter.pTriple)) * (pitcher.pTriple / (1-pitcher.pTriple)) 
                  / (leagueDF.loc[2019, "pTriple"] / (1-leagueDF.loc[2019, "pTriple"])))
    oddsHR     = ((batter.pHR / (1-batter.pHR)) * (pitcher.pHR / (1-pitcher.pHR)) 
                  / (leagueDF.loc[2019, "pHR"] / (1-leagueDF.loc[2019, "pHR"])))
    oddsTw     = ((batter.pTw / (1-batter.pTw)) * (pitcher.pTw / (1-pitcher.pTw)) 
                  / (leagueDF.loc[2019, "pTw"] / (1-leagueDF.loc[2019, "pTw"])))
    oddsK      = ((batter.pK / (1-batter.pK)) * (pitcher.pK / (1-pitcher.pK)) 
                  / (leagueDF.loc[2019, "pK"] / (1-leagueDF.loc[2019, "pK"])))
    oddsOut    = ((batter.pOut / (1-batter.pOut)) * (pitcher.pOut / (1-pitcher.pOut)) 
                  / (leagueDF.loc[2019, "pOut"] / (1-leagueDF.loc[2019, "pOut"])))

    #now turn the odds into probabilities to better compare
    pSingle = oddsSingle / (oddsSingle + 1)
    pDouble = oddsDouble / (oddsDouble + 1)
    pTriple = oddsTriple / (oddsTriple + 1)
    pHR     = oddsHR / (oddsHR + 1)
    pTw     = oddsTw / (oddsTw + 1)
    pK      = oddsK / (oddsK + 1)
    pOut    = oddsOut / (oddsOut + 1)

    total = pSingle + pDouble + pTriple + pHR + pTw + pK + pOut

    #since the probabilities don't exactly add up to 1 
    #I need to normalize them by dividing by the total
    npSingle = pSingle / total
    npDouble = pDouble / total
    npTriple = pTriple / total
    npHR     = pHR / total
    npTw     = pTw / total
    npK      = pK / total
    npOut    = pOut / total
    return [npSingle, npDouble, npTriple, npHR, npTw, npK, npOut]

# plays an entire game and returns 0 if the away team wins and 1 otherwise
def playGame(lineup1, lineup2, leagueDF, brDF):
	inning = 0
	out = 0
	bases = "000"
	state = "0,000"
	homeBattingOrder = 1
	awayBattingOrder = 1
	homeScore = 0
	awayScore = 0
	playList = ["1b", "2b", "3b", "hr", "tw", "so", "bo"]

    # play from top 1st to bottom 9th inning, and extra innings are upto 33rd
    #this decides when the game will be over
	for inning in [i / 10 for i in range(10,3305,5)]:
		if inning == 9.5 and awayScore < homeScore:  # home team won; don't play bottom 9th
			break
		elif inning == 10.0 and awayScore != homeScore:  # winner is decided after 9 innings
			break
		elif inning >= 11.0 and (inning % 1.0) == 0.0:  # extra innings (one inning sudden death)
			if awayScore != homeScore:
				break

		# print("--- inning: " + str(inning) + " ---")
		if (inning % 1.0) == 0.0:  # away team bats
			batter = lineup1[awayBattingOrder]
			pitcher = lineup2[10]  # no need to do this in this loop since there is only one pitcher now
			score = awayScore
			battingOrder = awayBattingOrder
		else:
			batter = lineup2[homeBattingOrder]
			pitcher = lineup1[10]
			score = homeScore
			battingOrder = homeBattingOrder
		while out < 3:
			playProbList = calcOdds(batter, pitcher, leagueDF)
			play = choice(playList, p=playProbList)
			if play == "1B" or play == "2B" or play == "3B" or play == "OUT":
				brDict = brDF.loc[state, play]
				resultList = list(brDict.keys())[1:]  
				countList = list(brDict.values())[1:]
				totalCount = brDict["total"]
				probList = [count / totalCount for count in countList]
				result = choice(resultList, p=probList)
				out = int(result.split(",")[0])
				bases = result.split(",")[1]
				score += int(result.split(",")[2])
			elif play == "hr":
				score += (int(bases[0]) + int(bases[1]) + int(bases[2]) + 1)
				bases = "000"
                #if a BB occurs
			elif play == "tw":
				if bases == "000" or bases == "001" or bases == "010":
					bases = str(int(bases) | 100)
				elif bases == "100":
					bases = "110"
				elif bases == "110" or bases == "011" or bases == "101":
					bases = "111"
				else:
					bases = "111"
					score += 1
			else:  #play == "so"
				out += 1

			state = str(out) + "," + bases
			# print("batting team score: " + str(score) + " | batter: " + str(battingOrder) + " | play: " + play + " | new state: " + state)
			if battingOrder < 9:
				battingOrder += 1
			else:
				battingOrder = 1

		# update the score and batting order for the correct team
		if (inning % 1.0) == 0.0:
			awayScore = score
			awayBattingOrder = battingOrder
		else:
			homeScore = score
			homeBattingOrder = battingOrder
		out =  0
		bases = "000"
		state = "0,000"
	# print("awayScore: " + str(awayScore) + " | homeScore: " + str(homeScore))
	if awayScore > homeScore:
		return 0
	else:
		return 1

#returns the highest slg% in the lineup
def maxSlg(lineup):
    count = 0
    for player in lineup:
        for j in range(0, len(lineup)-count-1):
            if type(lineup[j]) != str:      
                if ((lineup[j].totBags)/lineup[j].AB) < ((lineup[j+1].totBags)/lineup[j+1].AB):
                    lineup[j], lineup[j+1] = lineup[j+1], lineup[j]
    return lineup[1]

#returns the highest obps in the lineup
def maxOBPS(lineup):
    count = 0
    for player in lineup:
        for j in range(0, len(lineup)-count-1): 
            if type(lineup[j]) != str:
                if ((lineup[j].pTw + lineup[j].pSingle + lineup[j].pDouble + lineup[j].pTriple + lineup[j].pHR) + (((lineup[j].totBags)/lineup[j].AB))) < ((lineup[j+1].pTw + lineup[j+1].pSingle + lineup[j+1].pDouble + lineup[j+1].pTriple + lineup[j+1].pHR) + ((lineup[j+1].totBags)/lineup[j+1].AB)):
                    lineup[j], lineup[j+1] = lineup[j+1], lineup[j]           
    return lineup[1]

#returns the highest obps in the lineup
def maxAVG(lineup):
    count = 0    
    for player in lineup:
        for j in range(0, len(lineup) - count - 1):
            if type(lineup[j]) != str:
                if (lineup[j].avg) < (lineup[j+1].avg):
                    lineup[j], lineup[j+1] = lineup[j+1], lineup[j]            
    return lineup[1]

    # simulates multiple games between two teams and prints out the result
def simulate(lineup1, lineup2, leagueDF, brDF):
	awayWin = 0
	homeWin = 0
	for i in range(0, 1000):
		result = playGame(lineup1, lineup2, leagueDF, brDF)
		if result == 0:
			awayWin += 1
		else:
			homeWin += 1
	print("awayWin: " + str(awayWin) + " | homeWin: " + str(homeWin))

def main(argv):
	batterDF, pitcherDF, leagueDF = readData()
    #checking Billy Bean model
	lineup1, lineup2 = createLineups(argv[1], argv[2], batterDF, pitcherDF)
	lineup1, lineup2, leagueDF = fillStatline(batterDF, pitcherDF, leagueDF, 
											   lineup1, lineup2, Algo.bean)
	brDF = fillBaserunning()
	simulate(lineup1, lineup2, leagueDF, brDF)

    #checking Woodard's Algorithm
	lineup1, lineup2 = createLineups(argv[1], argv[2], batterDF, pitcherDF)
	lineup1, lineup2, leagueDF = fillStatline(batterDF, pitcherDF, leagueDF, 
											   lineup1, lineup2, Algo.wood)
	brDF = fillBaserunning()
	simulate(lineup1, lineup2, leagueDF, brDF)

    #checking Wissinger Method
	lineup1, lineup2 = createLineups(argv[1], argv[2], batterDF, pitcherDF)
	lineup1, lineup2, leagueDF = fillStatline(batterDF, pitcherDF, leagueDF, 
											   lineup1, lineup2, Algo.wiss)
	brDF = fillBaserunning()
	simulate(lineup1, lineup2, leagueDF, brDF)

    #control
	lineup1, lineup2 = createLineups(argv[1], argv[2], batterDF, pitcherDF)
	lineup1, lineup2, leagueDF = fillStatline(batterDF, pitcherDF, leagueDF, 
											   lineup1, lineup2, Algo.none)
	brDF = fillBaserunning()
	simulate(lineup1, lineup2, leagueDF, brDF)


if __name__ == "__main__": main(sys.argv)