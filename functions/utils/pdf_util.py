from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def create_pdf_with_text(text, file_path, max_chars_per_line=80):
    """Create a multi-page PDF file with the specified text."""
    c = canvas.Canvas(file_path, pagesize=letter)
    width, height = letter
    c.setFont("Helvetica", 12)

    # Set starting position and page parameters
    margin = 40
    line_height = 14  # Adjust based on font size
    max_lines_per_page = int((height - 2 * margin) / line_height)

    # Split text into lines and further split long lines by character limit
    text_lines = []
    for line in text.splitlines():
        # Split line into chunks if it exceeds max_chars_per_line
        while len(line) > max_chars_per_line:
            text_lines.append(line[:max_chars_per_line])
            line = line[max_chars_per_line:]
        text_lines.append(line)

    # Loop through lines and add to PDF, page by page
    line_count = 0
    for line in text_lines:
        if line_count >= max_lines_per_page:
            c.showPage()  # Start a new page
            c.setFont("Helvetica", 12)
            line_count = 0  # Reset line count for new page

        # Draw the line on the current page
        c.drawString(margin, height - margin - (line_count * line_height), line)
        line_count += 1

    # Save the PDF
    c.save()