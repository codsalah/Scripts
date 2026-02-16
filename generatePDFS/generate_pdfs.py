import json
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER


def create_exam_answer_key(json_file, output_pdf):
    """
    Generate a PDF answer key from JSON data
    
    Args:
        json_file: Path to JSON file with exam data
        output_pdf: Path for output PDF file
    """
    
    # Load JSON data
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Create PDF
    doc = SimpleDocTemplate(
        output_pdf,
        pagesize=letter,
        rightMargin=50,
        leftMargin=50,
        topMargin=50,
        bottomMargin=50
    )
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Define custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a5490'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.grey,
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica-Oblique'
    )
    
    question_style = ParagraphStyle(
        'QuestionStyle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.black,
        spaceAfter=8,
        fontName='Helvetica-Bold',
        leftIndent=0
    )
    
    option_style = ParagraphStyle(
        'OptionStyle',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.black,
        spaceAfter=3,
        fontName='Helvetica',
        leftIndent=20
    )
    
    correct_option_style = ParagraphStyle(
        'CorrectOptionStyle',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#006400'),
        spaceAfter=3,
        fontName='Helvetica-Bold',
        leftIndent=20
    )
    
    section_style = ParagraphStyle(
        'SectionStyle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1a5490'),
        spaceAfter=12,
        spaceBefore=15,
        fontName='Helvetica-Bold'
    )
    
    # Add header
    elements.append(Paragraph(data["title"], title_style))
    elements.append(Paragraph(data["subtitle"], subtitle_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Generate questions
    for section_data in data["sections"]:
        elements.append(Paragraph(section_data["section"], section_style))
        elements.append(Spacer(1, 0.1*inch))
        
        for q_data in section_data["questions"]:
            # Add question
            elements.append(Paragraph(q_data["question"], question_style))
            
            # Handle multiple correct answers
            correct_answers = q_data["correct"] if isinstance(q_data["correct"], list) else [q_data["correct"]]
            
            # Add options
            for i, option in enumerate(q_data["options"]):
                if i in correct_answers:
                    # Correct answer in green with checkmark
                    elements.append(Paragraph(f"<b>✓ {option}</b>", correct_option_style))
                else:
                    # Incorrect option
                    elements.append(Paragraph(f"○ {option}", option_style))
            
            elements.append(Spacer(1, 0.15*inch))
    
    # Add summary if exists
    if "summary" in data:
        elements.append(PageBreak())
        elements.append(Paragraph("Summary", title_style))
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph(data["summary"], styles['Normal']))
    
    # Build PDF
    doc.build(elements)
    print(f"PDF created successfully: {output_pdf}")


# Example JSON structure
example_json = {
    "title": "Linux System Administration I Exam",
    "subtitle": "Complete Answer Key with All Options",
    "sections": [
        {
            "section": "Section 1: Basic Commands & File System",
            "questions": [
                {
                    "question": "1. The LINUX command to print the system time is: (1 Point)",
                    "options": [
                        "echo time",
                        "time",
                        "echo date",
                        "date"
                    ],
                    "correct": 3
                },
                {
                    "question": "2. Which of the following is a relative path: (1 Point)",
                    "options": [
                        "../etc/passwd/",
                        "/../etc/passwd",
                        "/etc/passwd",
                        ".. etc/passwd"
                    ],
                    "correct": 0
                },
                {
                    "question": "3. Which of the following is standard output redirection: (Choose Two answers) (1 Point)",
                    "options": [
                        "2>",
                        "<",
                        ">",
                        "&",
                        ">>",
                        "|"
                    ],
                    "correct": [2, 4]
                }
            ]
        },
        {
            "section": "Section 2: Process Management",
            "questions": [
                {
                    "question": "4. The kill command is used to: (1 Point)",
                    "options": [
                        "send a kill signal to a process",
                        "send a signal to a process",
                        "kill a signal",
                        "none of the above"
                    ],
                    "correct": 1
                },
                {
                    "question": "5. To list background processes: (1 Point)",
                    "options": [
                        "fg",
                        "bg",
                        "jobs",
                        "ps"
                    ],
                    "correct": 2
                }
            ]
        }
    ],
    "summary": """<b>Total Questions:</b> 5<br/>
<br/>
<b>Format:</b> All questions shown with all answer options. Correct answers are marked in <font color="#006400"><b>GREEN</b></font> with a checkmark (✓).<br/>
<br/>
<b>Topics Covered:</b><br/>
- Basic Linux Commands<br/>
- File System Navigation<br/>
- Process Management<br/>
"""
}


if __name__ == "__main__":
    # Save example JSON
    with open("exam_data.json", "w", encoding='utf-8') as f:
        json.dump(example_json, f, indent=2, ensure_ascii=False)
    
    # Generate PDF
    create_exam_answer_key("exam_data.json", "exam_answer_key.pdf")