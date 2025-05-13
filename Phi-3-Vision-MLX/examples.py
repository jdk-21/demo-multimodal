# This file was originally authored by GitHub user @couillonnade (PR #2)

import phi_3_vision_mlx as pv

# Decoding Strategies

## Code Generation
prompt = "Write a Python function to calculate the Fibonacci sequence up to a given number n."
constr = [(100, "\n```python\n"), (100, " return "), (200, "\n```")]

### Constrained Decoding
pv.constrain(prompt, constr, use_beam=False)

### Constrained Beam Search Decoding
pv.constrain(prompt, constr, use_beam=True)

## Multiple Choice Question Answering
prompts = [
    "A 20-year-old woman presents with menorrhagia for the past several years. She says that her menses “have always been heavy”, and she has experienced easy bruising for as long as she can remember. Family history is significant for her mother, who had similar problems with bruising easily. The patient's vital signs include: heart rate 98/min, respiratory rate 14/min, temperature 36.1°C (96.9°F), and blood pressure 110/87 mm Hg. Physical examination is unremarkable. Laboratory tests show the following: platelet count 200,000/mm3, PT 12 seconds, and PTT 43 seconds. Which of the following is the most likely cause of this patient’s symptoms? A: Factor V Leiden B: Hemophilia A C: Lupus anticoagulant D: Protein C deficiency E: Von Willebrand disease",
    "A 25-year-old primigravida presents to her physician for a routine prenatal visit. She is at 34 weeks gestation, as confirmed by an ultrasound examination. She has no complaints, but notes that the new shoes she bought 2 weeks ago do not fit anymore. The course of her pregnancy has been uneventful and she has been compliant with the recommended prenatal care. Her medical history is unremarkable. She has a 15-pound weight gain since the last visit 3 weeks ago. Her vital signs are as follows: blood pressure, 148/90 mm Hg; heart rate, 88/min; respiratory rate, 16/min; and temperature, 36.6℃ (97.9℉). The blood pressure on repeat assessment 4 hours later is 151/90 mm Hg. The fetal heart rate is 151/min. The physical examination is significant for 2+ pitting edema of the lower extremity. Which of the following tests o should confirm the probable condition of this patient? A: Bilirubin assessment B: Coagulation studies C: Hematocrit assessment D: Leukocyte count with differential E: 24-hour urine protein"
]
constrs = [(0, '\nThe'), (100, ' The correct answer is'), (1, 'X.')]

### Constrained Beam Search Decoding
pv.constrain(prompts, constrs, blind_model=True, quantize_model=True, use_beam=True)

### Choosing from Options
pv.choose(prompts, choices='ABCDE')

# LoRA

## Train
pv.train_lora(
    lora_layers=5,  # Number of layers to apply LoRA
    lora_rank=16,   # Rank of the LoRA adaptation
    epochs=10,      # Number of training epochs
    lr=1e-4,        # Learning rate
    warmup=0.5,     # Fraction of steps for learning rate warmup
    dataset_path="JosefAlbers/akemiH_MedQA_Reason"
)

## Test
test_lora(adapter_path=None)                         # Without LoRA adapter
test_lora(adapter_path=True)                         # With default LoRA adapter
test_lora(adapter_path="adapters/phi3_mini_128k_Q")  # With specific adapter

# Agent

## Multi-turn VQA
agent = pv.Agent()
agent('What is shown in this image?', 'https://collectionapi.metmuseum.org/api/collection/v1/iiif/344291/725918/main-image')
agent('What is the location?')
agent.end()

## Generative Feedback Loop
agent('Plot a Lissajous Curve.')
agent('Modify the code to plot 3:4 frequency')
agent.end()

## API Tool Use
agent('Draw "A perfectly red apple, 32k HDR, studio lighting"')
agent.end()
agent('Speak "People say nothing is impossible, but I do nothing every day."')
agent.end()

# Toolchain

## LLM Backend Hotswap
agent = pv.Agent(toolchain = "responses, history = mistral_api(prompt, history)")
agent('Write a neurology ICU admission note')
agent('Give me the inpatient BP goal for this patient.')
agent('DVT ppx for this pt?')
agent("The patient's prognosis?")
agent.end()

# Misc

## ICL
pv.add_text('How to inspect API endpoints? @https://raw.githubusercontent.com/gradio-app/gradio/main/guides/08_gradio-clients-and-lite/01_getting-started-with-the-python-client.md')

## RAG
pv.rag('Comparison of Sortino Ratio for Bitcoin and Ethereum.')

## Multimodal Reddit Thread Summarizer
try:
    from rd2md import rd2md
    from pathlib import Path
    import json
    filename, contents, images = rd2md()
    prompt = 'Write an executive summary of above (max 200 words). The article should capture the diverse range of opinions and key points discussed in the thread, presenting a balanced view of the topic without quoting specific users or comments directly. Focus on organizing the information cohesively, highlighting major arguments, counterarguments, and any emerging consensus or unresolved issues within the community.'
    prompts = [f'{s}\n\n{prompt}' for s in contents]
    results = [pv.generate(prompts[i], images[i], max_tokens=512, blind_model=False, quantize_model=True, quantize_cache=False, verbose=False) for i in range(len(prompts))]
    with open(Path(filename).with_suffix('.json'), 'w') as f:
        json.dump({'prompts':prompts, 'images':images, 'results':results}, f, indent=4)
except Exception:
    print("This example requires the 'rd-to-md' package (https://github.com/JosefAlbers/rd2md). Install it with: pip install rd-to-md")

# Benchmark
pv.benchmark()
