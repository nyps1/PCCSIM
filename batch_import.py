import os
import sys
import glob
import shutil
from pathlib import Path
from werkzeug.datastructures import FileStorage
from app import app, pccim_service
from services.ppt_importer import ppt_importer
from utils.file_helper import FileHelper
from models.attachment import Attachment

def run_batch_import():
    print("=" * 50)
    print(" PCCSIM Batch PPT Importer ")
    print("=" * 50)
    
    # Get folder path from user
    folder_path = input("\nPlease enter the full path to the folder containing PPT files:\n> ").strip()
    
    # Remove quotes if user dragged and dropped folder in terminal
    folder_path = folder_path.strip('"\'')
    
    if not os.path.isdir(folder_path):
        print(f"\n[Error] The directory '{folder_path}' does not exist.")
        sys.exit(1)
        
    print(f"\nScanning directory: {folder_path} ...")
    
    # Find all .ppt and .pptx files
    search_pattern_pptx = os.path.join(folder_path, "*.pptx")
    search_pattern_ppt = os.path.join(folder_path, "*.ppt")
    files = glob.glob(search_pattern_pptx) + glob.glob(search_pattern_ppt)
    
    if not files:
        print("No .ppt or .pptx files found in this directory.")
        sys.exit(0)
        
    print(f"Found {len(files)} file(s) to process.\n")
    
    processed_dir = os.path.join(folder_path, "processed")
    os.makedirs(processed_dir, exist_ok=True)
    
    success_count = 0
    error_count = 0
    
    # We must run within app context because of database config and upload paths
    with app.app_context():
        for file_path in files:
            filename = os.path.basename(file_path)
            print(f"Processing: {filename} ... ", end="")
            
            try:
                # Mock a FileStorage object for ppt_importer
                with open(file_path, "rb") as f:
                    file_storage = FileStorage(stream=f, filename=filename, content_type="application/vnd.openxmlformats-officedocument.presentationml.presentation")
                    
                    request_no = pccim_service.generate_request_no()
                    apply_date = pccim_service.get_today()
                    
                    application, attachments = ppt_importer.import_ppt(file_storage, request_no, apply_date)
                    
                    # Create application in DB
                    pccim_service.create_application(application)
                    
                    # Create attachments in DB
                    for att in attachments:
                        pccim_service.add_attachment(att)
                        
                    # Save the uploaded PPT itself as an attachment
                    f.seek(0)
                    saved_filename = FileHelper.save_attachment(
                        file=file_storage,
                        request_no=request_no,
                        section_name="content_ppt",
                        attachment_no=1,
                    )
                    
                    ppt_attachment = Attachment(
                        request_no=request_no,
                        section_name="content_ppt",
                        attachment_no=1,
                        file_path=saved_filename,
                        original_file_name=filename,
                        file_type=FileHelper.get_extension(filename),
                        remark="Uploaded content PPT (Batch Import)",
                    )
                    pccim_service.add_attachment(ppt_attachment)
                        
                print("SUCCESS")
                success_count += 1
                
                # Move to processed
                dest_path = os.path.join(processed_dir, filename)
                # Ensure we don't overwrite if one already exists with the same name, or we can just replace
                if os.path.exists(dest_path):
                    os.remove(dest_path)
                shutil.move(file_path, processed_dir)
                
            except Exception as e:
                print("FAILED")
                print(f"   └─ Error: {e}")
                error_count += 1
                
    print("\n" + "=" * 50)
    print(" Import Summary ")
    print("=" * 50)
    print(f"Total Files Processed: {len(files)}")
    print(f"Successful: {success_count}")
    print(f"Failed: {error_count}")
    print("=" * 50)

if __name__ == "__main__":
    run_batch_import()
