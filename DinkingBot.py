import nest_asyncio
import numpy as np
import pandas as pd
import time
import matplotlib
import os
import sys
import requests
import markovify as mk
matplotlib.use('Agg')
import matplotlib.pyplot as plt
nest_asyncio.apply()




def list_creator(names):
    N = len(names)
    if N == 1:
        out = names[0]
    elif N > 1:
        sep = [', ']*(N-1)
        sep[-1] = ' and '
        out = names[0]
        for i in range(N-1):
            out += sep[i] + names[i+1] 
    else:
        sep = [' and ']
        out = names[0] + sep[0] + names[1]
    return out

def Calculator(string):
    if 'os.' in string or 'sys.' in string:
        return 'Module not allowed'
    result = {}
    try:
        exec('a =%s' % string,None,result)
        print('%s'%result['a'] , str(string))
        if str(result['a']) != str(string):
            return result['a']
    except:
        return 'Invalid syntax'

# def current_stream(hour =int(time.strftime('%H',time.gmtime())) ): #for raid parties
#     streams = ['therealgpf','thesweedrunner','elxrdj','cptn_jaxx','ditz33']
#     times = [18,19,20,21,22]
#     current_hour = hour
#     if current_hour in times:
#         i =  [i for i in range(len(times)) if times[i] == current_hour][0]
#         string = 'Currently %s is live at https://www.twitch.tv/%s' %(streams[i],streams[i])
#     else:
#         string = 'No stream currently running'
#     return string

def week_hour():
    day = int(time.strftime('%w',time.gmtime()))-1
    hour_of_day = int(time.strftime('%H',time.gmtime()))
    if day == -1:
        day = 6
    return day*24+hour_of_day+2
def dink_time(T0 = 4*24+16):
    if week_hour() >= 4 and week_hour() <= T0:
        return False
    else:
        return True
def time_till_dink(T0 = 4*24+16):
    return T0 - week_hour()+1

def live_on_twitch(channelName='therealgpf'):
    contents = requests.get('https://www.twitch.tv/' + channelName).content.decode('utf-8')
    if 'isLiveBroadcast' in contents: 
        print(channelName + ' is live')
        return True
    else:
        print(channelName + ' is not live')
        return False


file = pd.read_csv('Dinking.csv')
IDs = list(file['ID'])
points = list(file['points'])
Totaldink = list(file['dinks'])
TotalHandouts = list(file['Handouts'])


def ID_Tracker(ID,opt): 
    #0: dink
    #1: Got dinked
    #2: Random Handout
    stored_IDs = [int(s[:-4]) for s in os.listdir('./UserTracker/') if '.csv' in s]
    if ID in stored_IDs:
        file = pd.read_csv('./UserTracker/%i.csv'%ID)
        Time = list(file['Time'])
        value = list(file['value'])
        Time.append(time.time())
        value.append(opt)
    else:
        Time = [time.time()]
        value = [opt]
    df = pd.DataFrame({'Time':Time , 'value':value})
    df.to_csv('./UserTracker/%i.csv'%ID,index=False)





def Delete(User_ID):
    i_ID = [i for i in range(len(IDs)) if IDs[i] == User_ID][0]
    leaving_points = points[i_ID]
    del IDs[i_ID]
    del points[i_ID]
    del Totaldink[i_ID]
    del TotalHandouts[i_ID]
    print("Leaving with %i points"%leaving_points)
    if leaving_points < 5:
        P =  5-leaving_points
        i = 0
        while i < P:
            points[np.random.choice(np.arange(len(IDs)),p=np.array(points)/np.sum(points))] += -1
            i += 1
    elif leaving_points > 5:
        P =  leaving_points-5
        i = 0
        while i < P:
            pp = 1/(np.array(points)+1e-5)/np.sum(1/(np.array(points)+1e-5))
            points[np.random.choice(np.arange(len(IDs)),p=pp)] += +1
            i += 1
    
    df = pd.DataFrame({'ID':IDs , 'points':points , 'dinks':Totaldink , 'Handouts':TotalHandouts})
    df.to_csv('Dinking.csv',index=False)
    
def Clear_all():
    IDs.clear()
    points.clear()
    Totaldink.clear()
    TotalHandouts.clear()
    df = pd.DataFrame({'ID':IDs , 'points':points , 'dinks':Totaldink , 'Handouts':TotalHandouts})
    df.to_csv('Dinking.csv',index=False)
    
def prob_proportionality(points,exponent=2):
    return np.array(points)**exponent/np.sum(np.asarray(points)**exponent)

def Random(IDs,points,N=1):
    return np.random.choice(IDs,size=N,p=prob_proportionality(points))




def FirstPlayer(ID):
    IDs.append(ID)
    points.append(5)
    Totaldink.append(0)
    TotalHandouts.append(0)


def Update(caller,dinkees,Handout=False): #dinkees must be a list
    N = len(dinkees)
    if caller in IDs and not Handout:
        i_caller = [i for i,ID in enumerate(IDs) if ID == caller][0]
        points[i_caller] +=  N
        if N < 2:
            Totaldink[i_caller] += 1
        else:
            Totaldink[i_caller] += N
    elif not Handout:
        IDs.append(caller)
        points.append(6)
        Totaldink.append(1)
        TotalHandouts.append(0)
    
    for i,ID in enumerate(dinkees):
        if ID in IDs and not Handout:
            i_dinked = [i for i,iD in enumerate(IDs) if iD == ID][0]
            TotalHandouts[i_dinked] += 1
            if points[i_dinked]>0:
                points[i_dinked] += -1
        if ID in IDs and Handout:
            i_dinked = [i for i,iD in enumerate(IDs) if iD == ID][0]
            TotalHandouts[i_dinked] += 1
                
    df = pd.DataFrame({'ID':IDs , 'points':points , 'dinks':Totaldink , 'Handouts':TotalHandouts})
    df.to_csv('Dinking.csv',index=False)

def Reset():
    for i in range(len(IDs)):
        points[i] = 5
        Totaldink[i] = 0
        TotalHandouts[i] = 0
    df = pd.DataFrame({'ID':IDs , 'points':points , 'dinks':Totaldink , 'Handouts':TotalHandouts})
    df.to_csv('Dinking.csv',index=False)

drunk_gif_list = ['https://i.makeagif.com/media/9-21-2015/mbewqE.gif'
                  ,'https://media.giphy.com/media/KctNhiy99LoLBTgLNO/giphy.gif'
                  ,'https://i.pinimg.com/originals/5b/8c/32/5b8c32f2177993c8c177548f8696f97f.gif'
                  ,'https://media.giphy.com/media/3oEjI9T0ixjZCFwi8U/giphy.gif'
                  ,'https://media.giphy.com/media/E3L5goMMSoAAo/giphy.gif'
                  ,'https://media.giphy.com/media/K34FVrUx8ggyA/giphy.gif'
                  ,'https://media4.giphy.com/media/l0Iy8G3PwyahZST2E/200.gif'
                  ,'https://media.tenor.com/images/d26c4abe0085bd1b0e29acacda30a769/tenor.gif'
                  ,'https://media4.giphy.com/media/26xBwu0ZZVWbG7gA0/giphy.gif'
                  ,'https://media.giphy.com/media/llZVEOIi9tCVxFskpY/giphy.gif'
                  ,'https://media.giphy.com/media/NCZQhdPbCNmwM/giphy.gif'
                  ,'https://media.giphy.com/media/Jrk7tpcTZtwcg/giphy.gif'
                  ,'https://media.giphy.com/media/NPAB0vUr8nfR6/giphy.gif'
                  ,'https://tenor.com/view/mimosa-drinking-cocktails-i-just-had-one-drink-alcoholic-gif-15802079'
                  ]
Mandy_vids = ['Oh you want MANDY? Here is a Mandy set with fucking VILLAIN as MC:  https://youtu.be/WJtVm25iP80'
              ,"I hope you're ready for some shitty mixing.... https://youtu.be/PPkFMtrinZU"
              ,'I cannot believe you actually want this... https://youtu.be/nFf9s2e2iCc'
              ,'https://youtu.be/Y6ddPorsZy8 There you go.. Unfortunately.'
              ,'We are all online, so why not cry using this online set with Mandy https://youtu.be/IfQYM1Ugbek'
              ]
Neckbeard_gifs = ['https://c.tenor.com/CdRnkNKsx9wAAAAM/epic-hat.gif'
                  ,'https://cdn.discordapp.com/attachments/778287703300505650/861352301566623754/image0.gif'
                  ,'https://c.tenor.com/FDdqrAlNNg0AAAAM/louis-neckbeard.gif'
                  ,'https://c.tenor.com/pjW1WjTke7YAAAAj/neckbeard-fat.gif'
                  ,'https://i.redd.it/bjwcretcwfb11.gif'
                  ,'https://c.tenor.com/1eYfGYelSRkAAAAM/tiktok-mouth.gif'
                  ,'<:pablo:861353940481998898>'
                  ]
crywank_gifs = ['https://i.imgur.com/y4ROWoJ.mp4'
                ,'https://cdn.discordapp.com/attachments/730787222445490252/878340666718044170/SmartSelect_20210820-201119_YouTube.gif'
                ]



import random
def rotate(l, n):
    return l[n:] + l[:n]
orders = [[0]]*2
for i in range(98):
    orders.append(list(np.arange(i+2)))
    random.shuffle(orders[i+2])

def Link_selector(link_list):
    N = len(link_list)
    choice = orders[N][0]
    orders[N] = rotate(orders[N],1)
    return link_list[choice]

def liner(string):
    sep = '\n'
    out = string[0]
    for i in range(len(string)-1):
        out += sep + string[i+1]
    return out
def wave(string,amplitude = 100,Nstop= 5):
    List = []
    space = []
    Nz = 0
    for i in range(200):
        space.append(np.floor(amplitude * np.sin(i/5)**2 * np.exp(-i/20) ).astype(int))
        if space[-1] == 0:
            Nz += 1
            if Nz>Nstop-1:
                space = space[:-Nstop+1]
                break
        else:
            Nz = 0
    for i in range(len(space)):
        List.append(  ' '* space[i]  + string + "\n"  )
    total = ''.join(List)
    if len(total) > 2000:
        total = total[:2000]
        end = total[::-1].index('\n')+1
        total = total[:-end]
    return total



#------MARKOV-------------------------------------------------------------------------------
def MarkovModel(file):
    text = list(pd.read_csv(file)['message'])
    return mk.Text(text)
text_model = MarkovModel('LoggedText0.csv')
markov_chance_percentage = 5

def Generate_sentence(pct=markov_chance_percentage,length = None):
    if np.random.rand()<pct/100:
        if length == None:
            msg = text_model.make_sentence(length)
            while msg == None:
                msg = text_model.make_sentence(length)
        else:
            msg = text_model.make_short_sentence(length)
            while msg == None:
                msg = text_model.make_short_sentence(length)
        return msg
    else:
        return None
markov_channels = [870997447374176267,863028160795115583,857670559038570507]
#-------------------------------------------------------------------------------------------

import discord
import asyncio
client = discord.Client()
@client.event  # event decorator/wrapper
async def on_ready():
    print(f"Logged in as {client.user}")
    # text_channel_list = []
    # for channel in client.get_all_channels():
    #     text_channel_list.append(channel.name)
    # print(text_channel_list)







#-----------------------------------------------------------------------
spam_commands = ["wave [content]"
                 ,"bbcum/cum"
                 ,"cope/seethe"
                 ,"bbfriend"
                 ,"bbcyka/bbblyat"
                 ,"bbMandy"
                 ,"bbshitpost"
                 ,'crywank'
                 ]
spam_desc     = ["Create an exponentially decaying squared sinusoidal wave of [content]. (Only works with GPF and default emojis and any message)"
                 ,"Random cum related stuff."
                 ,"Random cope/seethe related stuff."
                 ,"Random wholesome related stuff."
                 ,"Random russia related stuff."
                 ,"Random Mandy related stuff."
                 ,"We believe you get it by now"
                 ,'Crywank?..'
                 ]
#-----------------------------------------------------------------------
utility_commands = ["Hello"
                    ,"!zoom"
                    ,"?live/!live"
                    ,"GPF"
                    ,"mizzy"
                    ,"horren"
                    ]
utility_desc    = ["Checks if Villain is online"
                   ,"GPF/Mizzy zoom call."
                   ,"Check if a twitch user is online"
                   ,"GPF    twitch link an live status"
                   ,"Mizzy  twitch link an live status"
                   ,"Horren twitch link an live status"
                   ]
#-----------------------------------------------------------------------
dinking_commands = [ "bbdink"
                    ,"bbdink [user]"
                    ,"opt in"
                    ,"opt out"
                    ,'Coinflip'
                    ,"bbtally"
                    ,"bbprob"
                    ]
dinking_desc = ["Dinks a random user (ALTs: bbskål & bbprost)."
                ,"Dinks a specific user or users. (supports ALTs)"
                ,"Join the dinking game."
                ,"Leave the dinking game."
                ,"Dink if you guess the wrong outcome of coinflip"
                ,"Tally for players in the game."
                ,"probability to get selected at random"
                ]
#-----------------------------------------------------------------------
admin_commands = [ "bbreset"
                    ,"bbspam"
                    ,"bboverride"
                    ,"bbvillain"
                    ,"opt out [user]"
                    ,"bbtime N,t"
                    ,"bbclear"
                    ]
admin_desc = ["Resets all tallys and points (5 points 0 dinks/drinks)."
                ,"Toggle the spam commands."
                ,"Toggles the dinking time blocker, resets upon restart."
                ,"Dink all players in the game (30min cooldown)."
                ,"opt a specific user out."
                ,"Trigger *N* random dinks by the bot spaced *t* minutes apart."
                ,"Remove all players and reset."
                ]
#-----------------------------------------------------------------------
def string_gen(commands,desc):
    command_length = [len(s) for s in commands]
    N_max = max(command_length)
    extended = []
    for i,s in enumerate(commands):
        extended.append( "`%s` " %   (s + " "*(  N_max-command_length[i]) + ":"  )   )
        extended[i] += desc[i]+'\n'
    return extended




Fun = True
admin_dink_time_override = False
Sponsor_message = False
N_requirement = 3
Fredag_post = False

T0 = [0]
T_dink = [0]
Trusted_IDs = list(np.loadtxt('Trusted_IDs.txt',np.int64)) ; Temp_Trusted = []
bbvillain_IDs = list(np.loadtxt('Trusted_IDs.txt',np.int64))
Channels = list(np.loadtxt('Channels.txt',np.int64))
repeat_channels = [730787222445490252,857670559038570507,863028160795115583,810263180533956708,778287703300505650,743024581916360755]
blacklist = []
dink_blacklist = [652986939443773450]




#auto removal after set amount of time (time tracker)




timer_IDs = {}
timer_times = {}
def countdown_timer(ID,counter='hey',cooldown = 6*60**2): #Check if user said Hi to Villin within cooldown time (cooldown in seconds)
    if counter not in timer_IDs:
        timer_IDs[counter] = []
        timer_times[counter] = []
    if ID in timer_IDs[counter]:
        i_ID = timer_IDs[counter].index(ID)
        if time.time() - timer_times[counter][i_ID] >= cooldown:
            timer_times[counter][i_ID] = time.time()
            return True
        else:
            return False
    else:
        timer_IDs[counter].append(ID)
        timer_times[counter].append(time.time())
        return True
def countdown_timer_left(ID,counter='hey',cooldown = 6*60**2):
    i_ID = timer_IDs[counter].index(ID)
    time_left = time.time() - timer_times[counter][i_ID]
    return int(np.ceil(  (cooldown - time_left)  /60))












@client.event
async def on_message(message):
    global Fun, admin_dink_time_override, Trusted_IDs, Sponsor_message, Temp_Trusted , Fredag_post
    if message.author != client.user and message.channel.id in repeat_channels:
        
        message_history = [];all_message_history = [];ID_history = [];all_ID_history = []
        async for msg in message.channel.history(limit=7+N_requirement):
            all_message_history.append(msg.content)
            all_ID_history.append(msg.author.id)
            if msg.author != client.user:
                message_history.append(msg.content)
                ID_history.append(msg.author.id)
        if len(np.unique([x.lower() for x in message_history[:N_requirement]])) == 1:
            if len(np.unique(ID_history[:N_requirement])) == N_requirement and client.user.id not in all_ID_history[:N_requirement]:
                await message.channel.send(message.content)
    
    if message.channel.id in markov_channels:
        if message.content.lower()[:10] == 'percentage' and message.author.id in Trusted_IDs:
            global markov_chance_percentage
            try:
                new_pct = float(message.content.lower()[11:])
                if new_pct >= 0 and new_pct <= 100:
                    markov_chance_percentage = new_pct
                    await message.channel.send( 'Villain trigger chance changed to %.4g%%'% (markov_chance_percentage),delete_after = 10)
                else:
                    await message.reply('Percentage must be between 0 and 100',delete_after = 10)
            except:
                await message.reply('Invalid syntax',delete_after = 10)
        if message.content.lower() == 'vtrigger':
            await message.channel.send(Generate_sentence(100),allowed_mentions=discord.AllowedMentions(users=False))
        elif message.reference is not None:
            messg = await client.get_channel(message.channel.id).fetch_message(message.reference.message_id)
            if messg.author == client.user:
                await message.reply(Generate_sentence(100),allowed_mentions=discord.AllowedMentions(users=False))
        elif message.author != client.user:
            mark_msg = Generate_sentence(markov_chance_percentage)
            if mark_msg != None:
                await message.channel.send(mark_msg,allowed_mentions=discord.AllowedMentions(users=False))
    
    
        


    if message.author.id in Trusted_IDs and message.content.lower() == 'villain, engage fed mode':
        await message.channel.send('Alright stealing all the messages in this channel (this will take a while)',delete_after=10)
        async def Logger(limit=None):
            T0 = time.time()
            i = 0
            print('-----------------------------------------------------------')
            print('Logging commenced')
            messages = []
            author = []
            date = []
            everything = []
            async for d in message.channel.history(limit=limit):
                i+=1
                if not d.author.bot and len(d.content)>0 and 'http' not in d.content:
                    messages.append(d.content)
                    author.append(d.author.name)
                    date.append(d.id)
                    everything.append(d)
                    if i%5000 == 0:
                        TN = time.time()
                        TD = TN - T0
                        print('%i done at %i per sec' % (i,i/TD))
            TN = time.time()
            TD = TN - T0
            print('%i done at %i per sec' % (i,i/TD))
            print('Total time was %i seconds'%(TD))
            print('-----------------------------------------------------------')
            await message.channel.send('Total of %i messaged logged in %i minutes at %i messages per second' % ( i , (TD)/60 , i/(TD) ) ,delete_after=10)
            df = pd.DataFrame({'author':author , 'message':messages , 'date':date , 'everything':everything})
            df.to_csv('LoggedText.csv',index=False)
        await Logger()
    

    
    if (message.author != client.user and message.channel.id in Channels) and message.author.id not in blacklist:
        print(f"{message.channel}: {message.channel.id}: {message.author.name}: {message.content}")

        
        if 'hello villain' == message.content.lower() or 'hey villain' == message.content.lower():
            if countdown_timer(message.author.id,'hey'):
                await message.reply('Hey x, weekend warrior!')
        if 'hello' == message.content.lower():
            if countdown_timer(message.author.id,'hey'):
                await message.reply('Hey weekend warrior!')
        if 'hello boys' == message.content.lower() or 'hello boys.' == message.content.lower():
            if countdown_timer(message.author.id,'pablo',cooldown=30*60):
                await message.reply(Link_selector(Neckbeard_gifs))
        if 'bye villain' == message.content.lower() and countdown_timer(message.author.id,'leaving'):
            await message.reply('There is no leaving (apart from opting out)')

        
        if "!zoom" == message.content.lower():
            await message.channel.send('GPF: https://hot.greazy.co/zoom')
            
        if "GPF" == message.content or "bbgpf" == message.content.lower():
            if live_on_twitch('therealgpf'):
                await message.channel.send('Watch GPF live at: https://www.twitch.tv/therealgpf')
            else:
                await message.channel.send('GPF is currently offline :( (https://www.twitch.tv/therealgpf)')
        if "mizzy" == message.content.lower() or "bbmizzy" == message.content.lower():
            if live_on_twitch('mizzbehaveofficial'):
                await message.channel.send('Watch MizzBehave live at: https://www.twitch.tv/mizzbehaveofficial')
            else:
                await message.channel.send('MizzBehave is currently offline :( (https://www.twitch.tv/mizzbehaveofficial)')
        if "horren" == message.content.lower() or "bbhorren" == message.content.lower():
            if live_on_twitch('captainhorren'):
                await message.channel.send('Watch horren live at: https://www.twitch.tv/captainhorren')
            else:
                await message.channel.send('Horren is currently offline :( (https://www.twitch.tv/captainhorren)')
        
        
        if "?live" in message.content.lower()[:5] or "!live" in message.content.lower()[:5]:
            channel_Name = message.content[6:]
            if live_on_twitch(channel_Name):
                await message.channel.send("YAY! %s is live right now! https://www.twitch.tv/%s" % (channel_Name,channel_Name))
            else:
                await message.channel.send("Oh nooo... %s seems to be offline :(" % (channel_Name))
        
            
            
        if 'blacklist' == message.content.lower()[:9] and message.author.id in Trusted_IDs:
            target = int(message.content.lower()[10:])
            if target not in Trusted_IDs:
                blacklist.append(target)
                if target in IDs:
                    Delete(target)
                await message.reply('User added to blacklist')
        if 'dink blacklist' == message.content.lower()[:14] and message.author.id in Trusted_IDs:
            target = int(message.content.lower()[10:])
            if target not in Trusted_IDs:
                dink_blacklist.append(target)
                if target in IDs:
                    Delete(target)
                await message.reply('User added to dinking blacklist')
        
        
        if 'bbspam' in message.content.lower()[:6] and message.author.id in Trusted_IDs:
            if not Fun:
                Fun = True
                await message.channel.send('Sperm now enabled')
            elif Fun:
                Fun = False
                await message.channel.send('Sperm now disabled')
        if 'bbspam' in message.content.lower()[:6] and message.author.id not in Trusted_IDs:
            await message.channel.send(f'{message.author.mention}. Only LeCerial and Truxa has the right to touch sperm. 👀')
            
        if Fun:
            if 'bbmandy' in message.content.lower()[:7]:
                await message.channel.send(Link_selector(Mandy_vids))
            if 'bbengland' in message.content.lower()[:9]:
                await message.channel.send(file=discord.File('./images/england/%s' % Link_selector([s for s in os.listdir("./images/england/") if '.ini' not in s])))
            if 'cope' in message.content.lower()[:4] or 'seethe' in message.content.lower()[:6]:
                await message.channel.send(file=discord.File('./images/cope/%s' % Link_selector([s for s in os.listdir("./images/cope/") if '.ini' not in s])))
            if 'bbfren' in message.content.lower()[:6] or 'bbfrien' in message.content.lower()[:7] or 'bbfriend' in message.content.lower()[:8]:
                await message.channel.send(file=discord.File('./images/fren/%s' % Link_selector([s for s in os.listdir("./images/fren/") if '.ini' not in s])) )
            if 'bbcyka' in message.content.lower()[:6] or 'bbrus' in message.content.lower()[:5] or 'bbblyat' in message.content.lower()[:7]:
                await message.channel.send(file=discord.File('./images/russia/%s' % Link_selector([s for s in os.listdir("./images/russia/") if '.ini' not in s])) )
            if 'bbcum' in message.content.lower()[:5]  or 'cum' in message.content.lower()[:3] or 'sborra' in message.content.lower()[:6]:
                await message.channel.send(file=discord.File('./images/cum/%s' % Link_selector([s for s in os.listdir("./images/cum/") if '.ini' not in s])) )        
            if 'crywank' == message.content.lower() or 'bbcrywank' == message.content.lower():
                await message.channel.send(Link_selector(crywank_gifs))
            if 'bbshitpost' in message.content.lower()[:10]  or 'shitpost' == message.content.lower() or 'lortepæl'== message.content.lower():
                if not Fredag_post and int(time.strftime('%w',time.gmtime())) == 5:
                    await message.reply('NU ÄR DET FREDAG!!!',file=discord.File('./images/shitpost/friday33.mp4'))
                    Fredag_post = True
                else:
                    File_Selected = Link_selector([s for s in os.listdir("./images/shitpost/") if '.ini' not in s])
                    while 'friday33' in File_Selected:
                        File_Selected = Link_selector([s for s in os.listdir("./images/shitpost/") if '.ini' not in s])
                    await message.channel.send(file=discord.File('./images/shitpost/%s' %File_Selected ) )
                if Fredag_post and int(time.strftime('%w',time.gmtime())) != 5:
                    Fredag_post = False
            
            
            
            if 'wave' in message.content.lower()[:4]:
                T_wave_cooldown = 30*60
                if countdown_timer(message.author.id,'emoji',T_wave_cooldown) or (message.author.id in Trusted_IDs or message.author.id in Temp_Trusted):
                    emoji = message.content[5:]
                    await message.channel.send( wave(emoji) )
                else:
                    t_left = countdown_timer_left(message.author.id,'emoji',T_wave_cooldown)
                    await message.reply('This command has a %i minute cooldown per user. (%i min left)' % (T_wave_cooldown/60,t_left) )
            
            
        if 'trust' == message.content.lower()[:5] and message.author.id in Trusted_IDs:
            if len(message.mentions)>0:
                mentions = [s.id for s in message.mentions if (s.id not in Trusted_IDs)]
                for ID in mentions:
                    Temp_Trusted.append(ID)
        
        
        
            
        if 'calculate' in message.content.lower()[:9] and (message.author.id in Trusted_IDs or message.author.id in Temp_Trusted):
            await message.channel.send(Calculator(message.content[10:]))
        
        # if 'raidtrain' in message.content.lower():
        #     await message.channel.send(current_stream(int(time.strftime('%H',time.gmtime()))))
        #     if int(time.strftime('%H'))<18:
        #         await message.channel.send('Planned schedule:')
        #         await message.channel.send('https://cdn.discordapp.com/attachments/865152397192855572/868789061198966804/Semen.png')
            
            

        if 'fuck off bot' == message.content.lower() and message.author.id in Trusted_IDs:
            await message.channel.send('Okay bye')
            await client.close()
        if 'update bot' == message.content.lower() and message.author.id in Trusted_IDs:
            await message.channel.send('Updating from github')
            if 'win' not in sys.platform:
                exec_return = os.system('git pull https://github.com/AndreHartwigsen/DinkingBot.git')
                print(exec_return)
        if 'fuck off bot then come back' == message.content.lower() and message.author.id in Trusted_IDs:
            await message.channel.send('Okay restarting')
            if 'win' not in sys.platform:
                os.system('git pull https://github.com/AndreHartwigsen/DinkingBot.git')
                await client.close()
            else:
                os.execv(sys.executable, ['python'] + sys.argv)
        if 'kill bot' == message.content.lower() and message.author.id in Trusted_IDs:
            os.system('pm2 stop DinkingBot')
            await client.close()


        
        if 'bbclear' == message.content.lower() and message.author.id in Trusted_IDs:
            Clear_all()
            await message.channel.send('All dinking data removed')
        
        if 'bbhelp' in message.content.lower():
            embed = discord.Embed(title=f'List of {client.user.name}™️ commands:',colour=discord.Colour.orange())
            embed.set_author(name=client.user.name, icon_url=client.user.avatar_url)
            embed.add_field(name='Dinking Related (Fri 4pm - Mon 4am CET):',    value=''.join(string_gen(dinking_commands,dinking_desc)),inline=False)
            embed.add_field(name='Utility commands:',                           value=''.join(string_gen(utility_commands,utility_desc)),inline=False)
            embed.add_field(name='Spam related:',                               value=''.join(string_gen(spam_commands,spam_desc)),inline=False)
            embed.set_footer(text=[f'{client.user.name}™️ takes no responsibility for any following or imminent alcoholism caused by dinking. \n'
                              +'Apart from random handouts given by the bot, and people dinking other people specifically '
                              +'(prevention of this is WIP), a maximum of 5 dinks more than the amount of dinks handed out can be '
                              +'received. Probability to be selected at random is based on the square of normalized points, dinking '
                              +'someone will give you their point. Every player starts with 5 points, hence the 5 drink max by random '
                              +'selection. The game is set up to dink the people who dink the most. \n'
                              + ["Dinking is active in %i hours" % (time_till_dink()) if not dink_time() else 'Dinking is active RIGHT NOW!'][0]
                              ][0] )
            await message.reply(embed=embed)
            
            if message.author.id in Trusted_IDs:
                embed = discord.Embed(title=f'List of {client.user.name}™️ commands:',colour=discord.Colour.red())
                embed.add_field(name='Admin commands:',value=''.join(string_gen(admin_commands,admin_desc)),inline=False)
                embed.set_footer(text=['Current status:\n'
                                       +"Dink Timer   : %s\n" % ( not admin_dink_time_override )
                                       +"Spam enabled : %s\n" % Fun
                                       ][0])
                await message.author.send("You are in the trusted IDs, so here are the admin commands.",embed=embed)
            




#------------------------------------- DINKING RELATED STUFF-----------------------------------------#

        bc = ["bbdink","bbprost","bbskål","bbreset","bbtally",'bbprob','bbprobbig','bbprob big','bbtime','bbvillain','coinflip']
        def check_command(msg=message.content.lower()):
            for s in bc:
                if s in msg[:len(s)]:
                    return True
            return False


        
        if 'bboverride' == message.content.lower() and message.author.id in Trusted_IDs:
            if not admin_dink_time_override:
                admin_dink_time_override = True
                await message.channel.send('Dinking now enabled')
            elif admin_dink_time_override:
                admin_dink_time_override = False
                await message.channel.send('Dinking now back to normal schedule. %i Hours left.'%(time_till_dink()))
        
        Nicks = []
        for ID in IDs:
            username = await client.fetch_user(ID)
            Nicks.append(str(username)[:-5]) 
        if (dink_time() or admin_dink_time_override or message.author.id in Trusted_IDs) and message.author.id not in dink_blacklist:
            
            
            async def Tally(Message=None):
                if len(IDs) > 0:
                    embed2 = discord.Embed(title= 'Dinking Tally')
                    embed2.add_field(name='User', value=liner(["<@%i>" % i for i in IDs]))
                    embed2.add_field(name='Dinks used', value=liner(["%i" % i for i in Totaldink]))
                    embed2.add_field(name='Dinks recieved', value=liner(["%i" % i for i in TotalHandouts]))
                    embed2.set_thumbnail(url=Link_selector(drunk_gif_list))
                    if Message == None:
                        await message.reply(embed=embed2)
                    else:
                        await message.channel.send(Message,embed=embed2)
                else:
                    await message.channel.send('No players in the game')
            async def PROB(Message=None):
                embed2 = discord.Embed(title= 'Dinking Probability')
                embed2.add_field(name='User', value=liner(["<@%i>" % i for i in IDs]))
                embed2.add_field(name='Probability', value=liner(["%.3g%%" % i for i in (100*prob_proportionality(points))]))
                if Message == None:
                    await message.channel.send(embed=embed2)
                else:
                    await message.reply(Message,embed=embed2)
    
    
            if 'bbsponsor' == message.content.lower() and message.author.id in Trusted_IDs:
                if Sponsor_message:
                    Sponsor_message = False
                else:
                    Sponsor_message = True
                
    
            if "bbdink" in message.content.lower()[:6] or "bbprost" in message.content.lower()[:7] or "bbskål" in message.content.lower()[:6] or "bbcheers" in message.content.lower()[:8]:
                if len(IDs)<1:
                    FirstPlayer(message.author.id)
                sponsor = " (message sponsored by juizzx)" if Sponsor_message else ''
                message_list = [f'Welp..! {message.author.name} wants %s to DINK ONE! Take one for the team and down your entire glass!'+sponsor
                                ,f'Raise your hands, Weekend Warrior! And make sure there is a shot in it, cause {message.author.name} wants %s to DINK ONE MOAR!'+sponsor
                                ,f"I'm an Alcoholic 'til the day that I die! And so is %s, {message.author.name} chose you to DINK ONE MOAR now!"+sponsor
                                ,f"Are you as good as Villain with drops?! Then %s should drop down ONE MOAR DINK cause {message.author.name} said so!"+sponsor
                                ,f"HEEEEEE! HOOOOOO! %s GOT VILLAINED by {message.author.name}! DINK NOW!"+sponsor
                                ,f"Make some nooooise! It's time to DINK ONE MOAR for %s, thanks to {message.author.name}!"+sponsor
                                ,f"At the top of your lungs, give it up for {message.author.name} that DINKED %s! Down ONE MOAR shot right now!"+sponsor
                                ,f"I can't heaaar you, Weekend Warriors! Everyone put their hands together for the next DINK! {message.author.name} VILLAINED %s!"+sponsor
                                ,f"Oh shit no. %s just got VILLAINED by {message.author.name}!!  Now YOU HAVE TO DINK ONE MOAR, otherwise you will be haunted by Villain tonight."+sponsor
                                ]
                
                sponsor =  " (Nachricht gesponsert von juizzx)" if Sponsor_message else ''
                message_list_de = [f'Nun..! {message.author.name} will, dass %s EINEN DINKT! Nimm einen für’s ganze Team und DINK dein ganzes Glas!'+sponsor
                                ,f'Hoch die Hände, Weekend Warrior! Und stell‘ sicher, dass sich ein Shot darin befindet, denn {message.author.name} will, dass %s NOCH EINEN DINKT!'+sponsor
                                ,f"Ich bin Alkoholiker bis zu dem Tag, an dem ich sterbe! Und so ist auch %s, {message.author.name} hat dich ausgewählt um jetzt EINEN ZU DINKEN!"+sponsor
                                ,f"Bist du so gut wie Villain mit Drops?! Dann sollte %s NOCH EINEN DINK hinunterstürzen, denn {message.author.name} verlangt es so!"+sponsor
                                ,f"HEEEEEE! HOOOOOO! %s wurde von {message.author.name} GEVILLAINED! DINK JETZT!"+sponsor
                                ,f"Macht ein bisschen Lärm! Dank {message.author.name} ist es Zeit für %s, NOCH EINEN ZU DINKEN!"+sponsor
                                ,f"Aus vollem Hals, macht Lärm für {message.author.name}, denn {message.author.name} hat %s GEDINKED! Kipp jetzt NOCH EINEN MEHR runter!"+sponsor
                                ,f"Ich kann euch nicht hööööören, Weekend Warriors! Klappt mal alle eure Hände zusammen für den nächsten DINK! {message.author.name} hat %s GEVILLAINED!"+sponsor
                                ,f"Oh scheiße. %s wurde gerade von {message.author.name} GEVILLAINED!!  DINK noch einen, sonst wird Villain dich heute Nacht heimsuchen."+sponsor
                                ]
                
                sponsor = " (Denne meddelse er sponsoreret af juizzx)" if Sponsor_message else ''
                message_list_dk = [f'Åhh nej! {message.author.name} vil have %s til at DINK EN! Tag en for holdet og drik hele dit glas!'+sponsor
                                ,f'Ræk dine hænder op, Weekend Kriger! Og sikrer dig at der er et shot i dem, fordi {message.author.name} vil have at %s skal DINK EN MERE!'+sponsor
                                ,f"Jeg er en alkoholiker til den dag jeg DØR! Og det er %s også! {message.author.name} har valgt dig til at DINK EN MERE!"+sponsor
                                ,f"Er du lige så god som Villain til at bunde?! Så skal %s bunde EN MERE DINK fordi {message.author.name} sagde det!"+sponsor
                                ,f"HEEEEEE! HOOOOOO! %s BLEV VILLAINERET af {message.author.name}! DINK NU!"+sponsor
                                ,f"Lav noget LAAARM! Det er tid til at DINK EN MERE for %s, takket være {message.author.name}!"+sponsor
                                ,f"Lad os høre jer, give det op for {message.author.name} der har DINKERET %s! Drik ET MERE shot lige nu!"+sponsor
                                ,f"Jeg kan ikke høøøre jer, Weekend Krigere! Alle sammen, put jeres hænder sammen for den næste DINK! {message.author.name} VILLAINERER %s!"+sponsor
                                ,f"Åhh nej. %s er lige blevet VILLAINERET af {message.author.name}!!  Nu bliver du nødt til at DINK EN MERE, ellers vil du blive hjemsøgt af Villain i nat."+sponsor
                                ]
                
                p_message_list = np.array([10]*len(message_list))
                p_message_list[0] = 1
                p_message_list[1] = 3
                
                dinker = message.author.id
                N_dinked = len(message.mentions)
                if N_dinked > 0:
                    mentions_list = [s.id for s in message.mentions if s.id in IDs]
                    mentions_name = [s.name for s in message.mentions if s.id in IDs]
                    mentions_not_in = [s.id for s in message.mentions if s.id not in IDs]
                    mentions_not_name = [s.name for s in message.mentions if s.id not in IDs]
                    N_in = len(mentions_list)
                    N_out = len(mentions_not_in)
                    print(mentions_name,mentions_not_name)
                else:
                    N_in = 0
                    N_out = 0
                
    
                if N_in == 0: #if no people are mentioned, chose random from IDs list
                    dinkee = Random(IDs,points)
                else:         #If people were  tagged,  chose the ones that are  on the ID list
                    dinkee = mentions_list
                    
                if len(dinkee) == 1:
                    string = "<@%i>" % (dinkee[0])
                else:
                    names = ["<@%i>" % i for i in dinkee]
                    string = list_creator(names)
            
            
                Update(dinker,dinkee)
                
                
                
                ID_Tracker(dinker, 0)
                for i in dinkee:
                    ID_Tracker(i, 1)
                
                
                
                
                if message.author.id in IDs:
                    i_ID = [i for i in range(len(IDs)) if IDs[i] == message.author.id][0]
                    embed = discord.Embed(title=f'{message.author.name} just dinked!')
                    embed.add_field(name='Counter',value='Dinks performed: \n Dinks recieved: \n Dink probability:')
                    embed.add_field(name='Value',value=liner(['%i'%Totaldink[i_ID],'%i'%TotalHandouts[i_ID],'%.3g%%'%((100*prob_proportionality(points)[i_ID]))] ))
                else:
                    embed = discord.Embed()
                embed.set_thumbnail(url='https://i.imgur.com/0yHN9n1.jpeg')
                
                if N_out >0: #Tell  the users that some people have not yet used the dink command
                    if N_out == 1:
                        non_dink = mentions_not_name[0]
                    else:
                        non_dink= list_creator(mentions_not_name)
                    await message.channel.send(f'{message.author.mention} Some people have not yet dinked (%s) and can therefore not be dinked yet :( A random person was chosen instead'%non_dink)
                print(points,np.mean(points))
    
                if   'bbskål'  in message.content.lower():
                    message_paste = np.random.choice(message_list_dk,p=np.asarray(p_message_list)/np.sum(p_message_list))
                elif 'bbprost' in message.content.lower():
                    message_paste = np.random.choice(message_list_de,p=np.asarray(p_message_list)/np.sum(p_message_list))
                else:
                    message_paste = np.random.choice(message_list   ,p=np.asarray(p_message_list)/np.sum(p_message_list))
                if 'small' not in message.content.lower():
                    await message.channel.send(message_paste % string,embed=embed)
                else:
                    await message.channel.send(message_paste % string)

    
    
            if "bbreset" in message.content.lower()[:7] and message.author.id in Trusted_IDs:
                Reset()
                print(points,np.mean(points))
                embed2 = discord.Embed(title= 'LeCerial reset the tally 👀')
                embed2.add_field(name='User', value=liner(["<@%i>" % i for i in IDs]))
                embed2.add_field(name='Dinks used', value=liner(["%i" % i for i in Totaldink]))
                embed2.add_field(name='Dinks recieved', value=liner(["%i" % i for i in TotalHandouts]))
                embed2.set_thumbnail(url='https://media.giphy.com/media/Ws4Mtju5Sq1swakFzU/giphy.gif')
                await message.channel.send('All tallys have been reset 😌',embed=embed2)
                
                
            if "bbtally" in message.content.lower()[:7]:
                await Tally()
            
            
            
            M6 = message.content.lower()[:6]
            if "bbsink" in M6 or "bbeink" in M6 or "bbfink" in M6 or "bbxink" in M6:
                await message.channel.send(f'{message.author.mention} mispelled bbdink, the drunk  bastard 👀')
            if 'bbdrink' in message.content.lower()[:7]:
                await message.channel.send(f'{message.author.mention} mispelled bbdink 👀.. SHAME! SHAME! SHAME!')
                
              
                
                
                
                
                
            if 'bbprobbig' in message.content.lower()[:len('bbprobbig')] or 'bbprob big' in message.content.lower()[:len('bbprob big')]:
                if len(IDs)>0:
                    def Pie(name='Pie.png'):
                        plt.figure(figsize=(6,4),dpi=150)
                        ax = plt.subplot(111)
                        labels = Nicks
                        ex = [0]*len(IDs)
                        for i in ex:
                            if i >= np.max(points):
                                ex[i] = 0.1
                        wedges, texts,autotext= ax.pie(points,explode=ex,labels=labels,autopct='%.1f%%',radius=1.2,textprops=dict(color="w"))
                        plt.savefig(name,transparent=True)
                    Pie()
                    file = discord.File("Pie.png", filename="Probability.png")
                    await message.reply('Probability to get selected at random',file=file)
                else:
                    await message.reply('No players in the game')
            elif 'bbprob' in message.content.lower()[:6]:
                if len(IDs)>0:
                    await PROB()
                else:
                    await message.reply('No players in the game')
            
            
            if 'bbtime' in message.content.lower()[:6] and (message.author.id in Trusted_IDs or message.author.id in Temp_Trusted):
                try:
                    if len(IDs)>0:
                        message_list = [f'OH SHIT! %s just got randomly dinked by {client.user.name}!!'
                                        ,f'{client.user.name} flipped a %i sided coin, and %s lost, time to DINK ONE MOAR!' % (len(IDs),'%s')
                                        ,f"Is it raining cows today? {client.user.name} checked, and the answer was no.. %s has to dink one more!"
                                        ,f"Our good bot {client.user.name} ran out of good ways to be random, so %s should dink ONE MOAR!!"
                                        ,'Its fucking dinking time, so %s should dink one MOAR!'
                                        ,f'{client.user.name}: We live to party, we drink to party, %s dink one MOAR!'
                                        ,'Alcohol might not solve your problems, but neither will milk or water, %s DINK ONE MOAR!'
                                        ]
                        p_message_list = np.array([10]*len(message_list))
                        p_message_list[0] = 1
                        p_message_list[0] = 3
                        string = message.content.lower()[7:]
                        N = int(string[:string.find(',')])
                        T = int(string[string.find(',')+1:])
                        for i in range(N):
                            await asyncio.sleep(np.random.randint(60)+T*60)
                            dinkee = Random(IDs,points)
                            Update(dinkee[0],dinkee,True)
                            ID_Tracker(dinkee, 2)
                            i_ID = [i for i in range(len(IDs)) if IDs[i] == dinkee[0]][0]
                            embed = discord.Embed(title=r'%s just got randomly dinked!'%Nicks[i_ID])
                            embed.add_field(name='Counter',value='Dinks performed: \n Dinks recieved: \n Dink probability:')
                            embed.add_field(name='Value',value=liner(['%i'%Totaldink[i_ID],'%i'%TotalHandouts[i_ID],'%.3g%%'%(100*points[i_ID]/np.sum(points))] ))
                            embed.set_thumbnail(url=Link_selector(drunk_gif_list))
                            message_paste = np.random.choice(message_list,p=np.asarray(p_message_list)/np.sum(p_message_list))
                            await message.channel.send(message_paste % ("<@%i>" % (dinkee[0])),embed=embed)
                except:
                    await message.channel.send('No players in the game')
                    
                    
    
            if 'opt in' == message.content.lower() or 'bbopt in' == message.content.lower():
                if message.author.id not in IDs:
                    IDs.append(message.author.id)
                    points.append(5)
                    Totaldink.append(0)
                    TotalHandouts.append(0)
                    await Tally(f'Welcome {message.author.mention}! Happy DINKING! <3')
                else:
                    await message.channel.send(f'{message.author.mention}, you are already in the game!')
            if 'opt out' == message.content.lower() or 'bbopt out' == message.content.lower():
                if message.author.id in IDs:
                    Delete(message.author.id)
                    if len(IDs)>0:
                        print(points,np.mean(points))
                    await message.channel.send(f'Sad to see you go {message.author.mention}! :(')
                else:
                    await message.channel.send(f'{message.author.mention}, you are not currently in the game!')
            if 'opt out' in message.content.lower()[:7] and message.author.id in Trusted_IDs and len(message.mentions)>0:
                in_list = [s.id for s in message.mentions if s.id in IDs]
                #out_list = [s.id for s in message.mentions if s.id not in IDs]
                for ID in in_list:
                    Delete(ID)
                    
                print(points,np.mean(points))
                if len(in_list) == 1:
                    string = "<@%i>" % (in_list[0])
                else:
                    names = ["<@%i>" % i for i in in_list]
                    string = list_creator(names)
                    
                await Tally('Sad to see %s go, come back soon x. 😔'% string )

            if 'opt in' == message.content.lower()[:6] and message.author.id in Trusted_IDs and len(message.mentions)>0:
                mentions_list = [s.id for s in message.mentions if s.id not in IDs]
                new_names = []
                for i,Id in enumerate(mentions_list):
                    IDs.append(Id)
                    points.append(5)
                    Totaldink.append(0)
                    TotalHandouts.append(0)
                    username = await client.fetch_user(Id)
                    new_names.append(str(username)[:-5])
                    
                if len(mentions_list) == 1:
                    string = new_names[0]
                else:
                    names = new_names
                    string = list_creator(names)
                await Tally('Everyone welcome %s to the game! Happy dinking x'%string)
            
            
            
            
            if 'bbvillain' == message.content.lower() and (message.author.id in Trusted_IDs or message.author.id in Temp_Trusted or message.author.id in bbvillain_IDs):
                TimeSetting = 30 #in minutes
                if len(IDs) > 0:
                    if len(IDs) > 0 and (time.time()-T0[-1]) > 60*TimeSetting and message.author.id in IDs:
                        string = '**OH SHIT!** Villain spotted, **group dink**!!! \n' + list_creator( (["<@%i>" % i for i in IDs]) )
                        T0.append(time.time())
                        for i in range(len(IDs)):
                            TotalHandouts[i] += 1
                            ID_Tracker(IDs[i], 2)
                        await message.channel.send(string,file=discord.File('./images/dink.mp4'))
                    elif len(IDs) > 0 and (time.time()-T0[-1]) <= 60*TimeSetting and message.author.id in IDs:
                        cooldown = int(np.floor( TimeSetting - (time.time()-T0[-1])/60  ))
                        await message.channel.send('Villain is not ready for another group dink, wait at least %i min'%cooldown)
                    else:
                        await message.channel.send(f'{message.author.mention} you are not allowed to summon the allmighty Villain without being in the game yourself')
                else:
                    await message.channel.send('No players in the game')
            if 'bbvillain' == message.content.lower()[:9] and message.author.id in bbvillain_IDs:
                if len(message.mentions)>0:
                    mentions_list = [s.id for s in message.mentions if s.id not in bbvillain_IDs]
                    for ID in mentions_list:
                        bbvillain_IDs.append(ID)
                    await message.reply('%i player%s %s added, they can now use bbvillain' % (len(mentions_list), 's' if len(mentions_list)>1 else '' , 'were' if len(mentions_list)>1 else 'was' ))
        
            if 'coinflip' == message.content.lower():
                T_coin_cooldown = 5*60
                if message.author.id in IDs:
                    if countdown_timer(message.author.id,'coinflip',cooldown=T_coin_cooldown):
                        msg = await message.reply('I flipped a coin, guess correctly and recieve nothing, guess wrong and dink')
                        valid_reactions = ['🍸','🍺']#['👍','👎']
                        for s in valid_reactions:
                            await msg.add_reaction(s)

                        def check(reaction, user):
                            return user == message.author and str(reaction.emoji) in valid_reactions
                        try:
                            reaction, user = await client.wait_for('reaction_add', timeout=10.0, check=check)
                            if str(reaction.emoji) in valid_reactions:
                                if str(reaction.emoji) == np.random.choice(valid_reactions):
                                    await message.reply('You guessed right! No dinking for now')
                                else:
                                    await message.reply('Wrong')
                                    dinkee = [message.author.id]
                                    Update(dinkee[0],dinkee,True)
                                    ID_Tracker(dinkee[0], 2)
                                    i_ID = [i for i in range(len(IDs)) if IDs[i] == dinkee[0]][0]
                                    embed = discord.Embed(title=r"%s's looser stats"%Nicks[i_ID])
                                    embed.add_field(name='Counter',value='Dinks performed: \n Dinks recieved: \n Dink probability:')
                                    embed.add_field(name='Value',value=liner(['%i'%Totaldink[i_ID],'%i'%TotalHandouts[i_ID],'%.3g%%'%(100*points[i_ID]/np.sum(points))] ))
                                    embed.set_thumbnail(url=Link_selector(drunk_gif_list))
                                    await message.channel.send(f'{message.author.mention} just dinked themselves by guessing wrong!! DINK MOAR',embed=embed)
                                await msg.delete()
                                    
                        except:
                            await msg.delete()
                            await message.reply('You did not react in time')
                    else:
                        t_left = countdown_timer_left(message.author.id,'coinflip',T_coin_cooldown)
                        await message.reply('This command has a %i minute cooldown per user. (%i min left)' % (T_coin_cooldown/60,t_left) )
                else:
                    await message.reply('You have to be in the game to flip coins')
                
                        
        
        
        elif check_command() or 'opt in' == message.content.lower() or 'opt out' == message.content.lower():
            if time.time()-T_dink[-1]>5*30:
                T_dink.append(time.time())
                await message.channel.send('Villain does not dink during weekdays \n'+'Come back in %i Hours (4pm Friday)'%(time_till_dink())
                                           ,file = discord.File('./images/sadain.PNG')
                                           )



token = open("token.txt", "r").read()
client.run(token)








