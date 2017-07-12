import random
from psychopy import visual


stim_text = {'CZERWONY': 'red', 'NIEBIESKI': '#5e75d9', 'BRAZOWY': '#574400', 'ZIELONY': 'green'}  # text: color
stim_neutral = "HHHHH"
colors_text = stim_text.keys()
random.shuffle(colors_text)
colors_names = [stim_text[color] for color in colors_text]
left_hand = colors_text[:2]
right_hand = colors_text[2:]


def prepare_trial(trial_type, win, text_size, colors_text_to_keys_dict):
    if trial_type == 'congruent':
        text = random.choice(stim_text.keys())
        color_name = text
        color = stim_text[text]

    elif trial_type == 'incongruent_1_1':
        possible_text = [color_text for color_text, keys in colors_text_to_keys_dict.iteritems() if len(keys) == 1]
        text = random.choice(possible_text)
        possible_text.remove(text)
        color_name = possible_text[0]
        color = stim_text[color_name]

    elif trial_type == 'incongruent_2_2':
        possible_text = [color_text for color_text, keys in colors_text_to_keys_dict.iteritems() if len(keys) == 2]
        text = random.choice(possible_text)
        possible_text.remove(text)
        color_name = possible_text[0]
        color = stim_text[color_name]

    elif trial_type == 'incongruent_1_2':
        possible_text = [color_text for color_text, keys in colors_text_to_keys_dict.iteritems() if len(keys) == 1]
        text = random.choice(possible_text)
        possible_colors = [color_text for color_text, keys in colors_text_to_keys_dict.iteritems() if len(keys) == 2]
        if text in left_hand:
            color_name = [col for col in possible_colors if col in right_hand][0]
        elif text in right_hand:
            color_name = [col for col in possible_colors if col in left_hand][0]
        else:
            raise Exception('Wrong trigger color')
        color = stim_text[color_name]

    elif trial_type == 'incongruent_2_1':
        possible_text = [color_text for color_text, keys in colors_text_to_keys_dict.iteritems() if len(keys) == 2]
        text = random.choice(possible_text)
        possible_colors = [color_text for color_text, keys in colors_text_to_keys_dict.iteritems() if len(keys) == 1]
        if text in left_hand:
            color_name = [col for col in possible_colors if col in right_hand][0]
        elif text in right_hand:
            color_name = [col for col in possible_colors if col in left_hand][0]
        else:
            raise Exception('Wrong trigger color')
        color = stim_text[color_name]

    elif trial_type == 'neutral':
        text = stim_neutral
        color = random.choice(stim_text.values())
        color_name = stim_text.keys()[stim_text.values().index(color)]

    else:
        raise Exception('Wrong trigger type')

    stim = visual.TextStim(win, color=color, text=text, height=2*text_size)
    good_keys = colors_text_to_keys_dict[color_name]
    return {'trial_type': trial_type,
            'text': text,
            'color': color,
            'stim': stim,
            'good_keys': good_keys}


def prepare_part(trials_congruent, trials_incongruent_1_1, trials_incongruent_2_2, trials_incongruent_1_2,
                 trials_incongruent_2_1, trials_neutral, win, text_size, keys_to_color_text_dict):
    trials = ['congruent'] * trials_congruent + \
             ['incongruent_1_1'] * trials_incongruent_1_1 + \
             ['incongruent_2_2'] * trials_incongruent_2_2 + \
             ['incongruent_1_2'] * trials_incongruent_1_2 + \
             ['incongruent_2_1'] * trials_incongruent_2_1 + \
             ['neutral'] * trials_neutral
    random.shuffle(trials)
    return [prepare_trial(trial_type, win, text_size, keys_to_color_text_dict) for trial_type in trials]


def prepare_exp(data, win, text_size, keys):
    left_random = [1, 2]
    random.shuffle(left_random)
    right_random = [1, 2]
    random.shuffle(right_random)
    all_random = left_random + right_random
    colors_text_to_show = [[col] * num for col, num in zip(colors_text, all_random)]
    # flatten array
    colors_text_to_show = [item for sublist in colors_text_to_show for item in sublist]

    # keys mapping
    colors_text_to_keys_dict = {col: [] for col in colors_text}
    for col, key in zip(colors_text_to_show, keys):
        colors_text_to_keys_dict[col].append(key)

    training1_trials = prepare_part(data['Training1_trials_congruent'], data['Training1_trials_incongruent_1_1'],
                                    data['Training1_trials_incongruent_2_2'], data['Training1_trials_incongruent_1_2'],
                                    data['Training1_trials_incongruent_2_1'], data['Training1_trials_neutral'], win,
                                    text_size, colors_text_to_keys_dict)

    training2_trials = prepare_part(data['Training2_trials_congruent'], data['Training2_trials_incongruent_1_1'],
                                    data['Training2_trials_incongruent_2_2'], data['Training2_trials_incongruent_1_2'],
                                    data['Training2_trials_incongruent_2_1'], data['Training2_trials_neutral'], win,
                                    text_size, colors_text_to_keys_dict)
    experiment_trials = prepare_part(data['Experiment_trials_congruent'], data['Experiment_trials_incongruent_1_1'],
                                     data['Experiment_trials_incongruent_2_2'], data['Experiment_trials_incongruent_1_2'],
                                     data['Experiment_trials_incongruent_2_1'], data['Experiment_trials_neutral'], win,
                                     text_size, colors_text_to_keys_dict)

    return [training1_trials, training2_trials], experiment_trials, colors_text_to_keys_dict, colors_text_to_show
