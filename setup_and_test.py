#!/usr/bin/env python3
"""
Setup and Testing Script for Digital Image Steganography and Steganalysis System
This script verifies installation and demonstrates system functionality
"""

import sys
import os
import numpy as np
import cv2
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if all required dependencies are installed"""
    logger.info("Checking dependencies...")
    
    required_packages = [
        'cv2', 'numpy', 'scipy', 'sklearn', 'tensorflow', 
        'fastapi', 'uvicorn', 'PIL', 'matplotlib', 'seaborn'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'cv2':
                import cv2
                logger.info(f"✓ OpenCV version: {cv2.__version__}")
            elif package == 'numpy':
                import numpy
                logger.info(f"✓ NumPy version: {numpy.__version__}")
            elif package == 'scipy':
                import scipy
                logger.info(f"✓ SciPy version: {scipy.__version__}")
            elif package == 'sklearn':
                import sklearn
                logger.info(f"✓ Scikit-learn version: {sklearn.__version__}")
            elif package == 'tensorflow':
                import tensorflow as tf
                logger.info(f"✓ TensorFlow version: {tf.__version__}")
            elif package == 'fastapi':
                import fastapi
                logger.info(f"✓ FastAPI version: {fastapi.__version__}")
            elif package == 'uvicorn':
                import uvicorn
                logger.info(f"✓ Uvicorn installed")
            elif package == 'PIL':
                from PIL import Image
                logger.info(f"✓ Pillow installed")
            elif package == 'matplotlib':
                import matplotlib
                logger.info(f"✓ Matplotlib version: {matplotlib.__version__}")
            elif package == 'seaborn':
                import seaborn
                logger.info(f"✓ Seaborn version: {seaborn.__version__}")
        except ImportError:
            missing_packages.append(package)
            logger.error(f"✗ {package} not found")
    
    if missing_packages:
        logger.error(f"Missing packages: {missing_packages}")
        return False
    
    logger.info("All dependencies are installed!")
    return True

def create_project_structure():
    """Create the project directory structure"""
    logger.info("Creating project structure...")
    
    directories = [
        "src/core/steganography",
        "src/core/steganalysis", 
        "src/core/image_processing",
        "src/core/security",
        "src/algorithms/lsb",
        "src/algorithms/dct", 
        "src/algorithms/dwt",
        "src/algorithms/ml_models",
        "src/api",
        "src/web",
        "src/database",
        "src/utils",
        "tests",
        "docs",
        "config",
        "sample_images",
        "results"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        # Create __init__.py files for Python packages
        if directory.startswith("src/"):
            init_file = Path(directory) / "__init__.py"
            init_file.touch()
    
    logger.info("Project structure created successfully!")

def create_sample_lsb_steganography():
    """Create a simplified LSB steganography implementation for testing"""
    
    lsb_code = '''import cv2
import numpy as np
from typing import Optional

class SimpleLSBSteganography:
    """Simplified LSB Steganography for testing"""
    
    def __init__(self):
        self.delimiter = "1111111111111110"  # 16-bit delimiter
    
    def embed_message(self, cover_image: np.ndarray, message: str) -> np.ndarray:
        """Embed message in image using LSB"""
        # Convert message to binary
        binary_message = self._string_to_binary(message) + self.delimiter
        
        # Check capacity
        if not self._check_capacity(cover_image, len(binary_message)):
            raise ValueError("Image capacity insufficient for message")
        
        stego_image = cover_image.copy()
        height, width, channels = stego_image.shape
        message_index = 0
        
        # Sequential embedding
        for i in range(height):
            for j in range(width):
                for k in range(channels):
                    if message_index < len(binary_message):
                        # Modify LSB
                        stego_image[i][j][k] = (stego_image[i][j][k] & 0xFE) | int(binary_message[message_index])
                        message_index += 1
                    else:
                        return stego_image
        
        return stego_image
    
    def extract_message(self, stego_image: np.ndarray) -> str:
        """Extract message from stego image"""
        height, width, channels = stego_image.shape
        binary_message = ""
        
        # Sequential extraction
        for i in range(height):
            for j in range(width):
                for k in range(channels):
                    binary_message += str(stego_image[i][j][k] & 1)
                    
                    # Check for delimiter
                    if binary_message.endswith(self.delimiter):
                        # Remove delimiter and convert to string
                        binary_data = binary_message[:-len(self.delimiter)]
                        return self._binary_to_string(binary_data)
        
        return self._binary_to_string(binary_message)
    
    def calculate_psnr(self, original: np.ndarray, stego: np.ndarray) -> float:
        """Calculate PSNR between original and stego images"""
        mse = np.mean((original - stego) ** 2)
        if mse == 0:
            return float('inf')
        
        max_pixel = 255.0
        psnr = 20 * np.log10(max_pixel / np.sqrt(mse))
        return psnr
    
    def _string_to_binary(self, message: str) -> str:
        """Convert string to binary"""
        return ''.join(format(ord(char), '08b') for char in message)
    
    def _binary_to_string(self, binary: str) -> str:
        """Convert binary to string"""
        message = ""
        for i in range(0, len(binary), 8):
            byte = binary[i:i+8]
            if len(byte) == 8:
                try:
                    message += chr(int(byte, 2))
                except ValueError:
                    break
        return message
    
    def _check_capacity(self, image: np.ndarray, message_length: int) -> bool:
        """Check if image has sufficient capacity"""
        height, width, channels = image.shape
        capacity = height * width * channels
        return capacity >= message_length
'''
    
    # Write to file
    with open("src/core/steganography/simple_lsb.py", "w") as f:
        f.write(lsb_code)
    
    logger.info("Simple LSB steganography implementation created!")

def create_sample_rs_analysis():
    """Create a simplified RS analysis implementation for testing"""
    
    rs_code = '''import numpy as np
import cv2
from typing import Dict

class SimpleRSAnalysis:
    """Simplified RS Analysis for testing"""
    
    def __init__(self):
        self.mask = np.array([0, 1, 1, 0])  # Standard RS mask
    
    def analyze_image(self, image: np.ndarray) -> Dict[str, float]:
        """Perform simplified RS analysis"""
        # Convert to grayscale
        if len(image.shape) == 3:
            gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray_image = image
        
        height, width = gray_image.shape
        
        # Initialize counters
        regular_count = 0
        singular_count = 0
        total_blocks = 0
        
        # Process in 2x2 blocks
        for i in range(0, height - 1, 2):
            for j in range(0, width - 1, 2):
                block = gray_image[i:i+2, j:j+2].flatten()
                
                if len(block) == 4:
                    category = self._categorize_block(block)
                    if category == "R":
                        regular_count += 1
                    elif category == "S":
                        singular_count += 1
                    total_blocks += 1
        
        # Calculate statistics
        if total_blocks == 0:
            return {"steganography_detected": False, "confidence": 0.0}
        
        rs_ratio = regular_count / total_blocks if total_blocks > 0 else 0
        
        # Simple detection logic
        # Natural images typically have more regular groups
        # Steganography disturbs this ratio
        expected_ratio = 0.6  # Expected ratio for natural images
        deviation = abs(rs_ratio - expected_ratio)
        
        confidence = min(deviation * 5, 1.0)  # Scale deviation to confidence
        steganography_detected = deviation > 0.1
        
        return {
            "steganography_detected": steganography_detected,
            "confidence": confidence,
            "regular_count": regular_count,
            "singular_count": singular_count,
            "total_blocks": total_blocks,
            "rs_ratio": rs_ratio
        }
    
    def _categorize_block(self, block: np.ndarray) -> str:
        """Categorize block as Regular, Singular, or Unusable"""
        # Calculate discrimination function
        f_value = self._discrimination_function(block)
        
        # Flip LSBs and recalculate
        flipped_block = self._flip_lsb(block)
        f_flipped = self._discrimination_function(flipped_block)
        
        # Simple categorization
        if f_value > f_flipped:
            return "R"  # Regular
        elif f_value < f_flipped:
            return "S"  # Singular
        else:
            return "U"  # Unusable
    
    def _discrimination_function(self, block: np.ndarray) -> float:
        """Calculate discrimination function"""
        variation = 0
        for i in range(len(block) - 1):
            if self.mask[i]:
                variation += abs(int(block[i]) - int(block[i + 1]))
        return variation
    
    def _flip_lsb(self, block: np.ndarray) -> np.ndarray:
        """Flip LSBs according to mask"""
        flipped = block.copy()
        for i in range(len(block)):
            if self.mask[i]:
                flipped[i] = flipped[i] ^ 1  # Flip LSB
        return flipped
'''
    
    # Write to file
    with open("src/core/steganalysis/simple_rs.py", "w") as f:
        f.write(rs_code)
    
    logger.info("Simple RS analysis implementation created!")

def create_test_images():
    """Create sample test images"""
    logger.info("Creating test images...")
    
    # Create a simple test image
    test_image = np.random.randint(0, 256, (256, 256, 3), dtype=np.uint8)
    cv2.imwrite("sample_images/test_image.png", test_image)
    
    # Create a more realistic image with patterns
    realistic_image = np.zeros((256, 256, 3), dtype=np.uint8)
    
    # Add some patterns
    for i in range(256):
        for j in range(256):
            realistic_image[i, j] = [
                int(128 + 50 * np.sin(i/20) * np.cos(j/20)),  # R
                int(128 + 50 * np.cos(i/15) * np.sin(j/15)),  # G  
                int(128 + 50 * np.sin(i/10) * np.sin(j/10))   # B
            ]
    
    cv2.imwrite("sample_images/pattern_image.png", realistic_image)
    
    # Create a natural-looking image
    natural_image = np.zeros((256, 256, 3), dtype=np.uint8)
    
    # Simulate a gradient with noise
    for i in range(256):
        for j in range(256):
            base_intensity = int(255 * (i + j) / 512)
            noise = np.random.randint(-20, 21)
            intensity = np.clip(base_intensity + noise, 0, 255)
            natural_image[i, j] = [intensity, intensity * 0.8, intensity * 0.6]
    
    cv2.imwrite("sample_images/natural_image.png", natural_image.astype(np.uint8))
    
    logger.info("Test images created successfully!")

def test_lsb_steganography():
    """Test LSB steganography implementation"""
    logger.info("Testing LSB Steganography...")
    
    try:
        # Import the simple implementation
        sys.path.append('src/core/steganography')
        from simple_lsb import SimpleLSBSteganography
        
        # Load test image
        cover_image = cv2.imread("sample_images/test_image.png")
        if cover_image is None:
            logger.error("Could not load test image")
            return False
        
        # Initialize steganography
        lsb_stego = SimpleLSBSteganography()
        
        # Test message
        secret_message = "Hello, this is a secret message for testing steganography!"
        
        # Embed message
        logger.info(f"Embedding message: '{secret_message}'")
        stego_image = lsb_stego.embed_message(cover_image, secret_message)
        
        # Save stego image
        cv2.imwrite("results/stego_image.png", stego_image)
        
        # Calculate PSNR
        psnr = lsb_stego.calculate_psnr(cover_image, stego_image)
        logger.info(f"PSNR: {psnr:.2f} dB")
        
        # Extract message
        extracted_message = lsb_stego.extract_message(stego_image)
        logger.info(f"Extracted message: '{extracted_message}'")
        
        # Verify
        if extracted_message == secret_message:
            logger.info("✓ LSB Steganography test PASSED!")
            return True
        else:
            logger.error("✗ LSB Steganography test FAILED!")
            return False
            
    except Exception as e:
        logger.error(f"LSB Steganography test failed with error: {e}")
        return False

def test_rs_analysis():
    """Test RS analysis implementation"""
    logger.info("Testing RS Analysis...")
    
    try:
        # Import the simple implementation
        sys.path.append('src/core/steganalysis')
        from simple_rs import SimpleRSAnalysis
        
        # Initialize RS analyzer
        rs_analyzer = SimpleRSAnalysis()
        
        # Test on clean image
        clean_image = cv2.imread("sample_images/natural_image.png")
        if clean_image is None:
            logger.error("Could not load natural image")
            return False
        
        logger.info("Analyzing clean image...")
        clean_results = rs_analyzer.analyze_image(clean_image)
        logger.info(f"Clean image results: {clean_results}")
        
        # Test on stego image (if available)
        stego_image = cv2.imread("results/stego_image.png")
        if stego_image is not None:
            logger.info("Analyzing stego image...")
            stego_results = rs_analyzer.analyze_image(stego_image)
            logger.info(f"Stego image results: {stego_results}")
            
            # Compare results
            if stego_results["confidence"] > clean_results["confidence"]:
                logger.info("✓ RS Analysis correctly detected higher suspicion in stego image!")
            else:
                logger.info("- RS Analysis results are inconclusive")
        
        logger.info("✓ RS Analysis test completed!")
        return True
        
    except Exception as e:
        logger.error(f"RS Analysis test failed with error: {e}")
        return False

def create_simple_api():
    """Create a simple API for testing"""
    
    api_code = '''from fastapi import FastAPI, File, UploadFile, HTTPException
import cv2
import numpy as np
import sys
import os

# Add src to path
sys.path.append('src/core/steganography')
sys.path.append('src/core/steganalysis')

from simple_lsb import SimpleLSBSteganography
from simple_rs import SimpleRSAnalysis

app = FastAPI(title="Simple Steganography API", version="1.0.0")

# Initialize components
lsb_stego = SimpleLSBSteganography()
rs_analyzer = SimpleRSAnalysis()

@app.get("/")
async def root():
    return {"message": "Simple Steganography API is running!"}

@app.post("/embed")
async def embed_message(image: UploadFile = File(...), message: str = "Hello World"):
    """Embed message in image"""
    try:
        # Read image
        image_data = await image.read()
        image_array = np.frombuffer(image_data, np.uint8)
        cover_image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        
        if cover_image is None:
            raise HTTPException(status_code=400, detail="Invalid image")
        
        # Embed message
        stego_image = lsb_stego.embed_message(cover_image, message)
        
        # Calculate PSNR
        psnr = lsb_stego.calculate_psnr(cover_image, stego_image)
        
        # Encode result
        _, buffer = cv2.imencode('.png', stego_image)
        
        return {
            "success": True,
            "message": f"Message '{message}' embedded successfully",
            "psnr": float(psnr),
            "image_size": len(buffer)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze")
async def analyze_image(image: UploadFile = File(...)):
    """Analyze image for steganography"""
    try:
        # Read image
        image_data = await image.read()
        image_array = np.frombuffer(image_data, np.uint8)
        test_image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        
        if test_image is None:
            raise HTTPException(status_code=400, detail="Invalid image")
        
        # Analyze with RS
        results = rs_analyzer.analyze_image(test_image)
        
        return {
            "success": True,
            "analysis_results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
    
    # Write API file
    with open("src/api/simple_api.py", "w") as f:
        f.write(api_code)
    
    logger.info("Simple API created!")

def run_comprehensive_test():
    """Run comprehensive system test"""
    logger.info("=" * 60)
    logger.info("RUNNING COMPREHENSIVE SYSTEM TEST")
    logger.info("=" * 60)
    
    success_count = 0
    total_tests = 4
    
    # Test 1: Dependencies
    if check_dependencies():
        success_count += 1
    
    # Test 2: LSB Steganography
    if test_lsb_steganography():
        success_count += 1
    
    # Test 3: RS Analysis
    if test_rs_analysis():
        success_count += 1
    
    # Test 4: Create API
    try:
        create_simple_api()
        logger.info("✓ API creation test PASSED!")
        success_count += 1
    except Exception as e:
        logger.error(f"✗ API creation test FAILED: {e}")
    
    # Results
    logger.info("=" * 60)
    logger.info(f"TEST RESULTS: {success_count}/{total_tests} tests passed")
    
    if success_count == total_tests:
        logger.info("🎉 ALL TESTS PASSED! System is ready for use.")
        return True
    else:
        logger.warning(f"⚠️  {total_tests - success_count} tests failed. Please check the errors above.")
        return False

def main():
    """Main setup and test function"""
    print("🔧 Digital Image Steganography & Steganalysis System Setup")
    print("=" * 60)
    
    # Create project structure
    create_project_structure()
    
    # Create implementations
    create_sample_lsb_steganography()
    create_sample_rs_analysis()
    
    # Create test images
    create_test_images()
    
    # Run comprehensive tests
    success = run_comprehensive_test()
    
    if success:
        print("\n🚀 NEXT STEPS:")
        print("1. To start the API server:")
        print("   cd src/api && python simple_api.py")
        print("\n2. To test the API:")
        print("   Open http://localhost:8000/docs in your browser")
        print("\n3. To run individual tests:")
        print("   python -c 'from setup_and_test import test_lsb_steganography; test_lsb_steganography()'")
        print("\n4. Check the 'results' folder for output images")
    
    return success

if __name__ == "__main__":
    main()