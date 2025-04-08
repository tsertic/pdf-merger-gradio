import os
import gradio as gr
from pypdf import PdfWriter


def merge_pdfs_ui(input_folder, output_folder, output_filename):
    """
    Function called by the Gradio interface for merging PDFs.
    Receives folder paths and output filename, returns a status message.
    """
    status_messages = []  # List for collecting messages to display to the user

    # --- 1. Input validation ---
    if not input_folder:
        return "Error: Please enter a path to the folder with PDF files."
    if not os.path.isdir(input_folder):
        return f"Error: Input folder '{input_folder}' not found or is not a valid folder."

    if not output_folder:
        return "Error: Please enter a path to the folder where you want to save the merged PDF."
    # Try to create output folder if it doesn't exist
    try:
        # exist_ok=True prevents errors if the folder already exists
        os.makedirs(output_folder, exist_ok=True)
    except OSError as e:
        return f"Error: Cannot create output folder '{output_folder}'. Error: {e}"
    if not os.path.isdir(output_folder):
        # Check again after creation attempt
        return f"Error: Output path '{output_folder}' is not a valid folder."

    if not output_filename:
        return "Error: Please enter a name for the output PDF file."

    # Ensure filename ends with .pdf and clean it
    output_filename = output_filename.strip()
    if not output_filename.lower().endswith('.pdf'):
        output_filename += ".pdf"
    if output_filename == ".pdf":  # If user only entered the extension
        return "Error: Output filename cannot be just '.pdf'."

    # Full path for output file
    final_output_path = os.path.join(output_folder, output_filename)
    status_messages.append(f"Input folder: {os.path.abspath(input_folder)}")
    status_messages.append(f"Output folder: {os.path.abspath(output_folder)}")
    status_messages.append(f"Output file: {output_filename}")
    status_messages.append("-" * 20)

    # --- 2. Finding PDF files ---
    pdf_files = []
    status_messages.append("Searching for PDF files...")
    try:
        for filename in os.listdir(input_folder):
            full_path = os.path.join(input_folder, filename)
            # Check if it's a file, ends with .pdf and isn't the output file itself
            # (important if input and output folders are the same)
            if os.path.isfile(full_path) and \
               filename.lower().endswith('.pdf') and \
               os.path.abspath(full_path).lower() != os.path.abspath(final_output_path).lower():
                pdf_files.append(full_path)
            elif os.path.abspath(full_path).lower() == os.path.abspath(final_output_path).lower():
                status_messages.append(
                    f" - Skipping existing output file: {filename}")

        if not pdf_files:
            status_messages.append(
                "\nNo PDF files found for merging in the input folder.")
            return "\n".join(status_messages)

        # Sort files alphabetically (by name)
        pdf_files.sort()

        status_messages.append(
            "\nFound PDF files for merging (in order):")
        for pdf_path in pdf_files:
            status_messages.append(f" - {os.path.basename(pdf_path)}")

    except Exception as e:
        status_messages.append(
            f"\nError while reading input folder: {e}")
        return "\n".join(status_messages)

    # --- 3. Merging PDF files ---
    merger = PdfWriter()
    status_messages.append("\nStarting merge process...")
    successfully_added = 0
    try:
        for pdf_path in pdf_files:
            status_messages.append(
                f" - Adding: {os.path.basename(pdf_path)}")
            try:
                merger.append(pdf_path)
                successfully_added += 1
            except Exception as e:
                status_messages.append(
                    f"   ! WARNING: Cannot add '{os.path.basename(pdf_path)}'. Error: {e}")
                status_messages.append(
                    f"   ! This file will be skipped.")

        if successfully_added == 0 or len(merger.pages) == 0:
            status_messages.append(
                "\nNo PDF files were successfully added or processed. Output file will not be created.")
            # Return messages without saving attempt
            return "\n".join(status_messages)

        # Save the merged PDF
        with open(final_output_path, "wb") as output_stream:
            merger.write(output_stream)

        status_messages.append("-" * 20)
        status_messages.append(f"\nMerge process SUCCESSFULLY completed!")
        status_messages.append(
            f"Merged PDF saved as: '{os.path.abspath(final_output_path)}'")
        status_messages.append(
            f"Total {successfully_added} of {len(pdf_files)} files successfully merged.")

    except Exception as e:
        status_messages.append(
            f"\n!!! ERROR during merge or save process: {e}")
    finally:
        # Always close the merger object (releases resources)
        merger.close()
        status_messages.append("Process completed.")

    # Return all collected messages as a single string
    return "\n".join(status_messages)


# --- Creating Gradio interface ---
with gr.Blocks() as iface:
    gr.Markdown("# PDF File Merger Tool")
    gr.Markdown(
        "Select a folder with PDF files, an output folder, and specify the output filename.")

    with gr.Row():
        input_folder_input = gr.Textbox(
            label="Folder with PDF files", placeholder="E.g., C:\\Users\\Username\\Documents\\PDFs_to_merge")
        output_folder_input = gr.Textbox(
            label="Folder to save merged PDF", placeholder="E.g., C:\\Users\\Username\\Documents\\Merged")

    output_filename_input = gr.Textbox(
        label="Output PDF filename (without .pdf)", placeholder="E.g., My_Merged_Document")

    submit_button = gr.Button("Merge PDFs")

    # interactive=False so the user cannot write in this field
    output_status = gr.Textbox(
        label="Status / Result", lines=15, interactive=False)

    # Connect button to function and inputs/outputs
    submit_button.click(
        fn=merge_pdfs_ui,
        inputs=[input_folder_input, output_folder_input, output_filename_input],
        outputs=output_status
    )

    gr.Markdown("---")
    gr.Markdown("Note: PDF files in the input folder will be sorted alphabetically before merging. If the output file already exists in the output folder, it will be overwritten.")

# Run the Gradio application
if __name__ == "__main__":
    print("Starting Gradio interface...")
    print("Install required libraries with: pip install pypdf gradio")
    # share=True will generate a public link (useful for sharing, but be cautious about privacy)
    # iface.launch(share=True)
    iface.launch()  # Runs locally, usually at http://127.0.0.1:7860
