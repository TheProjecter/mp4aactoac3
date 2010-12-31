import tkFileDialog
from Tkinter import *

import os
import logging
from optparse import OptionParser

def main(options):
    logging.basicConfig(filename='converter.log', level=logging.DEBUG)
    logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    log = logging.getLogger('')
    
    try:
        root = Tk()
        
        #Display the window to get the file location
        fp = tkFileDialog.askopenfilename()
        log.info('Path: %s' % fp)
        
        #Determine the drive letter where of the file location
        if ':' in fp:
            fileBase = fp.split(':')[0]
        elif '//' in fp:
            fileBase = '//' + fp.split('/')[2]
            
        log.info('Base of path: %s' % fileBase)
        
        if ':' in os.getcwd():
            localBase = os.getcwd().split(':')[0]
        elif '//' in os.getcwd():
            localBase = '//' + os.getcwd().split('/')[2]
            
        log.info('Local base path: %s' % localBase)
        
        if options.skipCopy == False:
            if(fileBase == localBase):
                log.info('File is on the local path, no need to copy.')
            else:
                #XXX need to copy file to local path
                log.info('File is not on the local path, copy to local.')
        
        statement = 'mp4box -info "%s" > temp.log' % fp.replace('/', '\\')
        log.info('os.system(%s)' % statement)
        os.system(statement)
        
        tempLog = open('temp.log')
        text = tempLog.readlines()
        tracks = 0
        
        streamsToExtract = []
        
        for line in text:
            if 'TrackID' in line:
                tracks += 1
                log.info('Adding another track...count is %s.' % tracks)
            elif 'Visual Stream' in line:
                log.info('Identified the video stream, TrackID %s.' % tracks)
                streamsToExtract.append(tracks)
            elif 'Audio AAC' in line and '6 Channel' in line:
                log.info('Identified 6 channel AAC track,TrackID %s.' % tracks)
                streamsToExtract.append(tracks)
                
        for stream in streamsToExtract:
            statement = 'mp4box -raw %s "%s"' % (stream, fp)
            log.info('os.system(%s)' % statement)
            os.system(statement)
        
        #May want to add support
        for fileName in os.listdir('.'):
            if '.aac' in fileName:
                AACFileName = fileName
            elif '.mp4' in fileName:
                MP4FileName = fileName
            elif '.h264' in fileName:
                h264FileName = fileName
        
        log.info('Convert AAC to multichannel WAV...')
        statement = 'faad "%s"' % AACFileName
        log.info(statement)
        os.system(statement)
        
        waveFileName = AACFileName.split('.aac')[0] + '.wav'
        AC3FileName = AACFileName.split('.aac')[0] + '.ac3'
        
        log.info('Convert WAV to AC3...')
        statement = 'eac3to "%s" "%s"' % (waveFileName, AC3FileName)
        log.info(statement)
        os.system(statement)
        
        newFileName = MP4FileName.split('.mp4')[0] + '.AC3.mp4'
        log.info('New file name: %s' % newFileName)
        statement = 'mp4box -add "%s" -add "%s" -new "%s"' % (h264FileName, AC3FileName, newFileName)
        log.info('Muxing h264 with AC3 file...')
        log.info(statement)
        os.system(statement)
        
        log.info('os.remove(%s)' % AACFileName)
        os.remove(AACFileName)
        log.info('os.remove(%s)' % waveFileName)
        os.remove(waveFileName)
        log.info('os.remove(%s)' % h264FileName)
        os.remove(h264FileName)
        log.info('os.remove(%s)' % AC3FileName)
        os.remove(AC3FileName)
        #Possibly delete faad generated log file?
        
        # if options.deleteOriginal:
            # log.info('os.remove(%s)' % fp)
            # os.remove(fp)
        
        root.destroy()
    except:
        raise

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-s', '--skipCopy', action='store_true', default='False', dest='skipCopy',
            help='Skip copying the file to the same directory as the script.')
    parser.add_option('-d', '--deleteOriginal', action='store_true', default='False', dest='deleteOriginal',
            help='Delete the original file when done.')
    
    (options, args) = parser.parse_args()
    
    main(options)