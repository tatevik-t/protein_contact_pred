# Protein Contact Prediction

A research project focused on enhancing protein residue-residue contact prediction using ESM2 (Evolutionary Scale Modeling) and structural features.

## Overview

This project implements a hybrid approach to protein contact prediction by:
- Leveraging pre-trained ESM2 language models
- Incorporating structural features
- Combining sequence and structure information for improved accuracy

## Setup

1. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Data Preparation
1. Download some data (feel free to stop at any time) with the following command

```bash
rsync -rlpt -v -z --delete --port=33444 rsync.rcsb.org::ftp_data/structures/divided/pdb/ ./pdb
```

2. Place your PDB files in the `data/raw` directory
3. Process the data:

```bash
python preprocess_pdb.py data/raw data/processed --log_file process.log
```

4. Create csv (default 300 proteins)
```bash
python create_df.py
```

### Experiments
1. Configure your experiment in `experiments/_________.yaml`
2. E.g to use vanilla esm2 contact predictor head run the following command
```bash
python3 main.py -c experiments/e0_vanilla_esm_head/config.yaml
```

## Documentation

The report should be found in [report.md](docs/report.md)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
