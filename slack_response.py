# -*- coding: utf-8 -*-
"""
Created on Tue Mar 13 23:17:08 2018

@author: Tim
"""
import time
import bqutil as bqu

class SlackResponseBuilder:
    """
        Finds and executes the given command, filling in response
    """
    def __init__(self, command, slash_command):
        #get an instance of the bq_utils() class
        self.bqq = bqu.BQutils()
        #initialize variables
        response, srefs, qrefs = self.check_command(command, slash_command)
        self.response = response
        self.srefs = srefs
        self.qrefs = qrefs

    def check_command(self, command, slash_command):
        """
            looks at command and returns appropriate reponse based on which command
        """
        srefs = None
        qrefs = None
        response = None
        # This is where you start to implement more commands!
        if command.startswith(slash_command[0]):
            response, srefs = self.command0response(command)

        if command.startswith(slash_command[1]):
            response, qrefs = self.command1response(command)
        if srefs:
            print('Refbot returned the following Scriptural references:\n'+srefs)
        elif qrefs:
            print('Refbot returned the following Quranic references:\n'+'\n'.join(qrefs))
        else:
            print('No references')
        return (response, srefs, qrefs)

    def command0response(self, command):
        """
            returns response to /getscripture Mark 3:15 ... for example
        """
        #TODO Find out why Slack igores my initial \n\n
        response = '\n\n'
        srefs = ''
        #find the references in the text
        refs = self.bqq.find_bible_verses(command)
        if refs:
            for ref in refs:
                #look up verse after politely waiting so we don't
                #get a 429 response from the ESV api
                time.sleep(1)
                sref = ref[0].strip() + ' ' + ref[1].strip() + ':' + ref[2].strip()
                scripture = self.bqq.get_scripture(sref)
                srefs += sref + '\n'
                #print out the ESV text of the verse(s)
                esvtext = scripture['passages'][0].split('Footnotes')[0].strip()
                #make the title bold and add appropriate spacing
                esvtext_bold_title = self.bold_esv_title(esvtext)
                #build the response string
                response += esvtext_bold_title
        else:
            response = '\n*No scripture references*\n'
        return (response, srefs)

    def command1response(self, command):
        """
            returns response to /getquran 4:125 ... for example
        """
        response = '\n\n'
        qverses = []
        #find the references in the text
        qrefs = self.bqq.find_quran_verses(command)
        if qrefs:
            for qref in qrefs:
                time.sleep(1)
                quran = self.bqq.get_quran(qref)
                quote = quran['data']['text']
                sura = quran['data']['surah']['englishName']
                qverse = sura + ' ' + qref[1]
                #print out the quranic text(s) with a bold reference at the top
                response += '*' + qverse + '*\n\n' + quote.strip() + '\n\n'
                qverses.append(qverse)
        else:
            response = '\n*No Quranic references*\n'
        return (response, qverses)

    @staticmethod
    def bold_esv_title(esvtext):
        """
            bolds the title of the esv text with Slack formatting
            and formats a little
        """
        esvsplit = esvtext.splitlines()
        return '\n\n*' + esvsplit[0] + '*\n\n'+' '.join(''.join(esvsplit[1:]).split())+'\n\n'
