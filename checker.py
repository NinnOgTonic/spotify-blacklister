from subprocess import Popen, PIPE
import json
import time


maxsleep = 20.0

def getPlayingInfo():
    process = Popen(['osascript', "scripts/check_playing.script"], stdout=PIPE)
    (output, err) = process.communicate()
    exit_code = process.wait()

    res = json.loads(output)
    res['progress'] = float(res['progress'].replace(',', '.'))

    # Assume that our track duration is between 100s and 999s
    res['duration'] = float(res['duration'][:3] + '.' + res['duration'][3:])

    return res


def getTimeToTrackEnd(res):
    return res['duration'] - res['progress']


def checkForBlacklist(res):
    return True

def next():
    process = Popen(['osascript', "scripts/next_track.script"], stdout=PIPE)
    (output, err) = process.communicate()
    exit_code = process.wait()


lastCheck = None

def getReadyToCheckAndChange(res):
    global lastCheck
    while res['state'] == 'playing':
        timeleft = getTimeToTrackEnd(res)
        print 'Timeleft %f' % timeleft
        currentCheck = {
            'track': res['track'],
            'artist': res['artist']
        }
        if timeleft < 1:
            time.sleep(0.1)
        elif timeleft < 10:
            time.sleep(1)
        elif res['progress'] < 2 and currentCheck != lastCheck and checkForBlacklist(res):
            print 'SKIPPING NOW'
            print res
            next()
            lastCheck = currentCheck
            return
        else:
            return

        res = getPlayingInfo()


while True:
    res = getPlayingInfo()

    sleep = max(min(res['duration']-res['progress']-1, maxsleep), 0.0 if res['state'] == 'playing' else 5.0)
    print res['progress'], res['duration'], res['duration']-res['progress'], sleep
    if sleep < maxsleep and res['state'] == 'playing':
        getReadyToCheckAndChange(res)
    else:
        print 'Sleeping %f' % sleep
        time.sleep(sleep)
    #time.sleep(max(min(duration-progress-1, maxsleep), 0))