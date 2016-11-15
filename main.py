import time,datetime
#from source.controller.DataManagement.MyTwitterAPI import MyTwitterAPI
#from source.controller.DataManagement.MongoDBHandler import MongoDBHandler
from source.controller.DataManagement.TransformationUtilities import *

from source.controller.EventDetection.SimilarityMatrixBuilder.LEDSimilarityMatrixBuilder import LEDSimilarityMatrixBuilder
from source.controller.EventDetection.SimilarityMatrixBuilder.MEDSimilarityMatrixBuilder import MEDSimilarityMatrixBuilder
from source.controller.EventDetection.OptimisedEventDetectorMEDBased import OptimisedEventDetectorMEDBased
from source.controller.EventDetection.EventDetector import EventDetector

from source.controller.EventDetection.Utils.Utils import *
import argparse
#---------------------------------------------------------------------------------------------------------------------------------------------

LED_SIM=0
MED_SIM=1
MED_SIM_WITHOUT_REAL_MATRIX=2

MIN_TERM_OCCURENCE=0
REMOVE_NOISE_WITH_POISSON_LAW=False

TIME_RESOLUTION=1800
DISTANCE_RESOLUTION=100
SCALE_NUMBER=4
MIN_SIMILARITY=0

MINLAT=38
MAXLAT=46
MINLON=-80
MAXLON=-71

# MYCOMMENT

MINTIME=datetime.datetime(2015,8,31)
MAXTIME=datetime.datetime(2015,10,1)

#NUMBER_OF_TWEETS=56021
#NUMBER_OF_TWEETS_MEHDI=798400

#---------------------------------------------------------------------------------------------------------------------------------------------
def filterTweets(tweets,minLat=MINLAT,maxLat=MAXLAT,minLon=MINLON,maxLon=MAXLON,minTime=MINTIME,maxTime=MAXTIME) :
    return [tweet for tweet in tweets if (minTime<tweet.time<maxTime) and (minLat<=tweet.position.latitude<=maxLat) and (minLon<=tweet.position.longitude<=maxLon)]
#---------------------------------------------------------------------------------------------------------------------------------------------
def getTweetsFromTwitterAndSave(count=100,export=False,mongoDBName='Twitter',mongoCollectionName="tweets") :
    mongoDBHandler=MongoDBHandler(database_name=mongoDBName,collection_name=mongoCollectionName)
    api = MyTwitterAPI("twitter_config_file.txt")
    tweets = api.getTweets(count=count,export=export)
    mongoDBHandler.saveTweets(tweets)
#---------------------------------------------------------------------------------------------------------------------------------------------
def getTweetsFromJSONRepositoryAndSave(repositoryPath="E:\\tweets",mongoDBName='Twitter',mongoCollectionName="tweets") :
    mongoDBHandler=MongoDBHandler(database_name=mongoDBName,collection_name=mongoCollectionName)
    mongoDBHandler.saveTweetsFromJSONRepository(repositoryPath)
#---------------------------------------------------------------------------------------------------------------------------------------------
def getTweetsFromCSVFileAndSave(csvFilePath="D:\\PRJS\\Data\\final.csv",mongoDBName='Twitter',mongoCollectionName="tweetsMehdi") :
    mongoDBHandler=MongoDBHandler(database_name=mongoDBName,collection_name=mongoCollectionName)
    mongoDBHandler.saveTweetsFromCSVFile(csvFilePath)
#---------------------------------------------------------------------------------------------------------------------------------------------
def getTweetFromLine(inputLine):
    line = inputLine.strip().split(",")
    _id=line[0]
    userId=line[1]
    latitude=float(line[2])
    longitude=float(line[3])
    position=Position(latitude,longitude)
    time=datetime.datetime.fromtimestamp(float(line[4]))
    text=line[5]
    hashtags=text.strip().split(" ")
    return Tweet(_id,userId,text,hashtags,time,position)
#---------------------------------------------------------------------------------------------------------------------------------------------
def getTweetsFromFile(inputFilePath="MedInputFile.txt") :
    tweets=[]
    with open(inputFilePath) as f :
            line=f.readline() #Header
            for line in f :
                tweets.append(getTweetFromLine(line))
    return tweets
                
#---------------------------------------------------------------------------------------------------------------------------------------------
def detectEvents(limit=300,similarityType=MED_SIM,minimalTermPerTweet=MIN_TERM_OCCURENCE,remove_noise_with_poisson_Law=REMOVE_NOISE_WITH_POISSON_LAW,printEvents=True,fileName="inputTweets.txt",printInFile="events.txt",useOnlyHashtags=False) :
    staringTime=time.time()
    #mongoDBHandler=MongoDBHandler(database_name=mongoDBName,collection_name=mongoCollectionName)
    #tweets=mongoDBHandler.getAllTweets(limit=limit)
    tweets=getTweetsFromFile(fileName);
    if similarityType==LED_SIM :
        s=LEDSimilarityMatrixBuilder(timeThreshold=TIME_RESOLUTION,distanceThreshold=DISTANCE_RESOLUTION,useOnlyHashtags=useOnlyHashtags)
        eventDetector=EventDetector(tweets,s)
        events=eventDetector.getEvents(minimalTermPerTweet=minimalTermPerTweet,remove_noise_with_poisson_Law=remove_noise_with_poisson_Law)
    elif similarityType==MED_SIM :
        s=MEDSimilarityMatrixBuilder(timeResolution=TIME_RESOLUTION,distanceResolution=DISTANCE_RESOLUTION,scaleNumber=SCALE_NUMBER,minSimilarity=MIN_SIMILARITY,useOnlyHashtags=useOnlyHashtags)
        eventDetector=EventDetector(tweets,s)
        events=eventDetector.getEvents(minimalTermPerTweet=minimalTermPerTweet,remove_noise_with_poisson_Law=remove_noise_with_poisson_Law)
    else :
        eventDetector=OptimisedEventDetectorMEDBased(tweets,timeResolution=TIME_RESOLUTION,distanceResolution=DISTANCE_RESOLUTION,scaleNumber=SCALE_NUMBER,minSimilarity=MIN_SIMILARITY,useOnlyHashtags=useOnlyHashtags)
        events=eventDetector.getEvents(minimalTermPerTweet=minimalTermPerTweet,remove_noise_with_poisson_Law=remove_noise_with_poisson_Law)
        
    print ""
    print "-"*40
    print "{0} Event detected : ".format(len(events))
    print "-"*40

    if printEvents :
        eventDetector.showTopEvents(top=len(events))

    if printInFile :
        txtFile=open(printInFile, 'w')
        elapsed_time=(time.time()-staringTime)
        #txtFile.write("Total elapsed time : {0}s\n".format(elapsed_time))
        #txtFile.write("-"*40+"\n")
        SEPARATOR=","
        HEADER=SEPARATOR.join(["key","event.type","eventDetector.endEpoch","event.strength","event.periodicity","event.period","mean_time","stddev_time","expression","dispersion","count","medoid","community_ID","nb_events_covered","dispersion","count","number_of_hashtags","covered_events"])+"\n"
        txtFile.write(HEADER)
        #txtFile.write("-"*40+"\n")
        for event in events :
            line=eventDetector.getStringOfEvent(event)
            txtFile.write(line+"\n")
            #txtFile.write("-"*40+"\n")
        txtFile.close();
        
    return events
#---------------------------------------------------------------------------------------------------------------------------------------------
def showTweetsNumberSignal(limit=300,granularity=3600, dyadic=True,mongoDBName='Twitter',mongoCollectionName="tweets") :
    mongoDBHandler=MongoDBHandler(database_name=mongoDBName,collection_name=mongoCollectionName)
    tweets=mongoDBHandler.getAllTweets(limit=limit)
    plotTweetsApparitionInTime(tweets, granularity=granularity, dyadic=dyadic)

def showTermOccurenceSignalByOrder(limit=300,topTermOrder=0, granularity=3600, dyadic=True,mongoDBName='Twitter',mongoCollectionName="tweets") :
    mongoDBHandler=MongoDBHandler(database_name=mongoDBName,collection_name=mongoCollectionName)
    tweets=mongoDBHandler.getAllTweets(limit=limit)
    plotTermApparitionInTimeWithOrder(tweets,topTermOrder=topTermOrder, granularity=granularity, dyadic=dyadic,mongoDBName='Twitter',mongoCollectionName="tweets")

def showTermOccurenceSignalByTerm(limit=300,term="#shopping", granularity=3600, dyadic=True,mongoDBName='Twitter',mongoCollectionName="tweets") :
    mongoDBHandler=MongoDBHandler(database_name=mongoDBName,collection_name=mongoCollectionName)
    tweets=mongoDBHandler.getAllTweets(limit=limit)
    plotTermApparitionInTime(tweets,term, granularity=granularity, dyadic=dyadic)

def showTweetsSpaceDistribution(limit=300,mongoDBName='Twitter',mongoCollectionName="tweets") :
    mongoDBHandler=MongoDBHandler(database_name=mongoDBName,collection_name=mongoCollectionName)
    tweets=mongoDBHandler.getAllTweets(limit=limit)
    plotTweetsInSpaceDistribution(tweets)

def showTermSpaceDistributionByOrder(limit=300,topTermOrder=0,mongoDBName='Twitter',mongoCollectionName="tweets") :
    mongoDBHandler=MongoDBHandler(database_name=mongoDBName,collection_name=mongoCollectionName)
    tweets=mongoDBHandler.getAllTweets(limit=limit)
    plotTermInSpaceDistributionWithOrder(tweets,topTermOrder=topTermOrder)

def showTermSpaceDistributionByTerm(limit=300,term="#shopping",mongoDBName='Twitter',mongoCollectionName="tweets") :
    mongoDBHandler=MongoDBHandler(database_name=mongoDBName,collection_name=mongoCollectionName)
    tweets=mongoDBHandler.getAllTweets(limit=limit)
    plotTermInSpaceDistribution(tweets,term)

def showTermOccurenceDistribution(limit=300,mongoDBName='Twitter',mongoCollectionName="tweets",useOnlyHashtags=False) :
    mongoDBHandler=MongoDBHandler(database_name=mongoDBName,collection_name=mongoCollectionName)
    tweets=mongoDBHandler.getAllTweets(limit=limit)
    plotTermOccurencesDistribution(tweets,useOnlyHashtags=useOnlyHashtags)
#---------------------------------------------------------------------------------------------------------------------------------------------  
def main(limit=300, similarityType=MED_SIM,useOnlyHashtags=True,fileName="inputTweets.txt", outputFilePath="retrievedEvents.txt") :
    staringTime=time.time()
    detectEvents(limit=limit,similarityType=similarityType,useOnlyHashtags=useOnlyHashtags,printEvents=False,fileName=fileName,printInFile=outputFilePath)
    elapsed_time=(time.time()-staringTime)
    print "-"*40
    print "Elapsed time : {0}s".format(elapsed_time)
    print "-"*40
#---------------------------------------------------------------------------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------------------------------------------------
#getTweetsFromCSVFileAndSave("D:\\PRJS\\Data\\final.csv",mongoDBName='Twitter',mongoCollectionName="tweetsMehdi")
#---------------------------------------------------------------------------------------------------------------------------------------------
#showTweetsNumberSignal(limit=NUMBER_OF_TWEETS_MEHDI,granularity=3600, dyadic=True,mongoDBName='Twitter',mongoCollectionName="tweetsMehdi")
#showTermOccurenceSignalByOrder(limit=NUMBER_OF_TWEETS,topTermOrder=1, granularity=3600, dyadic=True)
#showTermOccurenceSignalByTerm(limit=NUMBER_OF_TWEETS,term="bisous", granularity=3600, dyadic=True)
#showTweetsSpaceDistribution(limit=300,mongoDBName='Twitter',mongoCollectionName="tweetsMehdi")
#showTermSpaceDistributionByOrder(limit=NUMBER_OF_TWEETS,topTermOrder=0)
#showTermOccurenceDistribution(limit=NUMBER_OF_TWEETS_MEHDI,useOnlyHashtags=True,mongoDBName='Twitter',mongoCollectionName="tweetsMehdi")
#---------------------------------------------------------------------------------------------------------------------------------------------
    
parser = argparse.ArgumentParser()
parser.add_argument("--inputFile", help="the path of the input file")
parser.add_argument("--outputPath", help="the path of the result file")
args = parser.parse_args()

# TODO: Add the filepath ARGS
main(limit=300, similarityType=MED_SIM,useOnlyHashtags=True, fileName=args.inputFile, outputFilePath=args.outputPath)
#---------------------------------------------------------------------------------------------------------------------------------------------
