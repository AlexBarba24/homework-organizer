# Try to import cv2, but make it optional
try:
	import cv2
	HAS_OPENCV = True
except ImportError:
	HAS_OPENCV = False

import numpy as np
from pdf2image import convert_from_path
import pytesseract
from PIL import Image
import chatGPT
import os
import sys
import json
from PyPDF2 import PdfReader

# Assuming Tesseract OCR is already installed
# If not, install it using: !apt install tesseract-ocr
def parse(pdf_path):
	# Check for GPU availability for OpenCV (only if available)
	use_gpu = False
	if HAS_OPENCV:
		try:
			use_gpu = cv2.cuda.getCudaEnabledDeviceCount() > 0
		except:
			use_gpu = False

	# Create directories for saving output
	os.makedirs('./content/batch_texts', exist_ok=True)
	os.makedirs('./content/batch_images', exist_ok=True)

	# Get total number of pages dynamically
	try:
		reader = PdfReader(pdf_path)
		total_pages = len(reader.pages)
	except Exception as e:
		# Fallback: try to get page count from pdf2image
		try:
			from pdf2image import pdfinfo_from_path
			info = pdfinfo_from_path(pdf_path)
			total_pages = info['Pages']
		except:
			total_pages = 20  # Default fallback

	# Function to preprocess an image (OpenCV if available, otherwise PIL)
	def preprocess_image(image):
		if HAS_OPENCV:
			# Use OpenCV for preprocessing if available
			try:
				image_cv = np.array(image)
				if use_gpu:
					# Upload image to GPU
					image_gpu = cv2.cuda_GpuMat(image_cv)
					# Convert to grayscale
					gray_gpu = cv2.cuda.cvtColor(image_gpu, cv2.COLOR_BGR2GRAY)
					# Download image from GPU to CPU
					image_cv = gray_gpu.download()
				else:
					# Convert to grayscale
					image_cv = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)
				return Image.fromarray(image_cv)
			except Exception as e:
				# If OpenCV fails, fallback to PIL
				print(f"Warning: OpenCV preprocessing failed, using PIL fallback: {e}", file=sys.stderr)
				return image.convert('L')
		else:
			# Fallback to PIL grayscale conversion (no OpenCV)
			return image.convert('L')

	# Collect all OCR text from all pages
	all_text = ""

	# Define the size of each batch
	batch_size = 10  # Process 10 pages at a time, adjust based on your environment's capability

	# Calculate the number of batches needed
	batches = (total_pages + batch_size - 1) // batch_size

	# Process each batch
	for batch in range(batches):
		start_page = batch * batch_size + 1
		end_page = min(start_page + batch_size - 1, total_pages)
		
		# Convert a range of pages to images
		images = convert_from_path(pdf_path, first_page=start_page, last_page=end_page, dpi=200)

		# Perform OCR on each image after preprocessing
		for i, image in enumerate(images):
			# Preprocess the image
			image = preprocess_image(image)

			# Perform OCR using pytesseract
			text = pytesseract.image_to_string(image)
			all_text += text + "\n"

			# Save the image (optional, for debugging)
			image_file_path = f'./content/batch_images/batch_{batch}_page_{start_page + i}.png'
			image.save(image_file_path)

		# Clear the images list to free up memory
		del images

	# Parse all collected text with ChatGPT
	all_assignments = []
	assignments = chatGPT.parse_pdf(all_text)
	if assignments:
		all_assignments.extend(assignments)

	return all_assignments

if __name__ == '__main__':
	# Get PDF path from command line argument or use default
	pdf_path = sys.argv[1] if len(sys.argv) > 1 else './parse.pdf'
	
	try:
		assignments = parse(pdf_path)
		# Output JSON to stdout for Electron to capture
		print(json.dumps(assignments))
	except Exception as e:
		# Output error as JSON
		print(json.dumps({'error': str(e)}), file=sys.stderr)
		sys.exit(1)
