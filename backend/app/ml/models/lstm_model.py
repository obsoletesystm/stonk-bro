"""LSTM model for stock price prediction"""
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from typing import Tuple, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class StockDataset(Dataset):
    """PyTorch Dataset for stock time series"""

    def __init__(self, X: np.ndarray, y: np.ndarray, sequence_length: int = 60):
        """
        Args:
            X: Feature array (samples, features)
            y: Target array (samples,)
            sequence_length: Length of input sequences
        """
        self.X = torch.FloatTensor(X)
        self.y = torch.FloatTensor(y)
        self.sequence_length = sequence_length

    def __len__(self):
        return len(self.X) - self.sequence_length

    def __getitem__(self, idx):
        return (
            self.X[idx:idx + self.sequence_length],
            self.y[idx + self.sequence_length]
        )


class LSTMModel(nn.Module):
    """LSTM neural network for stock prediction"""

    def __init__(
        self,
        input_size: int,
        hidden_size: int = 128,
        num_layers: int = 2,
        dropout: float = 0.2,
        bidirectional: bool = False
    ):
        """
        Args:
            input_size: Number of input features
            hidden_size: Number of LSTM hidden units
            num_layers: Number of LSTM layers
            dropout: Dropout probability
            bidirectional: Use bidirectional LSTM
        """
        super(LSTMModel, self).__init__()

        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.bidirectional = bidirectional

        # LSTM layers
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            dropout=dropout if num_layers > 1 else 0,
            batch_first=True,
            bidirectional=bidirectional
        )

        # Fully connected layers
        fc_input_size = hidden_size * 2 if bidirectional else hidden_size
        self.fc1 = nn.Linear(fc_input_size, 64)
        self.fc2 = nn.Linear(64, 32)
        self.fc3 = nn.Linear(32, 1)

        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        """Forward pass"""
        # LSTM
        lstm_out, _ = self.lstm(x)

        # Take output from last time step
        out = lstm_out[:, -1, :]

        # Fully connected layers
        out = self.relu(self.fc1(out))
        out = self.dropout(out)
        out = self.relu(self.fc2(out))
        out = self.dropout(out)
        out = self.fc3(out)

        return out


class LSTMPredictor:
    """LSTM-based stock price predictor"""

    def __init__(
        self,
        input_size: int,
        sequence_length: int = 60,
        hidden_size: int = 128,
        num_layers: int = 2,
        dropout: float = 0.2,
        learning_rate: float = 0.001,
        device: Optional[str] = None
    ):
        """
        Args:
            input_size: Number of input features
            sequence_length: Length of input sequences
            hidden_size: Number of LSTM hidden units
            num_layers: Number of LSTM layers
            dropout: Dropout probability
            learning_rate: Learning rate for optimizer
            device: Device to use ('cuda' or 'cpu')
        """
        self.input_size = input_size
        self.sequence_length = sequence_length
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.dropout = dropout
        self.learning_rate = learning_rate

        # Set device
        if device is None:
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = torch.device(device)

        # Initialize model
        self.model = LSTMModel(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            dropout=dropout
        ).to(self.device)

        # Loss and optimizer
        self.criterion = nn.MSELoss()
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=learning_rate)

        logger.info(f"Initialized LSTM model on {self.device}")
        logger.info(f"Model parameters: {sum(p.numel() for p in self.model.parameters()):,}")

    def train(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: Optional[np.ndarray] = None,
        y_val: Optional[np.ndarray] = None,
        epochs: int = 100,
        batch_size: int = 32,
        early_stopping_patience: int = 10,
        verbose: bool = True
    ) -> Dict[str, list]:
        """
        Train the LSTM model

        Args:
            X_train: Training features
            y_train: Training targets
            X_val: Validation features
            y_val: Validation targets
            epochs: Number of training epochs
            batch_size: Batch size
            early_stopping_patience: Patience for early stopping
            verbose: Print training progress

        Returns:
            Dictionary with training history
        """
        # Create datasets
        train_dataset = StockDataset(X_train, y_train, self.sequence_length)
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

        has_validation = X_val is not None and y_val is not None
        if has_validation:
            val_dataset = StockDataset(X_val, y_val, self.sequence_length)
            val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

        # Training history
        history = {
            'train_loss': [],
            'val_loss': [] if has_validation else None
        }

        best_val_loss = float('inf')
        patience_counter = 0

        for epoch in range(epochs):
            # Training phase
            self.model.train()
            train_losses = []

            for X_batch, y_batch in train_loader:
                X_batch = X_batch.to(self.device)
                y_batch = y_batch.to(self.device).unsqueeze(1)

                # Forward pass
                self.optimizer.zero_grad()
                predictions = self.model(X_batch)
                loss = self.criterion(predictions, y_batch)

                # Backward pass
                loss.backward()
                self.optimizer.step()

                train_losses.append(loss.item())

            avg_train_loss = np.mean(train_losses)
            history['train_loss'].append(avg_train_loss)

            # Validation phase
            if has_validation:
                self.model.eval()
                val_losses = []

                with torch.no_grad():
                    for X_batch, y_batch in val_loader:
                        X_batch = X_batch.to(self.device)
                        y_batch = y_batch.to(self.device).unsqueeze(1)

                        predictions = self.model(X_batch)
                        loss = self.criterion(predictions, y_batch)
                        val_losses.append(loss.item())

                avg_val_loss = np.mean(val_losses)
                history['val_loss'].append(avg_val_loss)

                # Early stopping
                if avg_val_loss < best_val_loss:
                    best_val_loss = avg_val_loss
                    patience_counter = 0
                else:
                    patience_counter += 1

                if patience_counter >= early_stopping_patience:
                    if verbose:
                        logger.info(f"Early stopping at epoch {epoch + 1}")
                    break

                if verbose and (epoch + 1) % 10 == 0:
                    logger.info(
                        f"Epoch {epoch + 1}/{epochs} - "
                        f"Train Loss: {avg_train_loss:.6f}, "
                        f"Val Loss: {avg_val_loss:.6f}"
                    )
            else:
                if verbose and (epoch + 1) % 10 == 0:
                    logger.info(f"Epoch {epoch + 1}/{epochs} - Train Loss: {avg_train_loss:.6f}")

        return history

    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Make predictions

        Args:
            X: Input features

        Returns:
            Predictions array
        """
        self.model.eval()

        dataset = StockDataset(X, np.zeros(len(X)), self.sequence_length)
        loader = DataLoader(dataset, batch_size=32, shuffle=False)

        predictions = []

        with torch.no_grad():
            for X_batch, _ in loader:
                X_batch = X_batch.to(self.device)
                pred = self.model(X_batch)
                predictions.extend(pred.cpu().numpy())

        return np.array(predictions).flatten()

    def evaluate(self, X: np.ndarray, y: np.ndarray) -> Dict[str, float]:
        """
        Evaluate model performance

        Args:
            X: Input features
            y: True targets

        Returns:
            Dictionary with evaluation metrics
        """
        predictions = self.predict(X)

        # Align predictions with targets (account for sequence length)
        y_aligned = y[self.sequence_length:]
        predictions_aligned = predictions[:len(y_aligned)]

        mse = np.mean((predictions_aligned - y_aligned) ** 2)
        rmse = np.sqrt(mse)
        mae = np.mean(np.abs(predictions_aligned - y_aligned))

        # R² score
        ss_res = np.sum((y_aligned - predictions_aligned) ** 2)
        ss_tot = np.sum((y_aligned - np.mean(y_aligned)) ** 2)
        r2 = 1 - (ss_res / ss_tot)

        return {
            'mse': float(mse),
            'rmse': float(rmse),
            'mae': float(mae),
            'r2': float(r2)
        }

    def save_model(self, path: str):
        """Save model to file"""
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'input_size': self.input_size,
            'sequence_length': self.sequence_length,
            'hidden_size': self.hidden_size,
            'num_layers': self.num_layers,
            'dropout': self.dropout,
            'learning_rate': self.learning_rate
        }, path)
        logger.info(f"Model saved to {path}")

    def load_model(self, path: str):
        """Load model from file"""
        checkpoint = torch.load(path, map_location=self.device)

        self.input_size = checkpoint['input_size']
        self.sequence_length = checkpoint['sequence_length']
        self.hidden_size = checkpoint['hidden_size']
        self.num_layers = checkpoint['num_layers']
        self.dropout = checkpoint['dropout']
        self.learning_rate = checkpoint['learning_rate']

        # Reinitialize model with loaded parameters
        self.model = LSTMModel(
            input_size=self.input_size,
            hidden_size=self.hidden_size,
            num_layers=self.num_layers,
            dropout=self.dropout
        ).to(self.device)

        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])

        logger.info(f"Model loaded from {path}")
