import torch
from esm import pretrained
import numpy as np
import os
import torch
import pandas as pd
import logging
from tqdm import tqdm


class ESMContactPrediction:
    def __init__(self, config):
        self.model_name = config["model_name"]
        self.output_dir = config["output_dir"]
        os.makedirs(self.output_dir, exist_ok=True)
        self.model, self.alphabet = pretrained.load_model_and_alphabet(self.model_name)
        self.batch_converter = self.alphabet.get_batch_converter()

    def run(self):
        """Run ESM contact prediction."""
        logger = logging.getLogger(__name__)
        logger.info(
            "[ESMContactPrediction] Running ESM contact prediction using model: %s",
            self.model_name,
        )

        # Load sequences
        df = pd.read_csv("data/proteins.csv")
        sequences = [
            (row["protein"], eval(row["contact_map"])) for _, row in df.iterrows()
        ]

        batch_size = 1
        for i in tqdm(range(0, len(sequences), batch_size)):
            batch_sequences = sequences[i : i + batch_size]
            batch_labels, batch_strs, batch_tokens = self.batch_converter(
                batch_sequences
            )

            # Predict contacts
            with torch.no_grad():
                results = self.model(
                    batch_tokens, repr_layers=[33], return_contacts=True
                )
                contacts = results["contacts"]

            # Save contacts
            for j, (label, contact) in enumerate(zip(batch_labels, contacts)):
                output_file = os.path.join(self.output_dir, f"{label}_contacts.npy")
                np.save(output_file, contact.cpu().numpy())
                logger.info(
                    "[ESMContactPrediction] Saved contact map to: %s", output_file
                )
