NormBank: A Knowledge Bank of Situational Social Norms
=================================

This repository contains data and code for the paper **NormBank: A Knowledge Bank of Situational Social Norms** by [Caleb Ziems](https://calebziems.com/), [Jane Dwivedi-Yu](https://janedwivedi.github.io/), [Yi-Chia Wang](https://scholar.google.com/citations?user=9gMgFPQAAAAJ&hl=en), [Alon Y. Halevy](https://scholar.google.com/citations?user=F_MI0pcAAAAJ&hl=en), [Diyi Yang](https://cs.stanford.edu/~diyiy/)

[Paper](https://arxiv.org/pdf/2305.17008.pdf) | [Data](https://drive.google.com/drive/folders/1XRhrzgG_R0zypPgPlCxK0nlqKbfaI9xe?usp=drive_link)
[![CC BY-SA 4.0][cc-by-sa-shield]][cc-by-sa]
## *What is NormBank?* 
`NormBank` is a knowledge bank of 155k situational norms that we built to ground flexible normative reasoning for interactive, assistive, and collaborative AI systems. Unlike prior commonsense resources, `NormBank` grounds each inference within a multivalent sociocultural frame, which includes the setting (e.g., restaurant), the agents’ contingent roles (waiter, customer),
their attributes (age, gender), and other physical, social, and cultural constraints (e.g., the temperature or the country of operation). In total, `NormBank` contains 63k unique constraints from a taxonomy that we introduce and iteratively refine here. Constraints then apply in different combinations to frame social norms. Under these manipulations, norms are non-monotonic — one can cancel an inference by updating its frame even slightly.

## *Where can I download the data?*
Follow [this link](https://drive.google.com/drive/folders/1XRhrzgG_R0zypPgPlCxK0nlqKbfaI9xe?usp=drive_link) to download `NormBank.csv`

This work is licensed under a
[Creative Commons Attribution-ShareAlike 4.0 International License][cc-by-sa].

[cc-by-sa]: http://creativecommons.org/licenses/by-sa/4.0/
[cc-by-sa-image]: https://licensebuttons.net/l/by-sa/4.0/88x31.png
[cc-by-sa-shield]: https://img.shields.io/badge/License-CC%20BY--SA%204.0-lightgrey.svg

## Full Project Pipeline (annotation + experiments + analysis)

### 0. Project Environment
* CUDA, cudnn
* [anaconda](https://www.anaconda.com/products/individual)

1. Create main project environment
```bash
conda create --name normbank python=3.7
conda activate normbank
pip install -r normbank.txt
```

2. Add openai API key, replacing `API_KEY` with your key
```bash
touch resources/openai_api_key.txt
echo "API_KEY"|cat>resources/openai_api_key.txt
```

### 1. Build SCENE Taxonomy

#### 1.1 Attributes
> Attributes are drawn from the literature and so they are pre-populated in `data/raw/Attributes` in the repo

#### 1.2 Roles and Items
> To bypass this step, simply use the `data/raw/Settings-Roles` and `data/raw/Settings-Items` directories pre-populated in the repo

1. Pull roles for each setting ==> `data/raw/Settings-Roles`
```bash
cd src
python pull_roles_GPT.py
```

2. Use GPT-3 to pull items (social props) for each setting (+ role) ==> Output: `data/raw/Settings-Items` (+ `data/raw/Settings-Roles-Items`)
```bash
python pull_items_GPT.py
```

#### 1.3 Behaviors
> To bypass this step, simply use the `data/raw/Behaviors-All-Hand-Filtered` directory pre-populated in the repo

3. Use GPT-3 to pull behaviors conditioned on settings + role ==> Output: `data/raw/Settings-Behaviors_Normal`
```bash
python pull_behaviors_GPT.py
```

4. Use GPT-3 to pull behaviors conditioned on personal attributes ==> Output: `data/raw/Settings-Attributes-Behaviors_Taboo`
```bash
python pull_behaviors_attributes.py
```

5. Use regexes clean and merge all behaviors ==> Ouput: `data/raw/Behaviors-All-Merged`
```bash
python merge_behaviors.py
```

6. Manually filter behaviors ==> Output: `data/raw/Behaviors-All-Hand-Filtered

### 2. Build NormBank HIT input files and run HIT

> To bypass this step, download HIT output files from `output.zip` in the following Drive folder: https://drive.google.com/drive/folders/1XRhrzgG_R0zypPgPlCxK0nlqKbfaI9xe?usp=sharing

1. Build HIT input files ==> Output: `hit/temp/subsample.csv'
```bash
python behaviors_to_hit.py
```

2. Build HIT qual on MTurk (after you modify the python code with the proper API keys) (`cd ../hit/qual`)
```bash
python qual_request.py
```

3. Set up and run HIT on MTurk using `HIT_Conditional_Norms.html` ==> Output: `hit/output`


### 3. Build SCENE

1. Build SCENE training CSV file
```bash
python build_gen_train_file.py
```

2. Compute SCENE statistics with `dataset-statistics.ipynb`


