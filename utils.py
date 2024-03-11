from ipywidgets import (
    Button,
    HTML,
    HBox,
    VBox,
    ToggleButtons
)
import os
from ipywidgets import Button, HTML, HBox
from IPython.display import display
import random
import pickle
import time
import pandas as pd


def load_samples(data_path):
    path_samples = data_path
    assert os.path.exists(path_samples), f"{path_samples} does not exist"
    samples = pd.read_csv(path_samples, header=0)
    return samples.to_dict("records")


def save_annotations(path, annots, verbose=False):
    with open(path, "wb") as file:
        pickle.dump(annots, file)
    if verbose:
        print(f"{len(annots)} annotation saved to {path}")


def load_annotations(save_path, examples):
    if os.path.isfile(save_path):
        with open(save_path, "rb") as file:
            loaded_annotations = pickle.load(file)
        annotated = [annot["talkid"] for annot in loaded_annotations['annots']]
        examples_out = [example for example in examples if example['talkid'] not in annotated]
        return loaded_annotations, examples_out
    else:
        return {"demographics": {}, "annots": []}, examples
    
def export_csv(annotations_path, save_path):
    if os.path.exists(annotations_path):
        with open(annotations_path, "rb") as file:
            loaded_annotations = pickle.load(file)
        exporting = []
        for annot in loaded_annotations['annots']:
            example = {
                "gender": annot['gender'],
                "comment": annot['comment'],
                "talkid": annot['talkid'],
                "videourl": annot['videourl']
            }
            if "annotation" in annot:
                annotations = annot['annotation']
                example.update(annotations)
            exporting.append(example)
        pd.DataFrame(exporting).to_csv(save_path, index=None)
    else:
        raise FileExistsError("Annotations file does not exists")


def display_buttons(btns, num_buttons_in_a_row=3):
    if len(btns) > num_buttons_in_a_row:
        box = VBox([HBox(btns[x:x + num_buttons_in_a_row])
                    for x in range(0, len(btns), num_buttons_in_a_row)])
    else:
        box = HBox(btns)
    display(box)


def get_demographics():
    button_sets = {}        
    
    button_sets['gender'] = ToggleButtons(
        options=["Female", "Male"],
        description='You personally identify as:',
        disabled=False,
        value=None,
        button_style='',
    )
    
    button_sets['age'] = ToggleButtons(
        options=["0-15", "15-25", "25-35", "35+" ],
        description='Please select the correct age bracket:',
        disabled=False,
        value=None,
        button_style='',
    )
    for set, buttons in button_sets.items():
        display(buttons)
    return button_sets


def save_demographics(save_path, demographics, verbose=False):
    demographics = {name: buttons.value for name, buttons in demographics.items()}
    if os.path.isfile(save_path):
        with open(save_path, "rb") as file:
            loaded_annotations = pickle.load(file)
            loaded_annotations['demographics'] = demographics
    else:
        loaded_annotations = {"demographics": demographics, "annots": []}
    with open(save_path, "wb") as file:
        pickle.dump(loaded_annotations, file)
    if verbose:
        print(f"demographics saved to {save_path}")


def annotate(examples, 
             save_path,
             questions=[
                 {"name": 'Anger', 
                  "question": 'What are the sentiments expressed by this tweet? choose all that applies. \n  Do you detect anger ? ', 
                  "options": ["anger", "annoyance", "disapproval"]},
                 
                 {"name": 'Happiness', 
                  "question":' Do you detect happiness?', 
                  "options": ["joy", "pride", "relief", "gratitude", "love", "optimism", "amusement", "admiration", "approval", "excitement"]},
                 
                 {"name": 'Sadness',
                  "question": 'Do you detect sadness?',
                  "options": ["sadness", "grief", "remorse", "disappointment"]},
                 
                 {"name": 'fear', 
                  "question": 'Do you detect fear?', 
                  "options": ["fear", "nervousness"]},

                 {"name": 'surprise', 
                  "question": 'Do you detect surprise?', 
                  "options": ["surprise", "realization"]},

                 {"name": 'disgust', 
                  "question": 'Do you detect disgust?', 
                  "options": ["disgust"]},
                 
                 {"name": 'other', 
                  "question": 'Do you detect any of these feelings?', 
                  "options": ["confusion", "curiosity", "desire", "embarrassment", "caring"]},
                 {"name": 'references', 
                  "question": 'Which one of the following references do you recognize in this tweet?', 
                  "options": ["Literature", "Historical", "Baraye", "Pop-Culture", "Religion","Proverb"]}

                 
                 ], 
             shuffle=False, 
             final_process_fn=None):
    
    def render(index):
        nonlocal start_time
        set_label_text(index)
        
        if index >= len(examples):
            end_time = time.time()
            print(f'Annotation done. (took {end_time-start_time:.0f}s)')
            if final_process_fn is not None:
                final_process_fn(list(annotations.items()))
            for _, butn in responses.items():
                butn.disabled = True
            btn.disabled = True
            count_label.value = f'{len(annotations["annots"])} of {len(annotations["annots"])} Examples annotated, Current Position: {len(annotations["annots"])} '
            return
        
        comment = examples[index]["comment"]
        parsed = comment.replace("\n", "<br>")
        text = '<h4 class="text-center"><u>Consider the following internet video, and its corresponding response:</u></h4>'
        text += f'<div class="row"><p class="text-center" style="padding-left:10%;padding-right:10%;font-size:120%"><br>{parsed}<br></p>  </div>'
        sentence_html.value = text
        for set, buttons in responses.items():
            buttons.value = None
            
    def set_label_text(index):
        nonlocal count_label
        if len(annotations["annots"])==0:
            count_label.value = f'{len(annotations["annots"])} of {len(examples)} Examples annotated, Current Position: {index + 1}'
        else:
            nonlocal start_time
            time_took = time.time() - start_time
            count_label.value = f'{len(annotations["annots"])} of {len(examples)} Examples annotated, Current Position: {index + 1}, Took {time_took:.0f}s (Avg {time_took/len(annotations):.0f}s) '
            
    def next_example(btn=None):
        nonlocal current_index
        if current_index < len(examples):
            current_index += 1
            render(current_index)
    
    def add_annotation(annotation):
        if "annotation" in examples[current_index]:
            del examples[current_index]["annotation"]
        examples[current_index]["annotation"] = annotation
        annotations["annots"].append(examples[current_index])
        save_annotations(save_path, annotations)
        next_example()
        
    if shuffle:
        random.shuffle(examples)
    annotations, examples = load_annotations(save_path, examples)
    current_index = 0
    
    start_time = time.time()
    count_label = HTML()
    set_label_text(current_index)
    display(count_label)

    #### SHOWING MAIN PART
    sentence_html=HTML()
    display(sentence_html)
    responses = {
        el['name']: ToggleButtons(
            options=el['options'], 
            description=el['question'], 
            disabled=False, value=None, button_style='') for el in questions
    }        

    
    for set, buttons in responses.items():
        display(buttons)
    
    btn = Button(description='submit', button_style='info', icon='check')
    def on_click(btn):
        nonlocal current_index
        labels_on = {}
        for cat, buttons in responses.items():
            labels_on[cat] = buttons.value
            buttons.value = None
        add_annotation(labels_on)
        render(current_index)
        
    btn.on_click(on_click)
    display(btn)
    render(current_index)
    return
    
