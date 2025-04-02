# 02_Transliteration

# Japanese Transliteration Datacard

## Dataset Description
### Dataset Summary
The Japanese Transliteration dataset is a collection of transliterated pairs from cataloging records dated __ to __. The Japanese script includes Hiragana, Katakana and Kanji. This dataset is designed for training and evaluating Maching Learning models in the task of transliteration between Japanese script and the Roman alphabet.

### Supported Tasks

### Languages 
The dataset contains both English and Japanese (written in Hiragana, Katakana, Kanji and Roman alphabet).

## Dataset Structure
The dataset is in the form of a dataframe where each row contains a transliteration pair along with the identifier (LCCN) for the record in which it orinates as well as the MARC field and subfield values.

### Data Instances
An example of the dataframe is as follows:

| lccn     | field | subfield | original_script               | transliterated_text                        | 
| :---:    | :---: | :---:    | :---:                         | :---:                                      | 
| 98840563 | 245   | a        |`「飮用井戶使用実態調查」 報告書 /` | `"Inʾyō ido shiyō jittai chōsa" hōkokusho /` |
| 98840563 | 245   | c        |`[編集東京都衛生局生活環境部環境指導課]`.| `\[henshū Tōkyō-to Eiseikyoku Seikatsu Kankyōbu ...`|
| 86129343 | 710   | a        |`労働福祉事業団 (Japan)`.| `Rōdō Fukushi Jigyōdan (Japan)`|
| 86129343 | 100   | a        |`山崎正一,`.| `Yamazaki, Masakazu,`|
| 86129343 | 245   | a        |`山崎正一全集.`.| `Yamazaki Masakazu zenshū.`|

### Data Fields
| Field               | Description |
|:---:                |:---:                              |
| lccn                | String or integer indicating the LCCN of the record |
| field               | String or integer indicating the MARC field that the transliteration pair belongs to |
| subfield            | String indicating the MARC subfield that the transliteration pair belongs to |
| originial_script    | String containing the original script for the transliterated text |
| transliterated_text | String containing the transliterated text for the original script |

### Data Versions
We are providing multiple versions of the transliteration dataset. All versions contain only transliteration pairs. Some versions have minimal fields excluded while others contain only personal name or corporate name fields.

All files are gzipped with the largest being 0.05GB in size.

## Dataset Creation
## Curation Rationale
This dataset has been created on behalf of the Library of Congress.

## Source Data
The source data comprises MARC cataloging records which have been send directly to us by the Library of Congress.

### Initial Data Collection and Normalization
#### Data Retrieval
The MARC cataloging records were sent directly to us by the Library of Congress in the form of TXT files.

#### Normalization
We have made the decision to not perform any text related pre-processing on the original script or transliterated text. If a subfield value contains mixed characters we have not attempted to split different character set types.

#### Filtering and Exclusion
We have filtered out any field and subfield values that do not contain Japanese transliterated pairs. Additionally, the `650` and any `3XX` and `5XX` fields have been excluded as these normally do not contain any transliterated text or can contain transliterated texts along with personal names which complicate the process when creating distinct name only and no name datasets.

We extracted the transliteration pairs by using the `880` field which contain pointers to the field and subfield. The extracted pairs are then verified in reverse using its pointer to ensure a correct match.

In cases of dataset versions containing only personal names or only corporate names, only the `a` subfields from the relevant fields have been targetted as requested. This ensures that these datasets consist entirely of (personal/corporate) names only.


### Personal and Sensitive Information


## Considerations for Using the Data

### Social Impact of Dataset
LC input needed regarding preferred readings.

### Dicussion of Biases
LC input needed regarding preferred readings.

### Other Known Limitations


## Additional Information

### Dataset Curators
### Licensing Information
LC input needed regarding licensing.

### Citation Information

# How to run
Instructions for running any specific part of the code can be found in the relevant subdirectory.

