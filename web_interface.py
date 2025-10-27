#!/usr/bin/env python3
"""
Web Interface for Digital Image Steganography and Steganalysis System
FastAPI-based web application with modern UI
"""

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
import shutil
from pathlib import Path
import cv2
import numpy as np
from steganography_core import SteganographyCore, SteganalysisCore
import tempfile
import base64
from typing import Optional

# Initialize FastAPI app
app = FastAPI(
    title="Digital Image Steganography & Steganalysis System",
    description="Advanced steganography system for forensic analysis",
    version="1.0.0"
)

# Initialize cores
stego_core = SteganographyCore()
steganalysis_core = SteganalysisCore()

# Create upload directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def home():
    """Serve the main web interface"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Digital Image Steganography & Steganalysis System</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: rgba(255, 255, 255, 0.95);
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
                overflow: hidden;
            }
            
            .header {
                background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }
            
            .header h1 {
                font-size: 2.5em;
                margin-bottom: 10px;
            }
            
            .header p {
                font-size: 1.2em;
                opacity: 0.9;
            }
            
            .content {
                padding: 40px;
            }
            
            .tabs {
                display: flex;
                border-bottom: 2px solid #ecf0f1;
                margin-bottom: 30px;
            }
            
            .tab {
                padding: 15px 30px;
                background: #ecf0f1;
                border: none;
                cursor: pointer;
                font-size: 16px;
                font-weight: 600;
                transition: all 0.3s;
                flex: 1;
            }
            
            .tab.active {
                background: #3498db;
                color: white;
            }
            
            .tab:hover {
                background: #2980b9;
                color: white;
            }
            
            .tab-content {
                display: none;
            }
            
            .tab-content.active {
                display: block;
            }
            
            .form-group {
                margin-bottom: 25px;
            }
            
            .form-group label {
                display: block;
                margin-bottom: 8px;
                font-weight: 600;
                color: #2c3e50;
            }
            
            .form-group input,
            .form-group textarea {
                width: 100%;
                padding: 12px;
                border: 2px solid #ddd;
                border-radius: 8px;
                font-size: 16px;
                transition: border-color 0.3s;
            }
            
            .form-group input:focus,
            .form-group textarea:focus {
                outline: none;
                border-color: #3498db;
            }
            
            .file-input {
                position: relative;
                display: inline-block;
                cursor: pointer;
                width: 100%;
            }
            
            .file-input input[type="file"] {
                position: absolute;
                opacity: 0;
                width: 100%;
                height: 100%;
                cursor: pointer;
            }
            
            .file-input-label {
                display: block;
                padding: 20px;
                border: 2px dashed #3498db;
                border-radius: 8px;
                text-align: center;
                background: #ecf8ff;
                transition: all 0.3s;
            }
            
            .file-input:hover .file-input-label {
                background: #dbeafe;
                border-color: #2563eb;
            }
            
            .btn {
                background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
                color: white;
                padding: 15px 30px;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s;
                width: 100%;
            }
            
            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 20px rgba(52, 152, 219, 0.3);
            }
            
            .btn-success {
                background: linear-gradient(135deg, #27ae60 0%, #229954 100%);
            }
            
            .btn-warning {
                background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
            }
            
            .result {
                margin-top: 30px;
                padding: 20px;
                border-radius: 8px;
                display: none;
            }
            
            .result.success {
                background: #d4edda;
                border: 1px solid #c3e6cb;
                color: #155724;
            }
            
            .result.error {
                background: #f8d7da;
                border: 1px solid #f5c6cb;
                color: #721c24;
            }
            
            .result.info {
                background: #cce7ff;
                border: 1px solid #99d3ff;
                color: #0066cc;
            }
            
            .grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 30px;
                margin-top: 30px;
            }
            
            .card {
                background: white;
                padding: 25px;
                border-radius: 12px;
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
                border: 1px solid #ecf0f1;
            }
            
            .card h3 {
                color: #2c3e50;
                margin-bottom: 15px;
                font-size: 1.3em;
            }
            
            .loading {
                display: none;
                text-align: center;
                padding: 20px;
            }
            
            .spinner {
                border: 4px solid #f3f3f3;
                border-top: 4px solid #3498db;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 0 auto 15px;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            .image-preview {
                max-width: 100%;
                height: auto;
                border-radius: 8px;
                margin-top: 15px;
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔐 Digital Image Steganography & Steganalysis System</h1>
                <p>Advanced forensic analysis and secure communication platform</p>
            </div>
            
            <div class="content">
                <div class="tabs">
                    <button class="tab active" onclick="showTab('embed')">🔒 Embed Message</button>
                    <button class="tab" onclick="showTab('extract')">🔓 Extract Message</button>
                    <button class="tab" onclick="showTab('analyze')">🔍 Steganalysis</button>
                    <button class="tab" onclick="showTab('about')">ℹ️ About</button>
                </div>
                
                <!-- Embed Tab -->
                <div id="embed" class="tab-content active">
                    <div class="grid">
                        <div class="card">
                            <h3>📸 Upload Cover Image</h3>
                            <form id="embedForm" enctype="multipart/form-data">
                                <div class="form-group">
                                    <label>Select Image:</label>
                                    <div class="file-input">
                                        <input type="file" id="coverImage" name="image" accept="image/*" required>
                                        <label for="coverImage" class="file-input-label">
                                            📁 Click to select or drag image here<br>
                                            <small>Supports PNG, BMP, TIFF formats</small>
                                        </label>
                                    </div>
                                </div>
                                
                                <div class="form-group">
                                    <label for="secretMessage">Secret Message:</label>
                                    <textarea id="secretMessage" name="message" rows="4" placeholder="Enter your secret message here..." required></textarea>
                                </div>
                                
                                <button type="submit" class="btn">🔒 Embed Message</button>
                            </form>
                            
                            <div class="loading" id="embedLoading">
                                <div class="spinner"></div>
                                <p>Embedding message into image...</p>
                            </div>
                            
                            <div id="embedResult" class="result"></div>
                        </div>
                        
                        <div class="card">
                            <h3>🖼️ Image Preview</h3>
                            <div id="imagePreview">
                                <p style="text-align: center; color: #7f8c8d; padding: 40px;">
                                    Select an image to see preview
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Extract Tab -->
                <div id="extract" class="tab-content">
                    <div class="card">
                        <h3>🔓 Extract Hidden Message</h3>
                        <form id="extractForm" enctype="multipart/form-data">
                            <div class="form-group">
                                <label>Select Stego Image:</label>
                                <div class="file-input">
                                    <input type="file" id="stegoImage" name="image" accept="image/*" required>
                                    <label for="stegoImage" class="file-input-label">
                                        📁 Click to select stego image<br>
                                        <small>Image containing hidden message</small>
                                    </label>
                                </div>
                            </div>
                            
                            <button type="submit" class="btn btn-success">🔓 Extract Message</button>
                        </form>
                        
                        <div class="loading" id="extractLoading">
                            <div class="spinner"></div>
                            <p>Extracting hidden message...</p>
                        </div>
                        
                        <div id="extractResult" class="result"></div>
                    </div>
                </div>
                
                <!-- Analyze Tab -->
                <div id="analyze" class="tab-content">
                    <div class="card">
                        <h3>🔍 Steganalysis - Hidden Content Detection</h3>
                        <form id="analyzeForm" enctype="multipart/form-data">
                            <div class="form-group">
                                <label>Select Image to Analyze:</label>
                                <div class="file-input">
                                    <input type="file" id="analyzeImage" name="image" accept="image/*" required>
                                    <label for="analyzeImage" class="file-input-label">
                                        📁 Click to select image for analysis<br>
                                        <small>Detect potential steganographic content</small>
                                    </label>
                                </div>
                            </div>
                            
                            <button type="submit" class="btn btn-warning">🔍 Analyze Image</button>
                        </form>
                        
                        <div class="loading" id="analyzeLoading">
                            <div class="spinner"></div>
                            <p>Performing steganalysis...</p>
                        </div>
                        
                        <div id="analyzeResult" class="result"></div>
                    </div>
                </div>
                
                <!-- About Tab -->
                <div id="about" class="tab-content">
                    <div class="grid">
                        <div class="card">
                            <h3>📋 System Overview</h3>
                            <p><strong>Digital Image Steganography and Steganalysis System</strong></p>
                            <p>Advanced forensic analysis platform based on research findings.</p>
                            <br>
                            <h4>Features:</h4>
                            <ul style="padding-left: 20px; line-height: 1.8;">
                                <li>🔒 LSB Steganography</li>
                                <li>🔓 Message Extraction</li>
                                <li>🔍 Chi-Square Detection</li>
                                <li>📊 Histogram Analysis</li>
                                <li>🛡️ Forensic Integrity</li>
                                <li>📈 Statistical Analysis</li>
                            </ul>
                        </div>
                        
                        <div class="card">
                            <h3>⚙️ Technical Details</h3>
                            <p><strong>Algorithms Implemented:</strong></p>
                            <ul style="padding-left: 20px; line-height: 1.8;">
                                <li>Least Significant Bit (LSB)</li>
                                <li>Chi-Square Test</li>
                                <li>Histogram Analysis</li>
                                <li>Statistical Detection</li>
                            </ul>
                            <br>
                            <p><strong>Supported Formats:</strong></p>
                            <ul style="padding-left: 20px; line-height: 1.8;">
                                <li>PNG (Recommended)</li>
                                <li>BMP (Lossless)</li>
                                <li>TIFF (High Quality)</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            function showTab(tabName) {
                // Hide all tab contents
                const contents = document.querySelectorAll('.tab-content');
                contents.forEach(content => content.classList.remove('active'));
                
                // Remove active class from all tabs
                const tabs = document.querySelectorAll('.tab');
                tabs.forEach(tab => tab.classList.remove('active'));
                
                // Show selected tab content
                document.getElementById(tabName).classList.add('active');
                
                // Add active class to clicked tab
                event.target.classList.add('active');
            }
            
            // Image preview functionality
            document.getElementById('coverImage').addEventListener('change', function(e) {
                const file = e.target.files[0];
                if (file) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        document.getElementById('imagePreview').innerHTML = 
                            `<img src="${e.target.result}" class="image-preview" alt="Cover Image Preview">`;
                    };
                    reader.readAsDataURL(file);
                }
            });
            
            // Form handlers
            document.getElementById('embedForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const loading = document.getElementById('embedLoading');
                const result = document.getElementById('embedResult');
                
                loading.style.display = 'block';
                result.style.display = 'none';
                
                const formData = new FormData(this);
                
                try {
                    const response = await fetch('/embed', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const data = await response.json();
                    
                    loading.style.display = 'none';
                    result.style.display = 'block';
                    
                    if (response.ok) {
                        result.className = 'result success';
                        result.innerHTML = `
                            <h4>✅ Message Embedded Successfully!</h4>
                            <p><strong>File:</strong> ${data.filename}</p>
                            <p><strong>Message Length:</strong> ${data.message_length} characters</p>
                            <p><strong>Capacity Used:</strong> ${data.capacity_used}%</p>
                            <a href="/download/${data.filename}" class="btn" style="margin-top: 15px; display: inline-block; text-decoration: none;">
                                📥 Download Stego Image
                            </a>
                        `;
                    } else {
                        result.className = 'result error';
                        result.innerHTML = `<h4>❌ Error:</h4><p>${data.detail}</p>`;
                    }
                } catch (error) {
                    loading.style.display = 'none';
                    result.style.display = 'block';
                    result.className = 'result error';
                    result.innerHTML = `<h4>❌ Network Error:</h4><p>${error.message}</p>`;
                }
            });
            
            document.getElementById('extractForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const loading = document.getElementById('extractLoading');
                const result = document.getElementById('extractResult');
                
                loading.style.display = 'block';
                result.style.display = 'none';
                
                const formData = new FormData(this);
                
                try {
                    const response = await fetch('/extract', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const data = await response.json();
                    
                    loading.style.display = 'none';
                    result.style.display = 'block';
                    
                    if (response.ok) {
                        result.className = 'result success';
                        result.innerHTML = `
                            <h4>🔓 Message Extracted Successfully!</h4>
                            <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin-top: 15px;">
                                <strong>Hidden Message:</strong><br>
                                <em>"${data.message}"</em>
                            </div>
                            <p style="margin-top: 15px;"><strong>Message Length:</strong> ${data.message.length} characters</p>
                        `;
                    } else {
                        result.className = 'result error';
                        result.innerHTML = `<h4>❌ Error:</h4><p>${data.detail}</p>`;
                    }
                } catch (error) {
                    loading.style.display = 'none';
                    result.style.display = 'block';
                    result.className = 'result error';
                    result.innerHTML = `<h4>❌ Network Error:</h4><p>${error.message}</p>`;
                }
            });
            
            document.getElementById('analyzeForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const loading = document.getElementById('analyzeLoading');
                const result = document.getElementById('analyzeResult');
                
                loading.style.display = 'block';
                result.style.display = 'none';
                
                const formData = new FormData(this);
                
                try {
                    const response = await fetch('/analyze', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const data = await response.json();
                    
                    loading.style.display = 'none';
                    result.style.display = 'block';
                    
                    if (response.ok) {
                        const chi = data.chi_square;
                        const hist = data.histogram;
                        
                        const suspiciousIcon = (chi.is_suspicious || hist.is_suspicious) ? '🚨' : '✅';
                        const suspiciousText = (chi.is_suspicious || hist.is_suspicious) ? 'SUSPICIOUS' : 'CLEAN';
                        
                        result.className = `result ${(chi.is_suspicious || hist.is_suspicious) ? 'error' : 'success'}`;
                        result.innerHTML = `
                            <h4>${suspiciousIcon} Steganalysis Results - ${suspiciousText}</h4>
                            
                            <div style="margin-top: 20px;">
                                <h5>📊 Chi-Square Test:</h5>
                                <p><strong>Suspicious:</strong> ${chi.is_suspicious ? '🚨 Yes' : '✅ No'}</p>
                                <p><strong>Chi-Square Value:</strong> ${chi.chi_square_value.toFixed(4)}</p>
                                <p><strong>Confidence:</strong> ${(chi.confidence * 100).toFixed(1)}%</p>
                            </div>
                            
                            <div style="margin-top: 20px;">
                                <h5>📈 Histogram Analysis:</h5>
                                <p><strong>Suspicious:</strong> ${hist.is_suspicious ? '🚨 Yes' : '✅ No'}</p>
                                <p><strong>Average Irregularity:</strong> ${hist.average_irregularity.toFixed(2)}</p>
                            </div>
                            
                            <div style="margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 5px;">
                                <strong>Analysis Summary:</strong><br>
                                ${(chi.is_suspicious || hist.is_suspicious) ? 
                                    'This image shows statistical anomalies that may indicate the presence of hidden content.' :
                                    'No significant statistical anomalies detected. Image appears clean.'}
                            </div>
                        `;
                    } else {
                        result.className = 'result error';
                        result.innerHTML = `<h4>❌ Error:</h4><p>${data.detail}</p>`;
                    }
                } catch (error) {
                    loading.style.display = 'none';
                    result.style.display = 'block';
                    result.className = 'result error';
                    result.innerHTML = `<h4>❌ Network Error:</h4><p>${error.message}</p>`;
                }
            });
        </script>
    </body>
    </html>
    """
    return html_content

@app.post("/embed")
async def embed_message(
    image: UploadFile = File(...),
    message: str = Form(...)
):
    """Embed secret message into image using LSB steganography"""
    try:
        # Validate file format
        if not image.filename.lower().endswith(('.png', '.bmp', '.tiff')):
            raise HTTPException(status_code=400, detail="Unsupported file format. Use PNG, BMP, or TIFF.")
        
        # Save uploaded file
        input_path = UPLOAD_DIR / f"cover_{image.filename}"
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        
        # Generate output filename
        output_filename = f"stego_{image.filename}"
        output_path = UPLOAD_DIR / output_filename
        
        # Embed message
        success = stego_core.lsb_embed(str(input_path), message, str(output_path))
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to embed message. Image may be too small.")
        
        # Calculate capacity used
        image_data = cv2.imread(str(input_path))
        max_capacity = image_data.shape[0] * image_data.shape[1] * 3
        capacity_used = (len(message) * 8 / max_capacity) * 100
        
        # Clean up input file
        os.remove(input_path)
        
        return {
            "success": True,
            "filename": output_filename,
            "message_length": len(message),
            "capacity_used": round(capacity_used, 2)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/extract")
async def extract_message(image: UploadFile = File(...)):
    """Extract hidden message from stego image"""
    try:
        # Save uploaded file
        input_path = UPLOAD_DIR / f"extract_{image.filename}"
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        
        # Extract message
        extracted_message = stego_core.lsb_extract(str(input_path))
        
        # Clean up
        os.remove(input_path)
        
        if extracted_message is None:
            raise HTTPException(status_code=400, detail="No hidden message found or extraction failed.")
        
        return {
            "success": True,
            "message": extracted_message
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze")
async def analyze_image(image: UploadFile = File(...)):
    """Perform steganalysis on uploaded image"""
    try:
        # Save uploaded file
        input_path = UPLOAD_DIR / f"analyze_{image.filename}"
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        
        # Perform analysis
        chi_result = steganalysis_core.chi_square_test(str(input_path))
        hist_result = steganalysis_core.histogram_analysis(str(input_path))
        
        # Clean up
        os.remove(input_path)
        
        return {
            "success": True,
            "chi_square": chi_result,
            "histogram": hist_result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download/{filename}")
async def download_file(filename: str):
    """Download generated stego image"""
    file_path = UPLOAD_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='application/octet-stream'
    )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "system": "Digital Image Steganography & Steganalysis",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    print("🚀 Starting Digital Image Steganography & Steganalysis Web Server...")
    print("📱 Web Interface: http://localhost:8000")
    print("📋 API Docs: http://localhost:8000/docs")
    print("🔧 System Status: http://localhost:8000/health")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")