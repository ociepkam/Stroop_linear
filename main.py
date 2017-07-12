#!/usr/bin/env python
# -*- coding: latin-1 -*-
import atexit
import codecs
import csv
from os.path import join
import yaml
from psychopy import visual, event, logging, gui, core
from misc.screen_misc import get_screen_res
from prepare_exp import prepare_exp
import time
import numpy
import random

# Incongruent_x_y:
# x - possible reactions
# y - conflict reactions


class TriggersNeutral(object):
    ProblemAppear = 1
    ParticipantReact = 7


class TriggersCongruent(object):
    ProblemAppear = 2
    ParticipantReact = 7


class TriggersIncongruent11(object):
    ProblemAppear = 3
    ParticipantReact = 7


class TriggersIncongruent22(object):
    ProblemAppear = 4
    ParticipantReact = 7


class TriggersIncongruent12(object):
    ProblemAppear = 5
    ParticipantReact = 7


class TriggersIncongruent21(object):
    ProblemAppear = 6
    ParticipantReact = 7


# GLOBALS
TEXT_SIZE = 40
TEXT_COLOR = '#f2f2f2'
VISUAL_OFFSET = 50
FIGURES_SCALE = 0.4
RESULTS = [['EXP', 'TRIAL_TYPE', 'TEXT', 'COLOR', 'WAIT', 'RESPTIME', 'RT', 'TRUE_KEY', 'ANSWER', 'CORR']]
POSSIBLE_KEYS = ['z', 'x', 'c', 'b', 'n', 'm']
# TRIGGER_LIST = []


@atexit.register
def save_beh_results():
    with open(join('results', PART_ID + '_beh.csv'), 'wb') as beh_file:
        beh_writer = csv.writer(beh_file)
        beh_writer.writerows(RESULTS)
    logging.flush()
    # with open(join('results', PART_ID + '_triggermap.txt'), 'w') as trigger_file:
    #     trigger_writer = csv.writer(trigger_file)
    #     trigger_writer.writerows(TRIGGER_LIST)


def read_text_from_file(file_name, insert=''):
    """
    Method that read message from text file, and optionally add some
    dynamically generated info.
    :param file_name: Name of file to read
    :param insert:
    :return: message
    """
    if not isinstance(file_name, str):
        logging.error('Problem with file reading, filename must be a string')
        raise TypeError('file_name must be a string')
    msg = list()
    with codecs.open(file_name, encoding='utf-8', mode='r') as data_file:
        for line in data_file:
            if not line.startswith('#'):  # if not commented line
                if line.startswith('<--insert-->'):
                    if insert:
                        msg.append(insert)
                else:
                    msg.append(line)
    return ''.join(msg)


def check_exit(key='f7'):
    stop = event.getKeys(keyList=[key])
    if len(stop) > 0:
        logging.critical('Experiment finished by user! {} pressed.'.format(key))
        exit(1)


def show_info(win, file_name, insert=''):
    """
    Clear way to show info message into screen.
    :param win:
    :return:
    """
    msg = read_text_from_file(file_name, insert=insert)
    msg = visual.TextStim(win, color=TEXT_COLOR, text=msg, height=TEXT_SIZE - 20, wrapWidth=SCREEN_RES['width'])
    msg.draw()
    win.flip()
    key = event.waitKeys(keyList=['f7', 'return', 'space'])
    if key == ['f7']:
        abort_with_error('Experiment finished by user on info screen! F7 pressed.')
    win.flip()


def show_info_2(win, info, show_time):
    info.setAutoDraw(True)
    win.flip()
    time.sleep(show_time)
    info.setAutoDraw(False)
    check_exit()
    win.flip()


def prepare_key_matching_text(colors_text_to_keys_dict):
    text = ""
    for color, keys in colors_text_to_keys_dict.iteritems():
        if len(keys) == 1:
            text += "klawisz {} gdy wyswietlono napis w kolorze {}\n".format(keys[0].upper(), color)
        elif len(keys) == 2:
            text += "klawisz {} lub {} gdy wyswietlono napis w kolorze {}\n".format(keys[0].upper(), keys[1].upper(), color)
        else:
            raise Exception('Wrong number of keys for good reactions')
    return text


def feedb(ans, true_keys):
    if data['Feedb']:
        if ans == '-':
            feedb_msg = no_feedb
        elif ans in true_keys:
            feedb_msg = pos_feedb
        elif ans not in true_keys:
            feedb_msg = neg_feedb
        else:
            raise Exception("Wrong feedb")

        show_info_2(win=win, info=feedb_msg, show_time=data['Feedb_time'])


def prepare_trial_info(trial):
    true_keys = trial['good_keys']
    reaction_time = -1
    if trial['trial_type'] == 'congruent':
        triggers = TriggersCongruent
    elif trial['trial_type'] == 'incongruent_1_1':
        triggers = TriggersIncongruent11
    elif trial['trial_type'] == 'incongruent_2_2':
        triggers = TriggersIncongruent22
    elif trial['trial_type'] == 'inicongruent_1_2':
        triggers = TriggersIncongruent12
    elif trial['trial_type'] == 'incongruent_2_1':
        triggers = TriggersIncongruent21
    else:
        triggers = TriggersNeutral
    return true_keys, reaction_time, triggers


def abort_with_error(err):
    logging.critical(err)
    raise Exception(err)


# exp info
data = yaml.load(open('config.yaml', 'r'))

# prepare nirs
if data['NIRS']:
    import pyxid

    devices = pyxid.get_xid_devices()

    # check NIRS
    if not devices:
        abort_with_error('NIRS not detected!')
    else:
        NIRS = devices[0]

# part info
info = {'Part_id': '', 'Part_age': '20', 'Part_sex': ['MALE', "FEMALE"],
        'ExpDate': data['Data'], '_Observer': data['Observer']}
dictDlg = gui.DlgFromDict(dictionary=info, title='Stroop')  # , fixed=['ExpDate']
if not dictDlg.OK:
    exit(1)
PART_ID = str(info['Part_id'] + info['Part_sex'] + info['Part_age'])

logging.LogFile('results/' + PART_ID + '.log', level=logging.INFO)
logging.info(info)

# prepare screen
SCREEN_RES = get_screen_res()
win = visual.Window(SCREEN_RES.values(), fullscr=True, monitor='testMonitor', units='pix', screen=0, color='#262626')
mouse = event.Mouse(visible=False)
fixation = visual.TextStim(win, color=TEXT_COLOR, text='+', height=2 * TEXT_SIZE)

# prepare feedb
pos_feedb = visual.TextStim(win, text=u'Poprawna odpowied\u017A', color=TEXT_COLOR, height=TEXT_SIZE)
neg_feedb = visual.TextStim(win, text=u'Odpowied\u017A niepoprawna', color=TEXT_COLOR, height=TEXT_SIZE)
no_feedb = visual.TextStim(win, text=u'Nie udzieli\u0142e\u015B odpowiedzi', color=TEXT_COLOR, height=TEXT_SIZE)

# prepare trials
training_trials, experiment_trials, colors_text_to_keys_dict, colors_text_to_show = prepare_exp(data, win, TEXT_SIZE, POSSIBLE_KEYS)
blocks = numpy.array_split(experiment_trials, data['Number_of_blocks'])

keys_mapping_text = prepare_key_matching_text(colors_text_to_keys_dict)

key_labes = visual.TextStim(win=win, text='{0}  {1}  {2}  {3}  {4}  {5}'.format(*colors_text_to_show), color=TEXT_COLOR,
                            wrapWidth=SCREEN_RES['width'],  height=TEXT_SIZE, pos=(0, -7 * VISUAL_OFFSET))

resp_clock = core.Clock()


# ----------------------- Start Stroop ----------------------- #

for idx, block in enumerate(training_trials):
    show_info(win, join('.', 'messages', 'training{}.txt'.format(idx+1)), insert=keys_mapping_text)
    for trial in block:
        # prepare trial
        true_keys, reaction_time, triggers = prepare_trial_info(trial)

        # show fix
        show_info_2(win=win, info=fixation, show_time=data['Fix_time'])
        check_exit()

        # show problem
        event.clearEvents()
        win.callOnFlip(resp_clock.reset)
        trial['stim'].setAutoDraw(True)
        key_labes.setAutoDraw(True)
        win.flip()

        while resp_clock.getTime() < data['Training_Resp_time']:
            key = event.getKeys(keyList=POSSIBLE_KEYS)
            if key:
                reaction_time = resp_clock.getTime()
                break
            check_exit()
            win.flip()

        trial['stim'].setAutoDraw(False)
        key_labes.setAutoDraw(False)
        win.flip()

        if key:
            ans = key[0]
        else:
            ans = '-'
        RESULTS.append(
            ['training', trial['trial_type'], trial['text'], trial['color'], data['Training_Wait_time'],
             data['Training_Resp_time'], reaction_time, true_keys, ans, ans in true_keys])
        check_exit()

        # show feedb
        if data['Feedb']:
            feedb(ans, true_keys)
            check_exit()

        # wait
        time.sleep(data['Training_Wait_time'])
        check_exit()

# ----------- Start experiment ------------- #

show_info(win, join('.', 'messages', 'instruction.txt'), insert=keys_mapping_text)

for idx, block in enumerate(blocks):
    for trial in block:
        # prepare trial
        true_keys, reaction_time, triggers = prepare_trial_info(trial)
        jitter = random.random() * data['Jitter']

        # show fix
        show_info_2(win=win, info=fixation, show_time=data['Fix_time'])
        check_exit()

        # show problem
        event.clearEvents()
        win.callOnFlip(resp_clock.reset)
        trial['stim'].setAutoDraw(True)
        key_labes.setAutoDraw(True)
        win.flip()
        if data['NIRS']:
            NIRS.activate_line(triggers.ProblemAppear)

        while resp_clock.getTime() < data['Experiment_Resp_time']:
            key = event.getKeys(keyList=POSSIBLE_KEYS)
            if key:
                reaction_time = resp_clock.getTime()
                if data['NIRS']:
                    NIRS.activate_line(triggers.ParticipantReact)
                break
            check_exit()
            win.flip()

        trial['stim'].setAutoDraw(False)
        key_labes.setAutoDraw(False)
        win.flip()

        if key:
            ans = key[0]
        else:
            ans = '-'

        RESULTS.append(
            ['experiment', trial['trial_type'], trial['text'], trial['color'], data['Experiment_Wait_time']+jitter,
             data['Experiment_Resp_time'], reaction_time, true_keys, ans, ans in true_keys])
        check_exit()

        # wait
        time.sleep(data['Experiment_Wait_time'])
        check_exit()

        # jitter
        time.sleep(jitter)
        check_exit()

    if idx+1 < len(blocks):
        show_info(win, join('.', 'messages', 'break{}.txt'.format(idx+1)))

show_info(win, join('.', 'messages', 'end.txt'))
