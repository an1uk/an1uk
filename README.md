# Flask eBay Clothes Reselling Manager

A **Flask-based web application** designed to manage and streamline the process of listing used clothing items on eBay. 

This project aims to automate as much of the workflow as possible, offering a practical, customisable solution for online resellers.

---

## Project Goals

- **Automation:** Minimise manual effort in creating eBay listings.
- **Integration:** Serve as a central hub for managing product images, SKUs, and listing details.
- **Expandability:** Build with future cross-listing and new feature support in mind.

---

## Workflow Overview

1. **Source & Prepare Item**
   - Acquire and prepare the clothing item for resale.
2. **Photography**
   - Take item photographs, ideally in a 1:1 aspect ratio.
   - The first few images should fully frame the item (for background removal).
3. **SKU Labelling**
   - Final photo includes the item with a QR code label.
   - *Note: A separate local script (not included here) generates and prints these QR code labels for items and storage locations (boxes/shelves).*
4. **Image Processing**  
   *Handled by a separate local script (not included in this repository):*
   - Renames images to a SKU-based format recognised by this system.
   - Validates image quality (e.g. sharpness, exposure).
   - Removes backgrounds on initial images.
   - Applies dynamic sharpening and vibrance adjustments for better listing appeal.
   - Resizes images optimally for eBay's requirements and S3 storage efficiency.
   - Uploads processed images to Amazon S3.
5. **Automated Management (this system):**
   - Reads the S3 file tree to detect new SKUs.
   - Displays the first image of each SKU for quick review and eBay category assignment (future: potential AI-powered category suggestions).
   - Presents a dashboard of eBay categories sorted by item count.
   - Category pages allow for detailed data entry, including auto-fetched item specifics from the eBay API (with local caching to minimise redundant calls).
   - Future: Enhanced tools for price research—integrated Google Image searches, sell-through rate calculations, and research links to inform pricing decisions.
   - Once all required data is entered, items can be listed or scheduled on eBay.
   - (See [Roadmap](#planned-features--roadmap) below for future plans.)

---

## Current Features

**This project is a work in progress. Current implemented features include:**

- **SKU Detection:**  
  Automatically detects SKUs from product image file trees uploaded to Amazon S3.

- **Category Assignment:**  
  Allows users to categorise each SKU by reviewing its first image and selecting the correct eBay category.

---

## Planned Features / Roadmap

Planned enhancements include:

- **eBay Integration:**  
  Complete API integration for seamless listing and management.
- **Cross-listing:**  
  Expand support to other marketplaces (e.g. Vinted, Depop, Vestiaire Collective).
- **Bulk Processing:**  
  Improved tools for handling large volumes of listings.
- **Advanced Image Recognition:**  
  Incorporate AI for category suggestions and item attribute recognition.
- **Analytics & Reporting:**  
  Monitor listing activity and sales performance.

---

## Project Status

**Active development** – SKU/image management and categorisation are currently supported.  
eBay API integration is in progress.  
Additional automation and marketplace support are planned for future releases.

---

## Contributing

Contributions, feature requests, and suggestions are welcome!  
Please open an issue or submit a pull request.