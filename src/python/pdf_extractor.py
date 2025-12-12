import cv2
import numpy as np
from pdf2image import convert_from_path
import pytesseract
from PIL import Image
from IPython.display import display  # To display images in Jupyter notebook/Colab
import chatGPT
import os

# Assuming Tesseract OCR is already installed
# If not, install it using: !apt install tesseract-ocr
def parse():
	# Check for GPU availability for OpenCV
	use_gpu = cv2.cuda.getCudaEnabledDeviceCount() > 0

	# Define the path to your PDF file
	pdf_path = './parse.pdf'  # Replace with the path to your PDF

	# Create directories for saving output
	os.makedirs('./content/batch_texts', exist_ok=True)
	os.makedirs('./content/batch_images', exist_ok=True)

	# Function to preprocess an image with OpenCV
	def preprocess_image(image):
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

	# Function to process a batch of pages as images
	def process_batch(start, end, batch_number):
		# Convert a range of pages to images
		images = convert_from_path(pdf_path, first_page=start, last_page=end, dpi=200)

		# Perform OCR on each image after preprocessing
		for i, image in enumerate(images):
			# Preprocess the image
			image = preprocess_image(image)

			# Perform OCR using pytesseract
			text = pytesseract.image_to_string(image)
			# print(text)
			chatGPT.parse_pdf(text)
			# Save the text in a file
			# text_file_path = f'./content/batch_texts/batch_{batch_number}_page_{start + i}.txt'
			# with open(text_file_path, 'w') as file:
			#     file.write(text)


			# Save the image
			image_file_path = f'./content/batch_images/batch_{batch_number}_page_{start + i}.png'
			image.save(image_file_path)

			# Display the image inline
			display(image)

		# Clear the images list to free up memory
		del images

	# Define the size of each batch
	batch_size = 10  # Process 10 pages at a time, adjust based on your environment's capability

	# Calculate the number of batches needed
	total_pages = 20  # Total number of pages in your PDF
	batches = (total_pages + batch_size - 1) // batch_size

	# Process each batch
	for batch in range(batches):
		start_page = batch * batch_size + 1
		end_page = min(start_page + batch_size - 1, total_pages)
		process_batch(start_page, end_page, batch)

parse()
