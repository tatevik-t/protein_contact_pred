import torch
import torch.nn as nn
import numpy as np
import esm
from typing import List, Tuple, Optional


class ESM2ContactPredictor(nn.Module):
    def __init__(self, model_name: str = "esm2_t33_650M_UR50D"):
        """Initialize ESM2-based contact prediction model."""
        super().__init__()
        
        # Load pre-trained ESM2 model
        self.esm_model, self.alphabet = esm.pretrained.load_model_and_alphabet(model_name)
        self.esm_model.eval()  # Set to evaluation mode
        
        # Add contact prediction head
        esm_dim = self.esm_model.args.embed_dim
        self.contact_head = nn.Sequential(
            nn.Linear(2 * esm_dim, 512),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(512, 128),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(128, 1),
            nn.Sigmoid()
        )
        
    def _get_embeddings(self, sequence: str) -> torch.Tensor:
        """Generate ESM2 embeddings for a protein sequence."""
        # Prepare batch
        batch_tokens = self.alphabet.encode(sequence)
        batch_tokens = batch_tokens.unsqueeze(0)  # Add batch dimension
        
        # Generate embeddings
        with torch.no_grad():
            results = self.esm_model(batch_tokens, repr_layers=[33])
            embeddings = results["representations"][33]
        
        return embeddings.squeeze(0)  # Remove batch dimension
        
    def _generate_pair_embeddings(self, embeddings: torch.Tensor) -> torch.Tensor:
        """Generate pairwise embeddings for contact prediction."""
        seq_len = embeddings.size(0)
        
        # Create all pairs of residue embeddings
        embeddings_i = embeddings.unsqueeze(1).repeat(1, seq_len, 1)
        embeddings_j = embeddings.unsqueeze(0).repeat(seq_len, 1, 1)
        
        # Concatenate pairs
        pair_embeddings = torch.cat([embeddings_i, embeddings_j], dim=-1)
        return pair_embeddings
        
    def forward(self, sequence: str) -> torch.Tensor:
        """Forward pass to predict contacts."""
        # Generate embeddings
        embeddings = self._get_embeddings(sequence)
        
        # Generate pair embeddings
        pair_embeddings = self._generate_pair_embeddings(embeddings)
        
        # Predict contacts
        contacts = self.contact_head(pair_embeddings)
        contacts = contacts.squeeze(-1)  # Remove last dimension
        
        return contacts
        
    def predict_contacts(self, sequence: str, threshold: float = 0.5) -> torch.Tensor:
        """Predict protein contacts with threshold."""
        self.eval()  # Set to evaluation mode
        with torch.no_grad():
            contacts = self(sequence)
            binary_contacts = (contacts > threshold).float()
        return binary_contacts
    
    def train_step(self, 
                  sequence: str, 
                  true_contacts: torch.Tensor,
                  optimizer: torch.optim.Optimizer) -> float:
        """Perform one training step."""
        self.train()  # Set to training mode
        optimizer.zero_grad()
        
        # Forward pass
        predicted_contacts = self(sequence)
        
        # Calculate loss
        loss = nn.BCELoss()(predicted_contacts, true_contacts)
        
        # Backward pass
        loss.backward()
        optimizer.step()
        
        return loss.item()

    @staticmethod
    def load_pretrained(path: str) -> 'ESM2ContactPredictor':
        """Load a pretrained model."""
        model = ESM2ContactPredictor()
        model.load_state_dict(torch.load(path))
        return model

import os
import logging
import torch
from esm import pretrained

class ESMContactPrediction:
    def __init__(self, config):
        self.model_name = config['model_name']
        self.output_dir = config['output_dir']
        os.makedirs(self.output_dir, exist_ok=True)
        self.model, self.alphabet = pretrained.load_model_and_alphabet(self.model_name)
        self.batch_converter = self.alphabet.get_batch_converter()

    def run(self):
        """Run ESM contact prediction."""
        logger = logging.getLogger(__name__)
        logger.info("[ESMContactPrediction] Running ESM contact prediction using model: %s", self.model_name)
        
        # Example sequence (replace with actual sequences)
        sequences = [("protein1", "MKTAYIAKQRQISFVKSHFSRQDILDLWQYHKEK")]
        
        # Convert sequences to batch
        batch_labels, batch_strs, batch_tokens = self.batch_converter(sequences)
        
        # Predict contacts
        with torch.no_grad():
            results = self.model(batch_tokens, repr_layers=[33], return_contacts=True)
            contacts = results["contacts"]
        
        # Save contacts
        for i, (label, contact) in enumerate(zip(batch_labels, contacts)):
            output_file = os.path.join(self.output_dir, f"{label}_contacts.npy")
            np.save(output_file, contact.cpu().numpy())
            logger.info("[ESMContactPrediction] Saved contact map to: %s", output_file)