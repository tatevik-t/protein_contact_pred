# Protein Residue-Residue Contact Prediction Task

## Task Definition

The goal of this project is to predict residue-residue contacts in protein structures. Residue-residue contact prediction is crucial for understanding protein folding, function, and interactions. Accurate contact maps can significantly enhance the accuracy of protein structure prediction and facilitate various downstream applications in bioinformatics and structural biology.

## Data

The primary data source for this project is the Protein Data Bank (PDB), which provides a comprehensive repository of protein structures. The PDB files were downloaded using the following command:

```
rsync -rlpt -v -z --delete --port=33444 rsync.rcsb.org::ftp_data/structures/divided/pdb/ ./pdb
```

### Preprocessing Steps

Decompression: The downloaded PDB files are compressed in .gz format. These files were decompressed using a custom Python script that utilizes multiprocessing to handle multiple files in parallel.

Filtering: After decompression, the PDB files were filtered to retain only those proteins that contain 'CA' (alpha carbon) atoms. This step is crucial because 'CA' atoms are used to define residue-residue contacts.

Contact Map Generation: For each filtered PDB file, a contact map was generated. A contact map is a binary matrix where each element indicates whether a pair of residues is in contact, typically defined by a distance threshold (e.g., 8 Å).

As the PDB database is huge, the small portion was used for the experiments.

The command for preprocessing was

## Model

As a model was used ESM2 (esm2_t6_8M_UR50D) model and it's contact prediction head.

## Experiments

The main idea of an experiment lies in the fact that attention layers of ESM2 model contain the structural information.

First experiment is just using the ESM2 head to predict the contact maps.

In the second experiment, the attention weights from all layers are ranked based on the revelance to the real contact map and the metrics are measured from the top-k attention means.

In the third experiment, the ESM2 is supplied with the layer upon the contact head and fine-tuned.

In the fourth experiment, the top-k attention maps (got in the second experiment) are supplied with a layer and the layer was trained.

**NOTE**: The data processing and understanding took long time, so the experiments were not held in a proper way, so only the visualization of attention matrices can be presented: [visualization.ipynb](../notebooks/visualization.ipynb).

## Results


## Literature

*Lin, Z., Akin, H., Rao, R., Hie, B., Zhu, Z., Lu, W., ... & Rives, A. (2023). Evolutionary-scale prediction of atomic-level protein structure with a language model. Science, 379(6637), 1123-1130.*

*Lin, Z., Akin, H., Rao, R., Hie, B., Zhu, Z., Lu, W., ... & Rives, A. (2022). Language models of protein sequences at the scale of evolution enable accurate structure prediction. BioRxiv, 2022, 500902.*
