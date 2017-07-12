import random
from psychopy import visual


stim_text = {'CZERWONY': 'red', 'NIEBIESKI': '#5e75d9', 'BRAZOWY': '#574400', 'ZIELONY': 'green'}  # text: color
stim_neutral = "HHHHH"
colors_text = stim_text.keys()
random.shuffle(colors_text)
colors_names = [stim_text[color] for color in colors_text]
left_hand = colors_text[:3]
right_hand = colors_text[3:]


def prepare_trial(trial_type, win, text_size):
    if trial_type == 'congruent':
        text = random.choice(stim_text.keys())
        color = stim_text[text]
    elif trial_type == 'incongruent':
        text = random.choice(stim_text.keys())
        if text in left_hand:
            possible_colors = [stim_text[key] for key in right_hand]
        else:
            possible_colors = [stim_text[key] for key in left_hand]
        color = random.choice(possible_colors)
    elif trial_type == 'neutral':
        text = stim_neutral
        color = random.choice(stim_text.values())
    else:
        raise Exception('Wrong trigger type')

    stim = visual.TextStim(win, color=color, text=text, height=2*text_size)
    return {'trial_type': trial_type, 'text': text, 'color': color, 'stim': stim}


def prepare_part(trials_congruent, trials_incongruent_1_1, trials_incongruent_2_2, trials_incongruent_1_2,
                 trials_incongruent_2_1, trials_neutral, win, text_size):
    trials = ['congruent'] * trials_congruent + \
             ['incongruent_1_1'] * trials_incongruent_1_1 + \
             ['incongruent_2_2'] * trials_incongruent_2_2 + \
             ['incongruent_1_2'] * trials_incongruent_1_2 + \
             ['incongruent_2_1'] * trials_incongruent_2_1 + \
             ['neutral'] * trials_neutral
    random.shuffle(trials)
    return [prepare_trial(trial_type, win, text_size) for trial_type in trials]


def prepare_exp(data, win, text_size, keys):
    training1_trials = prepare_part(data['Training1_trials_congruent'], data['Training1_trials_incongruent_1_1'],
                                    data['Training1_trials_incongruent_2_2'], data['Training1_trials_incongruent_1_2'],
                                    data['Training1_trials_incongruent_2_1'], data['Training1_trials_neutral'], win,
                                    text_size)

    training2_trials = prepare_part(data['Training2_trials_congruent'], data['Training2_trials_incongruent_1_1'],
                                    data['Training2_trials_incongruent_2_2'], data['Training2_trials_incongruent_1_2'],
                                    data['Training2_trials_incongruent_2_1'], data['Training2_trials_neutral'], win,
                                    text_size)
    experiment_trials = prepare_part(data['Experiment_trials_congruent'], data['Experiment_trials_incongruent_1_1'],
                                     data['Experiment_trials_incongruent_2_2'], data['Experiment_trials_incongruent_1_2'],
                                     data['Experiment_trials_incongruent_2_1'], data['Experiment_trials_neutral'], win,
                                     text_size)

    return [training1_trials, training2_trials], experiment_trials, colors_text, colors_names
