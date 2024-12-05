#!/usr/bin/env python3
import fitz  # PyMuPDF
from PIL import Image
import io
import os
import argparse
from typing import List, Tuple
import tempfile

class PDFConverter:
    def __init__(self, dpi: int = 400):
        """
        Initialize the converter with specified DPI for image quality.
        
        Args:
            dpi: Dots per inch for PDF to image conversion (default: 300)
        """
        self.dpi = dpi
        # Calculate the scaling factor based on DPI
        self.zoom = self.dpi / 72  # 72 is the default PDF DPI
        # Create scaling matrix for PDF rendering
        self.matrix = fitz.Matrix(self.zoom, self.zoom)

    def pdf_to_images(self, pdf_path: str) -> List[Image.Image]:
        """
        Convert each page of a PDF to a PIL Image.
        
        Args:
            pdf_path: Path to the input PDF file
        
        Returns:
            List of PIL Image objects, one for each page
        """
        print("Converting PDF to images...")
        images = []
        pdf_document = fitz.open(pdf_path)
        
        for page_num in range(len(pdf_document)):
            print(f"Converting page {page_num + 1}/{len(pdf_document)} to image")
            page = pdf_document[page_num]
            
            # Convert page to pixmap (image)
            pix = page.get_pixmap(matrix=self.matrix, alpha=False)
            
            # Convert pixmap to PIL Image
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            images.append(img)
        
        pdf_document.close()
        return images

    def invert_image(self, image: Image.Image) -> Image.Image:
        """
        Invert the colors of an image while preserving color relationships.
        
        Args:
            image: PIL Image to process
        
        Returns:
            PIL Image with inverted colors
        """
        # Convert to RGB mode if not already
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Create an inverted version of the image
        inverted_image = Image.new('RGB', image.size)
        
        # Get image data
        data = image.getdata()
        inverted_data = []
        
        # Process each pixel
        for pixel in data:
            # Invert each RGB channel
            inverted_pixel = tuple(255 - value for value in pixel)
            inverted_data.append(inverted_pixel)
        
        inverted_image.putdata(inverted_data)
        return inverted_image

    def images_to_pdf(self, images: List[Image.Image], output_path: str) -> None:
        """
        Convert a list of images to a PDF file.
        
        Args:
            images: List of PIL Images to convert
            output_path: Path where the output PDF should be saved
        """
        print("\nCreating PDF from inverted images...")
        
        # Create a temporary directory to store intermediate files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save the first image as PDF
            first_image = images[0]
            pdf_path = os.path.join(temp_dir, "output.pdf")
            
            # Convert images to PDF pages
            first_image.save(
                pdf_path,
                "PDF",
                resolution=self.dpi,
                save_all=True,
                append_images=images[1:]
            )
            
            # Copy the temporary PDF to the final location
            with open(pdf_path, 'rb') as temp_pdf:
                with open(output_path, 'wb') as final_pdf:
                    final_pdf.write(temp_pdf.read())

    def convert_pdf_to_dark_mode(self, input_path: str, output_path: str) -> None:
        """
        Convert a PDF to dark mode using image conversion as an intermediate step.
        
        Args:
            input_path: Path to the input PDF file
            output_path: Path where the dark mode PDF should be saved
        """
        try:
            # Step 1: Convert PDF to images
            images = self.pdf_to_images(input_path)
            
            # Step 2: Invert colors of each image
            print("\nInverting colors...")
            inverted_images = []
            for i, image in enumerate(images, 1):
                print(f"Inverting colors for page {i}/{len(images)}")
                inverted_image = self.invert_image(image)
                inverted_images.append(inverted_image)
            
            # Step 3: Convert inverted images back to PDF
            self.images_to_pdf(inverted_images, output_path)
            
            print(f"\nDark mode PDF successfully created: {output_path}")
            
        except Exception as e:
            print(f"Error during conversion: {str(e)}")
            raise

def main():
    """
    Main function to handle command line arguments and process the PDF.
    """
    parser = argparse.ArgumentParser(description='Convert PDF to dark mode using image conversion')
    parser.add_argument('input_pdf', help='Path to input PDF file')
    parser.add_argument('--output', '-o', 
                       help='Path to output PDF file (default: input_darkmode.pdf)')
    parser.add_argument('--dpi', type=int, default=300,
                       help='DPI for image conversion (default: 300)')
    
    args = parser.parse_args()
    
    # Generate output path if not specified
    if not args.output:
        base, ext = os.path.splitext(args.input_pdf)
        args.output = f"{base}_darkmode{ext}"
    
    # Create converter and process the PDF
    converter = PDFConverter(dpi=args.dpi)
    
    try:
        converter.convert_pdf_to_dark_mode(args.input_pdf, args.output)
    except Exception as e:
        print(f"Error processing PDF: {e}")
        exit(1)

if __name__ == "__main__":
    main()