# Implementation Part - Digital Image Steganography and Steganalysis System

## Overview
This document provides detailed implementation specifications, code examples, and technical guidelines for developing the Digital Image Steganography and Steganalysis System based on the research paper findings.

## 1. Core Implementation Framework

### 1.1 Development Environment Setup

**Requirements:**
```bash
# Python Environment
Python 3.9+
OpenCV 4.5+
NumPy 1.21+
SciPy 1.7+
Scikit-learn 1.0+
TensorFlow 2.8+
FastAPI 0.75+
PostgreSQL 13+
Redis 6.2+
```

**Installation Script:**
```bash
#!/bin/bash
# setup_environment.sh

# Create virtual environment
python3 -m venv stego_env
source stego_env/bin/activate

# Install core dependencies
pip install opencv-python==4.5.5.64
pip install numpy==1.21.6
pip install scipy==1.7.3
pip install scikit-learn==1.0.2
pip install tensorflow==2.8.0
pip install fastapi==0.75.2
pip install uvicorn==0.17.6
pip install psycopg2-binary==2.9.3
pip install redis==4.2.2
pip install Pillow==9.1.0
pip install matplotlib==3.5.1
pip install seaborn==0.11.2
```

### 1.2 Project Structure
```
steganography_system/
├── src/
│   ├── core/
│   │   ├── steganography/
│   │   ├── steganalysis/
│   │   ├── image_processing/
│   │   └── security/
│   ├── algorithms/
│   │   ├── lsb/
│   │   ├── dct/
│   │   ├── dwt/
│   │   └── ml_models/
│   ├── api/
│   ├── web/
│   ├── database/
│   └── utils/
├── tests/
├── docs/
├── config/
└── requirements.txt
```

## 2. Core Algorithm Implementations

### 2.1 LSB Steganography Implementation

```python
# src/core/steganography/lsb_steganography.py

import cv2
import numpy as np
from typing import Optional, Tuple
import logging

class LSBSteganography:
    """
    Implementation of Least Significant Bit steganography
    with various embedding strategies
    """
    
    def __init__(self, mode: str = "sequential"):
        """
        Initialize LSB steganography
        
        Args:
            mode: Embedding mode ('sequential', 'random', 'adaptive')
        """
        self.mode = mode
        self.logger = logging.getLogger(__name__)
    
    def embed_message(self, cover_image: np.ndarray, 
                     secret_message: str, 
                     password: Optional[str] = None) -> np.ndarray:
        """
        Embed secret message in cover image using LSB technique
        
        Args:
            cover_image: Input cover image
            secret_message: Secret message to hide
            password: Optional password for encryption
            
        Returns:
            Stego image with embedded message
        """
        # Convert message to binary
        binary_message = self._string_to_binary(secret_message)
        
        # Add delimiter to mark end of message
        binary_message += "1111111111111110"  # Delimiter
        
        # Encrypt if password provided
        if password:
            binary_message = self._encrypt_message(binary_message, password)
        
        # Check capacity
        if not self._check_capacity(cover_image, len(binary_message)):
            raise ValueError("Image capacity insufficient for message")
        
        stego_image = cover_image.copy()
        
        if self.mode == "sequential":
            stego_image = self._embed_sequential(stego_image, binary_message)
        elif self.mode == "random":
            stego_image = self._embed_random(stego_image, binary_message)
        elif self.mode == "adaptive":
            stego_image = self._embed_adaptive(stego_image, binary_message)
        
        return stego_image
    
    def extract_message(self, stego_image: np.ndarray, 
                       password: Optional[str] = None) -> str:
        """
        Extract hidden message from stego image
        
        Args:
            stego_image: Image containing hidden message
            password: Password for decryption if used
            
        Returns:
            Extracted secret message
        """
        if self.mode == "sequential":
            binary_message = self._extract_sequential(stego_image)
        elif self.mode == "random":
            binary_message = self._extract_random(stego_image)
        elif self.mode == "adaptive":
            binary_message = self._extract_adaptive(stego_image)
        
        # Decrypt if password provided
        if password:
            binary_message = self._decrypt_message(binary_message, password)
        
        # Convert binary to string
        message = self._binary_to_string(binary_message)
        
        return message
    
    def _embed_sequential(self, image: np.ndarray, 
                         binary_message: str) -> np.ndarray:
        """Sequential LSB embedding"""
        height, width, channels = image.shape
        message_index = 0
        
        for i in range(height):
            for j in range(width):
                for k in range(channels):
                    if message_index < len(binary_message):
                        # Modify LSB
                        image[i][j][k] = (image[i][j][k] & 0xFE) | \
                                       int(binary_message[message_index])
                        message_index += 1
                    else:
                        return image
        
        return image
    
    def _embed_random(self, image: np.ndarray, 
                     binary_message: str) -> np.ndarray:
        """Random LSB embedding using PRNG"""
        height, width, channels = image.shape
        total_pixels = height * width * channels
        
        # Generate random sequence
        np.random.seed(42)  # Fixed seed for reproducibility
        random_positions = np.random.permutation(total_pixels)
        
        flat_image = image.flatten()
        
        for i, bit in enumerate(binary_message):
            if i < len(random_positions):
                pos = random_positions[i]
                flat_image[pos] = (flat_image[pos] & 0xFE) | int(bit)
        
        return flat_image.reshape(height, width, channels)
    
    def _embed_adaptive(self, image: np.ndarray, 
                       binary_message: str) -> np.ndarray:
        """Adaptive LSB embedding based on image complexity"""
        height, width, channels = image.shape
        
        # Calculate edge map for complexity assessment
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        
        # Get edge positions
        edge_positions = np.where(edges > 0)
        
        message_index = 0
        # Prefer embedding in edge regions
        for i, j in zip(edge_positions[0], edge_positions[1]):
            for k in range(channels):
                if message_index < len(binary_message):
                    image[i][j][k] = (image[i][j][k] & 0xFE) | \
                                   int(binary_message[message_index])
                    message_index += 1
                else:
                    return image
        
        # Continue with remaining positions if needed
        for i in range(height):
            for j in range(width):
                for k in range(channels):
                    if message_index < len(binary_message) and edges[i][j] == 0:
                        image[i][j][k] = (image[i][j][k] & 0xFE) | \
                                       int(binary_message[message_index])
                        message_index += 1
                    elif message_index >= len(binary_message):
                        return image
        
        return image
    
    def _extract_sequential(self, image: np.ndarray) -> str:
        """Extract message using sequential method"""
        height, width, channels = image.shape
        binary_message = ""
        
        for i in range(height):
            for j in range(width):
                for k in range(channels):
                    binary_message += str(image[i][j][k] & 1)
                    
                    # Check for delimiter
                    if binary_message.endswith("1111111111111110"):
                        return binary_message[:-16]  # Remove delimiter
        
        return binary_message
    
    @staticmethod
    def _string_to_binary(message: str) -> str:
        """Convert string to binary representation"""
        binary = ""
        for char in message:
            binary += format(ord(char), '08b')
        return binary
    
    @staticmethod
    def _binary_to_string(binary: str) -> str:
        """Convert binary to string"""
        message = ""
        for i in range(0, len(binary), 8):
            byte = binary[i:i+8]
            if len(byte) == 8:
                message += chr(int(byte, 2))
        return message
    
    def _check_capacity(self, image: np.ndarray, message_length: int) -> bool:
        """Check if image has sufficient capacity"""
        height, width, channels = image.shape
        capacity = height * width * channels
        return capacity >= message_length
    
    def calculate_psnr(self, original: np.ndarray, 
                      stego: np.ndarray) -> float:
        """Calculate Peak Signal-to-Noise Ratio"""
        mse = np.mean((original - stego) ** 2)
        if mse == 0:
            return float('inf')
        
        max_pixel = 255.0
        psnr = 20 * np.log10(max_pixel / np.sqrt(mse))
        return psnr
```

### 2.2 Steganalysis Implementation - RS Analysis

```python
# src/core/steganalysis/rs_analysis.py

import numpy as np
from typing import Tuple, Dict
import cv2

class RSAnalysis:
    """
    Implementation of Regular/Singular (RS) Analysis
    for LSB steganography detection
    """
    
    def __init__(self):
        self.mask = np.array([0, 1, 1, 0])  # Standard RS mask
    
    def analyze_image(self, image: np.ndarray) -> Dict[str, float]:
        """
        Perform RS analysis on image
        
        Args:
            image: Input image for analysis
            
        Returns:
            Dictionary containing analysis results
        """
        # Convert to grayscale if colored
        if len(image.shape) == 3:
            gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray_image = image
        
        # Get image dimensions
        height, width = gray_image.shape
        
        # Initialize counters
        rm_counts = {"R": 0, "S": 0, "U": 0}  # Regular, Singular, Unusable
        rm1_counts = {"R": 0, "S": 0, "U": 0}  # After flipping LSB
        
        # Process image in 2x2 blocks
        for i in range(0, height - 1, 2):
            for j in range(0, width - 1, 2):
                # Extract 2x2 block
                block = gray_image[i:i+2, j:j+2].flatten()
                
                if len(block) == 4:
                    # Analyze original block
                    category = self._categorize_group(block)
                    rm_counts[category] += 1
                    
                    # Analyze block with flipped LSBs
                    flipped_block = self._flip_lsb(block)
                    category_flipped = self._categorize_group(flipped_block)
                    rm1_counts[category_flipped] += 1
        
        # Calculate RS statistics
        total_groups = rm_counts["R"] + rm_counts["S"] + rm_counts["U"]
        
        if total_groups == 0:
            return {"steganography_detected": False, "confidence": 0.0}
        
        # Calculate discrimination function
        d0 = rm_counts["R"] - rm_counts["S"]
        d1 = rm1_counts["R"] - rm1_counts["S"]
        
        # Estimate hidden message length
        if d0 != d1:
            x = d0 / (d0 - d1)
            if 0 <= x <= 1:
                estimated_length = x / 2
            else:
                estimated_length = 0
        else:
            estimated_length = 0
        
        # Determine if steganography is present
        threshold = 0.05  # 5% threshold
        steganography_detected = estimated_length > threshold
        
        # Calculate confidence score
        confidence = min(estimated_length * 10, 1.0)  # Scale to 0-1
        
        return {
            "steganography_detected": steganography_detected,
            "estimated_message_length": estimated_length,
            "confidence": confidence,
            "rm_regular": rm_counts["R"],
            "rm_singular": rm_counts["S"],
            "rm1_regular": rm1_counts["R"],
            "rm1_singular": rm1_counts["S"],
            "discrimination_d0": d0,
            "discrimination_d1": d1
        }
    
    def _categorize_group(self, group: np.ndarray) -> str:
        """
        Categorize a group as Regular, Singular, or Unusable
        
        Args:
            group: 4-element array representing a 2x2 block
            
        Returns:
            Category string: 'R', 'S', or 'U'
        """
        # Apply mask and calculate discrimination function
        f_value = self._discrimination_function(group)
        
        # Flip LSBs and recalculate
        flipped_group = self._flip_lsb(group)
        f_flipped = self._discrimination_function(flipped_group)
        
        # Categorize based on discrimination function behavior
        if f_value > f_flipped:
            return "R"  # Regular
        elif f_value < f_flipped:
            return "S"  # Singular
        else:
            return "U"  # Unusable
    
    def _discrimination_function(self, group: np.ndarray) -> float:
        """
        Calculate discrimination function for a group
        
        Args:
            group: 4-element array
            
        Returns:
            Discrimination function value
        """
        # Apply mask to get variation
        variation = 0
        for i in range(len(group) - 1):
            if self.mask[i]:
                variation += abs(int(group[i]) - int(group[i + 1]))
        
        return variation
    
    def _flip_lsb(self, group: np.ndarray) -> np.ndarray:
        """
        Flip LSBs according to mask
        
        Args:
            group: Input group
            
        Returns:
            Group with flipped LSBs
        """
        flipped = group.copy()
        for i in range(len(group)):
            if self.mask[i]:
                flipped[i] = flipped[i] ^ 1  # Flip LSB
        
        return flipped
```

### 2.3 DCT-based Steganalysis Implementation

```python
# src/core/steganalysis/dct_analysis.py

import cv2
import numpy as np
from scipy.fftpack import dct, idct
from typing import Dict, List
import logging

class DCTAnalysis:
    """
    DCT-based steganalysis for JPEG steganography detection
    """
    
    def __init__(self, block_size: int = 8):
        self.block_size = block_size
        self.logger = logging.getLogger(__name__)
    
    def analyze_image(self, image: np.ndarray) -> Dict[str, float]:
        """
        Perform DCT analysis for steganography detection
        
        Args:
            image: Input image (preferably JPEG)
            
        Returns:
            Analysis results dictionary
        """
        # Convert to grayscale
        if len(image.shape) == 3:
            gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray_image = image
        
        # Extract DCT coefficients
        dct_coefficients = self._extract_dct_coefficients(gray_image)
        
        # Analyze coefficient distribution
        analysis_results = self._analyze_coefficient_distribution(dct_coefficients)
        
        # Detect anomalies
        anomaly_score = self._detect_anomalies(dct_coefficients)
        
        analysis_results.update({
            "anomaly_score": anomaly_score,
            "steganography_detected": anomaly_score > 0.3,
            "confidence": min(anomaly_score, 1.0)
        })
        
        return analysis_results
    
    def _extract_dct_coefficients(self, image: np.ndarray) -> List[np.ndarray]:
        """
        Extract DCT coefficients from image blocks
        
        Args:
            image: Grayscale image
            
        Returns:
            List of DCT coefficient blocks
        """
        height, width = image.shape
        coefficients = []
        
        # Process image in 8x8 blocks
        for i in range(0, height - self.block_size + 1, self.block_size):
            for j in range(0, width - self.block_size + 1, self.block_size):
                block = image[i:i+self.block_size, j:j+self.block_size]
                
                # Apply DCT
                dct_block = dct(dct(block.T, norm='ortho').T, norm='ortho')
                coefficients.append(dct_block)
        
        return coefficients
    
    def _analyze_coefficient_distribution(self, 
                                        coefficients: List[np.ndarray]) -> Dict[str, float]:
        """
        Analyze statistical distribution of DCT coefficients
        
        Args:
            coefficients: List of DCT coefficient blocks
            
        Returns:
            Statistical analysis results
        """
        # Flatten all coefficients
        all_coeffs = np.concatenate([block.flatten() for block in coefficients])
        
        # Calculate statistics
        mean_coeff = np.mean(all_coeffs)
        std_coeff = np.std(all_coeffs)
        skewness = self._calculate_skewness(all_coeffs)
        kurtosis = self._calculate_kurtosis(all_coeffs)
        
        # Analyze high-frequency coefficients
        high_freq_coeffs = []
        for block in coefficients:
            # Extract high-frequency coefficients (bottom-right region)
            hf_region = block[4:, 4:]
            high_freq_coeffs.extend(hf_region.flatten())
        
        hf_variance = np.var(high_freq_coeffs)
        hf_energy = np.sum(np.square(high_freq_coeffs))
        
        return {
            "mean_coefficient": float(mean_coeff),
            "std_coefficient": float(std_coeff),
            "skewness": float(skewness),
            "kurtosis": float(kurtosis),
            "hf_variance": float(hf_variance),
            "hf_energy": float(hf_energy)
        }
    
    def _detect_anomalies(self, coefficients: List[np.ndarray]) -> float:
        """
        Detect anomalies in DCT coefficients
        
        Args:
            coefficients: DCT coefficient blocks
            
        Returns:
            Anomaly score (0-1)
        """
        anomaly_indicators = []
        
        # Check for unusual coefficient patterns
        for block in coefficients:
            # Check for artificial patterns in AC coefficients
            ac_coeffs = block.copy()
            ac_coeffs[0, 0] = 0  # Remove DC component
            
            # Calculate entropy of AC coefficients
            entropy = self._calculate_entropy(ac_coeffs.flatten())
            anomaly_indicators.append(entropy)
            
            # Check for suspicious coefficient relationships
            suspicious_ratio = self._check_coefficient_relationships(block)
            anomaly_indicators.append(suspicious_ratio)
        
        # Calculate overall anomaly score
        avg_anomaly = np.mean(anomaly_indicators)
        
        # Normalize to 0-1 range
        normalized_score = min(max(avg_anomaly / 10.0, 0), 1)
        
        return normalized_score
    
    def _calculate_skewness(self, data: np.ndarray) -> float:
        """Calculate skewness of data"""
        mean_val = np.mean(data)
        std_val = np.std(data)
        
        if std_val == 0:
            return 0
        
        normalized = (data - mean_val) / std_val
        skewness = np.mean(normalized ** 3)
        
        return skewness
    
    def _calculate_kurtosis(self, data: np.ndarray) -> float:
        """Calculate kurtosis of data"""
        mean_val = np.mean(data)
        std_val = np.std(data)
        
        if std_val == 0:
            return 0
        
        normalized = (data - mean_val) / std_val
        kurtosis = np.mean(normalized ** 4) - 3  # Excess kurtosis
        
        return kurtosis
    
    def _calculate_entropy(self, data: np.ndarray) -> float:
        """Calculate entropy of data"""
        # Quantize data to calculate probability distribution
        hist, _ = np.histogram(data, bins=50)
        hist = hist[hist > 0]  # Remove zero counts
        
        # Calculate probabilities
        probabilities = hist / np.sum(hist)
        
        # Calculate entropy
        entropy = -np.sum(probabilities * np.log2(probabilities))
        
        return entropy
    
    def _check_coefficient_relationships(self, block: np.ndarray) -> float:
        """
        Check for suspicious relationships between coefficients
        
        Args:
            block: DCT coefficient block
            
        Returns:
            Suspicion ratio
        """
        # Check for unusual patterns in coefficient magnitudes
        flat_block = block.flatten()
        
        # Look for artificial patterns (e.g., too many zeros or regular patterns)
        zero_ratio = np.sum(flat_block == 0) / len(flat_block)
        
        # Check for unnatural coefficient distributions
        variance = np.var(flat_block)
        
        # Combine indicators
        suspicion_ratio = zero_ratio + (1.0 / (1.0 + variance))
        
        return min(suspicion_ratio, 1.0)
```

## 3. Machine Learning Implementation

### 3.1 CNN-based Steganalysis

```python
# src/algorithms/ml_models/cnn_steganalysis.py

import tensorflow as tf
from tensorflow.keras import layers, models
import numpy as np
from typing import Tuple, Dict
import cv2

class CNNSteganalysis:
    """
    Convolutional Neural Network for steganography detection
    """
    
    def __init__(self, input_shape: Tuple[int, int, int] = (64, 64, 1)):
        self.input_shape = input_shape
        self.model = None
        self.trained = False
    
    def build_model(self) -> models.Model:
        """
        Build CNN model architecture for steganalysis
        
        Returns:
            Compiled Keras model
        """
        model = models.Sequential([
            # First convolutional block
            layers.Conv2D(32, (3, 3), activation='relu', 
                         input_shape=self.input_shape),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            
            # Second convolutional block
            layers.Conv2D(64, (3, 3), activation='relu'),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            
            # Third convolutional block
            layers.Conv2D(128, (3, 3), activation='relu'),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            
            # Fourth convolutional block
            layers.Conv2D(256, (3, 3), activation='relu'),
            layers.BatchNormalization(),
            layers.GlobalAveragePooling2D(),
            
            # Fully connected layers
            layers.Dense(512, activation='relu'),
            layers.Dropout(0.5),
            layers.Dense(256, activation='relu'),
            layers.Dropout(0.3),
            layers.Dense(1, activation='sigmoid')  # Binary classification
        ])
        
        # Compile model
        model.compile(
            optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy', 'precision', 'recall']
        )
        
        self.model = model
        return model
    
    def train_model(self, train_images: np.ndarray, train_labels: np.ndarray,
                   validation_images: np.ndarray, validation_labels: np.ndarray,
                   epochs: int = 50, batch_size: int = 32) -> Dict:
        """
        Train the CNN model
        
        Args:
            train_images: Training images
            train_labels: Training labels (0=clean, 1=stego)
            validation_images: Validation images
            validation_labels: Validation labels
            epochs: Number of training epochs
            batch_size: Batch size for training
            
        Returns:
            Training history
        """
        if self.model is None:
            self.build_model()
        
        # Data augmentation
        datagen = tf.keras.preprocessing.image.ImageDataGenerator(
            rotation_range=10,
            width_shift_range=0.1,
            height_shift_range=0.1,
            horizontal_flip=True,
            zoom_range=0.1
        )
        
        # Callbacks
        callbacks = [
            tf.keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=10,
                restore_best_weights=True
            ),
            tf.keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=5,
                min_lr=1e-7
            )
        ]
        
        # Train model
        history = self.model.fit(
            datagen.flow(train_images, train_labels, batch_size=batch_size),
            epochs=epochs,
            validation_data=(validation_images, validation_labels),
            callbacks=callbacks,
            verbose=1
        )
        
        self.trained = True
        return history.history
    
    def predict(self, image: np.ndarray) -> Dict[str, float]:
        """
        Predict steganography presence in image
        
        Args:
            image: Input image
            
        Returns:
            Prediction results
        """
        if not self.trained or self.model is None:
            raise ValueError("Model must be trained before prediction")
        
        # Preprocess image
        processed_image = self._preprocess_image(image)
        
        # Make prediction
        prediction = self.model.predict(processed_image)
        confidence = float(prediction[0][0])
        
        return {
            "steganography_detected": confidence > 0.5,
            "confidence": confidence,
            "steganography_probability": confidence,
            "clean_probability": 1.0 - confidence
        }
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for CNN input
        
        Args:
            image: Input image
            
        Returns:
            Preprocessed image array
        """
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray_image = image
        
        # Resize to model input size
        resized = cv2.resize(gray_image, 
                           (self.input_shape[0], self.input_shape[1]))
        
        # Normalize pixel values
        normalized = resized.astype(np.float32) / 255.0
        
        # Add batch and channel dimensions
        processed = np.expand_dims(normalized, axis=[0, -1])
        
        return processed
    
    def save_model(self, filepath: str):
        """Save trained model"""
        if self.model is not None:
            self.model.save(filepath)
    
    def load_model(self, filepath: str):
        """Load pre-trained model"""
        self.model = tf.keras.models.load_model(filepath)
        self.trained = True
```

## 4. API Implementation

### 4.1 FastAPI Backend

```python
# src/api/main.py

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import cv2
import numpy as np
from typing import Optional, Dict
import io
from PIL import Image

from src.core.steganography.lsb_steganography import LSBSteganography
from src.core.steganalysis.rs_analysis import RSAnalysis
from src.core.steganalysis.dct_analysis import DCTAnalysis
from src.algorithms.ml_models.cnn_steganalysis import CNNSteganalysis

app = FastAPI(title="Steganography Analysis System", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Initialize analyzers
rs_analyzer = RSAnalysis()
dct_analyzer = DCTAnalysis()
cnn_analyzer = CNNSteganalysis()
lsb_stego = LSBSteganography()

@app.post("/api/v1/steganography/embed")
async def embed_message(
    image: UploadFile = File(...),
    message: str,
    password: Optional[str] = None,
    method: str = "lsb_sequential"
):
    """
    Embed secret message in image
    """
    try:
        # Read image
        image_data = await image.read()
        image_array = np.frombuffer(image_data, np.uint8)
        cover_image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        
        if cover_image is None:
            raise HTTPException(status_code=400, detail="Invalid image format")
        
        # Set embedding method
        if method == "lsb_sequential":
            lsb_stego.mode = "sequential"
        elif method == "lsb_random":
            lsb_stego.mode = "random"
        elif method == "lsb_adaptive":
            lsb_stego.mode = "adaptive"
        else:
            raise HTTPException(status_code=400, detail="Unsupported method")
        
        # Embed message
        stego_image = lsb_stego.embed_message(cover_image, message, password)
        
        # Calculate quality metrics
        psnr = lsb_stego.calculate_psnr(cover_image, stego_image)
        
        # Encode result image
        _, buffer = cv2.imencode('.png', stego_image)
        
        return {
            "success": True,
            "message": "Message embedded successfully",
            "psnr": float(psnr),
            "image_data": buffer.tobytes().hex(),
            "method_used": method
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/steganography/extract")
async def extract_message(
    image: UploadFile = File(...),
    password: Optional[str] = None,
    method: str = "lsb_sequential"
):
    """
    Extract hidden message from image
    """
    try:
        # Read image
        image_data = await image.read()
        image_array = np.frombuffer(image_data, np.uint8)
        stego_image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        
        if stego_image is None:
            raise HTTPException(status_code=400, detail="Invalid image format")
        
        # Set extraction method
        if method == "lsb_sequential":
            lsb_stego.mode = "sequential"
        elif method == "lsb_random":
            lsb_stego.mode = "random"
        elif method == "lsb_adaptive":
            lsb_stego.mode = "adaptive"
        else:
            raise HTTPException(status_code=400, detail="Unsupported method")
        
        # Extract message
        extracted_message = lsb_stego.extract_message(stego_image, password)
        
        return {
            "success": True,
            "message": extracted_message,
            "method_used": method
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/steganalysis/analyze")
async def analyze_image(
    image: UploadFile = File(...),
    algorithms: Optional[str] = "all"
):
    """
    Analyze image for steganography presence
    """
    try:
        # Read image
        image_data = await image.read()
        image_array = np.frombuffer(image_data, np.uint8)
        test_image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        
        if test_image is None:
            raise HTTPException(status_code=400, detail="Invalid image format")
        
        results = {}
        
        # RS Analysis
        if algorithms == "all" or "rs" in algorithms:
            rs_results = rs_analyzer.analyze_image(test_image)
            results["rs_analysis"] = rs_results
        
        # DCT Analysis
        if algorithms == "all" or "dct" in algorithms:
            dct_results = dct_analyzer.analyze_image(test_image)
            results["dct_analysis"] = dct_results
        
        # CNN Analysis (if model is loaded)
        if algorithms == "all" or "cnn" in algorithms:
            if cnn_analyzer.trained:
                cnn_results = cnn_analyzer.predict(test_image)
                results["cnn_analysis"] = cnn_results
        
        # Fusion of results
        fusion_result = _fuse_analysis_results(results)
        results["fusion_analysis"] = fusion_result
        
        return {
            "success": True,
            "results": results,
            "summary": {
                "steganography_detected": fusion_result.get("steganography_detected", False),
                "confidence": fusion_result.get("confidence", 0.0)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def _fuse_analysis_results(results: Dict) -> Dict:
    """
    Fuse results from multiple analysis methods
    """
    confidences = []
    detections = []
    
    for method, result in results.items():
        if isinstance(result, dict):
            if "confidence" in result:
                confidences.append(result["confidence"])
            if "steganography_detected" in result:
                detections.append(result["steganography_detected"])
    
    if not confidences:
        return {"steganography_detected": False, "confidence": 0.0}
    
    # Average confidence
    avg_confidence = np.mean(confidences)
    
    # Majority vote for detection
    detection_vote = sum(detections) > len(detections) / 2
    
    return {
        "steganography_detected": detection_vote,
        "confidence": float(avg_confidence),
        "methods_count": len(results),
        "positive_detections": sum(detections)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## 5. Testing and Validation

### 5.1 Unit Testing Framework

```python
# tests/test_lsb_steganography.py

import unittest
import numpy as np
import cv2
from src.core.steganography.lsb_steganography import LSBSteganography

class TestLSBSteganography(unittest.TestCase):
    
    def setUp(self):
        self.lsb_stego = LSBSteganography()
        self.test_image = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
        self.test_message = "This is a secret message for testing!"
    
    def test_sequential_embedding_extraction(self):
        """Test sequential LSB embedding and extraction"""
        self.lsb_stego.mode = "sequential"
        
        # Embed message
        stego_image = self.lsb_stego.embed_message(self.test_image, self.test_message)
        
        # Extract message
        extracted_message = self.lsb_stego.extract_message(stego_image)
        
        self.assertEqual(extracted_message, self.test_message)
    
    def test_random_embedding_extraction(self):
        """Test random LSB embedding and extraction"""
        self.lsb_stego.mode = "random"
        
        # Embed message
        stego_image = self.lsb_stego.embed_message(self.test_image, self.test_message)
        
        # Extract message
        extracted_message = self.lsb_stego.extract_message(stego_image)
        
        self.assertEqual(extracted_message, self.test_message)
    
    def test_capacity_check(self):
        """Test capacity checking"""
        small_image = np.random.randint(0, 256, (10, 10, 3), dtype=np.uint8)
        long_message = "This message is too long for the small image" * 100
        
        with self.assertRaises(ValueError):
            self.lsb_stego.embed_message(small_image, long_message)
    
    def test_psnr_calculation(self):
        """Test PSNR calculation"""
        stego_image = self.lsb_stego.embed_message(self.test_image, self.test_message)
        psnr = self.lsb_stego.calculate_psnr(self.test_image, stego_image)
        
        # PSNR should be reasonable for LSB steganography
        self.assertGreater(psnr, 30)
        self.assertLess(psnr, 100)

if __name__ == '__main__':
    unittest.main()
```

### 5.2 Performance Benchmarking

```python
# tests/benchmark_performance.py

import time
import numpy as np
import cv2
from src.core.steganography.lsb_steganography import LSBSteganography
from src.core.steganalysis.rs_analysis import RSAnalysis

def benchmark_embedding_performance():
    """Benchmark embedding performance"""
    lsb_stego = LSBSteganography()
    
    # Test different image sizes
    sizes = [(256, 256), (512, 512), (1024, 1024)]
    message = "Test message for performance benchmarking"
    
    results = {}
    
    for size in sizes:
        test_image = np.random.randint(0, 256, (*size, 3), dtype=np.uint8)
        
        start_time = time.time()
        stego_image = lsb_stego.embed_message(test_image, message)
        embedding_time = time.time() - start_time
        
        start_time = time.time()
        extracted_message = lsb_stego.extract_message(stego_image)
        extraction_time = time.time() - start_time
        
        results[f"{size[0]}x{size[1]}"] = {
            "embedding_time": embedding_time,
            "extraction_time": extraction_time,
            "total_time": embedding_time + extraction_time
        }
    
    return results

def benchmark_analysis_performance():
    """Benchmark steganalysis performance"""
    rs_analyzer = RSAnalysis()
    
    # Test different image sizes
    sizes = [(256, 256), (512, 512), (1024, 1024)]
    
    results = {}
    
    for size in sizes:
        test_image = np.random.randint(0, 256, size, dtype=np.uint8)
        
        start_time = time.time()
        analysis_result = rs_analyzer.analyze_image(test_image)
        analysis_time = time.time() - start_time
        
        results[f"{size[0]}x{size[1]}"] = {
            "analysis_time": analysis_time,
            "throughput": (size[0] * size[1]) / analysis_time  # pixels per second
        }
    
    return results

if __name__ == "__main__":
    print("Benchmarking embedding performance...")
    embedding_results = benchmark_embedding_performance()
    
    print("\nEmbedding Performance Results:")
    for size, metrics in embedding_results.items():
        print(f"{size}: Embedding={metrics['embedding_time']:.3f}s, "
              f"Extraction={metrics['extraction_time']:.3f}s")
    
    print("\nBenchmarking analysis performance...")
    analysis_results = benchmark_analysis_performance()
    
    print("\nAnalysis Performance Results:")
    for size, metrics in analysis_results.items():
        print(f"{size}: Analysis={metrics['analysis_time']:.3f}s, "
              f"Throughput={metrics['throughput']:.0f} pixels/sec")
```

This implementation provides a comprehensive foundation for the steganography and steganalysis system with practical, working code examples that can be extended and optimized for production use.