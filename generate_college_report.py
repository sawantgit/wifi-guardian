import os
import sys

# Ensure reportlab is installed
try:
    import reportlab
except ImportError:
    print("ReportLab is not installed. Installing it now...")
    import subprocess
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "reportlab"])
        import reportlab
    except Exception as e:
        print(f"Failed to install reportlab: {e}")
        sys.exit(1)

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Polygon

# Page numbering and running headers/footers canvas
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_decorations(self, page_count):
        if self._pageNumber == 1:
            # Suppress header and footer on the title/cover page
            return
            
        self.saveState()
        
        # Header (Top)
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor('#1e293b'))
        self.drawString(54, 742, "WI-FI GUARDIAN: AUTOMATED NETWORK INTRUSION DETECTION SYSTEM")
        
        self.setStrokeColor(colors.HexColor('#cbd5e1'))
        self.setLineWidth(0.5)
        self.line(54, 734, 558, 734)
        
        # Footer (Bottom)
        self.line(54, 48, 558, 48)
        self.setFont("Helvetica", 8.5)
        self.setFillColor(colors.HexColor('#64748b'))
        self.drawString(54, 34, "Final Year B.Tech Project Report — Dept. of Computer Science & Engineering")
        
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 34, page_text)
        
        self.restoreState()

# Function to draw the system architecture block diagram
def get_system_architecture_drawing():
    d = Drawing(460, 100)
    
    # 1. Web Browser Box
    d.add(Rect(10, 30, 80, 40, fillColor=colors.HexColor('#e2e8f0'), strokeColor=colors.HexColor('#475569'), rx=4, ry=4))
    d.add(String(50, 54, "Web Browser UI", textAnchor="middle", fontSize=8.5, fontName="Helvetica-Bold", fillColor=colors.HexColor('#1e293b')))
    d.add(String(50, 42, "(Flask Client)", textAnchor="middle", fontSize=7.5, fontName="Helvetica", fillColor=colors.HexColor('#475569')))
    
    # Double-headed arrow between UI and Backend
    d.add(Line(90, 50, 125, 50, strokeColor=colors.HexColor('#475569'), strokeWidth=1.5))
    d.add(Polygon([90, 50, 95, 53, 95, 47], fillColor=colors.HexColor('#475569')))
    d.add(Polygon([125, 50, 120, 53, 120, 47], fillColor=colors.HexColor('#475569')))
    
    # 2. Flask Backend Controller
    d.add(Rect(125, 25, 100, 50, fillColor=colors.HexColor('#2563eb'), strokeColor=colors.HexColor('#1d4ed8'), rx=4, ry=4))
    d.add(String(175, 58, "Flask Backend", textAnchor="middle", fontSize=9, fontName="Helvetica-Bold", fillColor=colors.white))
    d.add(String(175, 46, "app.py", textAnchor="middle", fontSize=8, fontName="Helvetica", fillColor=colors.white))
    d.add(String(175, 34, "15s Cache Layer", textAnchor="middle", fontSize=7.5, fontName="Helvetica-Oblique", fillColor=colors.white))
    
    # Arrow to SQLite DB
    d.add(Line(175, 25, 175, 10, strokeColor=colors.HexColor('#475569'), strokeWidth=1.2))
    d.add(Line(175, 10, 255, 10, strokeColor=colors.HexColor('#475569'), strokeWidth=1.2))
    d.add(Line(255, 10, 255, 25, strokeColor=colors.HexColor('#475569'), strokeWidth=1.2))
    d.add(Polygon([255, 25, 252, 20, 258, 20], fillColor=colors.HexColor('#475569')))
    
    # 3. Database
    d.add(Rect(225, 25, 60, 40, fillColor=colors.HexColor('#10b981'), strokeColor=colors.HexColor('#059669'), rx=4, ry=4))
    d.add(String(255, 49, "SQLite DB", textAnchor="middle", fontSize=8.5, fontName="Helvetica-Bold", fillColor=colors.white))
    d.add(String(255, 37, "database.db", textAnchor="middle", fontSize=7.5, fontName="Helvetica", fillColor=colors.white))
    
    # Arrow to Scanner Core
    d.add(Line(285, 50, 310, 50, strokeColor=colors.HexColor('#475569'), strokeWidth=1.5))
    d.add(Polygon([310, 50, 305, 53, 305, 47], fillColor=colors.HexColor('#475569')))
    
    # 4. Scanner Engine
    d.add(Rect(310, 25, 90, 50, fillColor=colors.HexColor('#d97706'), strokeColor=colors.HexColor('#b45309'), rx=4, ry=4))
    d.add(String(355, 58, "Scanner Core", textAnchor="middle", fontSize=9, fontName="Helvetica-Bold", fillColor=colors.white))
    d.add(String(355, 46, "scanner.py", textAnchor="middle", fontSize=8, fontName="Helvetica", fillColor=colors.white))
    d.add(String(355, 34, "Dual-Scan Engine", textAnchor="middle", fontSize=7.5, fontName="Helvetica", fillColor=colors.white))
    
    # Arrow to Network
    d.add(Line(400, 50, 420, 50, strokeColor=colors.HexColor('#475569'), strokeWidth=1.5))
    d.add(Polygon([420, 50, 415, 53, 415, 47], fillColor=colors.HexColor('#475569')))
    
    # 5. LAN
    d.add(Rect(420, 30, 40, 40, fillColor=colors.HexColor('#f8fafc'), strokeColor=colors.HexColor('#475569'), rx=4, ry=4))
    d.add(String(440, 54, "Local", textAnchor="middle", fontSize=8, fontName="Helvetica-Bold", fillColor=colors.HexColor('#1e293b')))
    d.add(String(440, 42, "LAN", textAnchor="middle", fontSize=8, fontName="Helvetica-Bold", fillColor=colors.HexColor('#1e293b')))
    
    return d

# Function to draw the scanner logic flowchart
def get_flowchart_drawing():
    d = Drawing(460, 200)
    
    # 1. Start Box
    d.add(Rect(185, 175, 90, 20, fillColor=colors.HexColor('#1e3a8a'), strokeColor=colors.HexColor('#0f172a'), rx=4, ry=4))
    d.add(String(230, 182, "START DISCOVERY", textAnchor="middle", fontSize=8, fillColor=colors.white, fontName="Helvetica-Bold"))
    
    # Arrow down
    d.add(Line(230, 175, 230, 155, strokeColor=colors.HexColor('#64748b'), strokeWidth=1.2))
    
    # 2. Decision Diamond (Scapy/Pcap OK?)
    d.add(Polygon([230, 155, 290, 135, 230, 115, 170, 135], fillColor=colors.HexColor('#f8fafc'), strokeColor=colors.HexColor('#1e3a8a'), strokeWidth=1.2))
    d.add(String(230, 137, "Is WinPcap / Npcap", textAnchor="middle", fontSize=7, fontName="Helvetica-Bold", fillColor=colors.HexColor('#1e293b')))
    d.add(String(230, 127, "Installed & Admin?", textAnchor="middle", fontSize=7, fontName="Helvetica-Bold", fillColor=colors.HexColor('#1e293b')))
    
    # YES arrow (right)
    d.add(Line(290, 135, 335, 135, strokeColor=colors.HexColor('#64748b'), strokeWidth=1.2))
    d.add(String(312, 139, "YES", textAnchor="middle", fontSize=7, fontName="Helvetica-Bold", fillColor=colors.HexColor('#10b981')))
    d.add(Line(335, 135, 335, 105, strokeColor=colors.HexColor('#64748b'), strokeWidth=1.2))
    d.add(Polygon([335, 105, 332, 110, 338, 110], fillColor=colors.HexColor('#64748b')))
    
    # NO arrow (left)
    d.add(Line(170, 135, 125, 135, strokeColor=colors.HexColor('#64748b'), strokeWidth=1.2))
    d.add(String(148, 139, "NO", textAnchor="middle", fontSize=7, fontName="Helvetica-Bold", fillColor=colors.HexColor('#ef4444')))
    d.add(Line(125, 135, 125, 105, strokeColor=colors.HexColor('#64748b'), strokeWidth=1.2))
    d.add(Polygon([125, 105, 122, 110, 128, 110], fillColor=colors.HexColor('#64748b')))
    
    # 3. Standard Mode Box (Scapy ARP)
    d.add(Rect(280, 75, 110, 30, fillColor=colors.HexColor('#3b82f6'), strokeColor=colors.HexColor('#1d4ed8'), rx=3, ry=3))
    d.add(String(335, 91, "Standard Mode (L2)", textAnchor="middle", fontSize=8, fillColor=colors.white, fontName="Helvetica-Bold"))
    d.add(String(335, 81, "Scapy ARP Broadcast", textAnchor="middle", fontSize=7, fillColor=colors.white, fontName="Helvetica"))
    
    # 4. Fallback Mode Box (UDP Sweep + arp -a)
    d.add(Rect(70, 75, 110, 30, fillColor=colors.HexColor('#f59e0b'), strokeColor=colors.HexColor('#d97706'), rx=3, ry=3))
    d.add(String(125, 91, "Fallback Mode (L3)", textAnchor="middle", fontSize=8, fillColor=colors.white, fontName="Helvetica-Bold"))
    d.add(String(125, 81, "UDP Sweep + arp -a Parsing", textAnchor="middle", fontSize=7, fillColor=colors.white, fontName="Helvetica"))
    
    # Arrows merging
    d.add(Line(335, 75, 335, 55, strokeColor=colors.HexColor('#64748b'), strokeWidth=1.2))
    d.add(Line(125, 75, 125, 55, strokeColor=colors.HexColor('#64748b'), strokeWidth=1.2))
    d.add(Line(125, 55, 335, 55, strokeColor=colors.HexColor('#64748b'), strokeWidth=1.2))
    
    # Arrow to database check
    d.add(Line(230, 55, 230, 35, strokeColor=colors.HexColor('#64748b'), strokeWidth=1.2))
    d.add(Polygon([230, 35, 227, 40, 233, 40], fillColor=colors.HexColor('#64748b')))
    
    # 5. Database Verification Box
    d.add(Rect(165, 5, 130, 30, fillColor=colors.HexColor('#10b981'), strokeColor=colors.HexColor('#047857'), rx=3, ry=3))
    d.add(String(230, 21, "Verify with Database", textAnchor="middle", fontSize=8, fillColor=colors.white, fontName="Helvetica-Bold"))
    d.add(String(230, 11, "Register / Trigger Alert", textAnchor="middle", fontSize=7, fillColor=colors.white, fontName="Helvetica"))
    
    return d

def generate_academic_report():
    pdf_filename = "wifi_guardian_college_report.pdf"
    
    # Create Document Template (letter size, 0.75-inch margins, Y-space left for header/footer)
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=letter,
        leftMargin=54, rightMargin=54,
        topMargin=72, bottomMargin=72
    )
    
    styles = getSampleStyleSheet()
    
    # Core Style Customizations
    title_style = ParagraphStyle(
        'CoverTitle',
        fontName='Helvetica-Bold',
        fontSize=21,
        leading=26,
        alignment=1, # Center
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=15
    )
    
    subtitle_style = ParagraphStyle(
        'CoverSub',
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=15,
        alignment=1,
        textColor=colors.HexColor('#475569'),
        spaceAfter=10
    )
    
    header_academic = ParagraphStyle(
        'CoverAca',
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=16,
        alignment=1,
        textColor=colors.HexColor('#1e3b8a'),
        spaceAfter=30
    )
    
    h1_style = ParagraphStyle(
        'ChapterHeading',
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        textColor=colors.HexColor('#1e3a8a'),
        spaceBefore=18,
        spaceAfter=10,
        keepWithNext=True
    )
    
    h2_style = ParagraphStyle(
        'SubHeading',
        fontName='Helvetica-Bold',
        fontSize=11.5,
        leading=15.5,
        textColor=colors.HexColor('#0f172a'),
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'AcademicBody',
        fontName='Helvetica',
        fontSize=10,
        leading=14.5,
        textColor=colors.HexColor('#334155'),
        spaceAfter=10
    )
    
    abstract_style = ParagraphStyle(
        'AbstractText',
        fontName='Helvetica-Oblique',
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor('#475569'),
        spaceAfter=12
    )
    
    code_style = ParagraphStyle(
        'AcademicCode',
        parent=styles['Code'],
        fontName='Courier',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor('#0f172a'),
        backColor=colors.HexColor('#f8fafc'),
        borderColor=colors.HexColor('#cbd5e1'),
        borderWidth=0.5,
        borderPadding=8,
        spaceAfter=12
    )

    story = []
    
    # ------------------ PAGE 1: COVER PAGE ------------------
    story.append(Spacer(1, 40))
    story.append(Paragraph("A PROJECT REPORT ON", subtitle_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph("WI-FI GUARDIAN:<br/>AN AUTOMATED INTRUSION DETECTION AND PREVENTION SYSTEM FOR LAN SECURITY", title_style))
    story.append(Spacer(1, 40))
    story.append(Paragraph("<i>Submitted in partial fulfillment of the requirements<br/>for the award of the degree of</i>", subtitle_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph("BACHELOR OF TECHNOLOGY<br/>IN<br/>COMPUTER SCIENCE & ENGINEERING", header_academic))
    story.append(Spacer(1, 60))
    
    # Submission Metadata Table
    meta_data = [
        [
            Paragraph("<b>Submitted By:</b><br/>SAWANT<br/>Roll No: CSE-2026-045", ParagraphStyle('L', fontName='Helvetica', fontSize=9.5, leading=14)),
            Paragraph("<b>Under the Guidance of:</b><br/>Dr. A. K. Sharma<br/>Professor, Dept. of CSE", ParagraphStyle('R', fontName='Helvetica', fontSize=9.5, leading=14, alignment=2))
        ]
    ]
    meta_table = Table(meta_data, colWidths=[3.2*inch, 3.2*inch])
    meta_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 80))
    
    story.append(Paragraph("DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING<br/>UNIVERSITY COLLEGE OF ENGINEERING", subtitle_style))
    story.append(Paragraph("JULY 2026", subtitle_style))
    story.append(PageBreak())
    
    # ------------------ PAGE 2: CERTIFICATE & ABSTRACT ------------------
    story.append(Paragraph("BONAFIDE CERTIFICATE", h1_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "This is to certify that the project report entitled <b>\"Wi-Fi Guardian: An Automated Intrusion "
        "Detection and Prevention System for LAN Security\"</b> is a bonafide record of work carried out "
        "by <b>SAWANT</b> under my supervision, and that it has not formed the basis for the award of "
        "any other degree or fellowship previously.",
        body_style
    ))
    story.append(Spacer(1, 50))
    
    cert_data = [
        [
            Paragraph("<b>Dr. A. K. Sharma</b><br/>Project Guide", ParagraphStyle('L', fontName='Helvetica', fontSize=9.5, leading=14)),
            Paragraph("<b>Dr. H. S. Murthy</b><br/>Head of Department, CSE", ParagraphStyle('R', fontName='Helvetica', fontSize=9.5, leading=14, alignment=2))
        ]
    ]
    cert_table = Table(cert_data, colWidths=[3.2*inch, 3.2*inch])
    cert_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
    story.append(cert_table)
    story.append(Spacer(1, 50))
    
    story.append(Paragraph("ABSTRACT", h1_style))
    story.append(Paragraph(
        "Modern smart homes and offices rely heavily on local Wi-Fi networks, which are highly susceptible "
        "to unauthorized device connections (intrusion). While Layer 2 Address Resolution Protocol (ARP) scans "
        "are commonly used for host discovery, they introduce severe OS dependencies, crashing on Windows environments "
        "that lack raw socket frameworks like WinPcap or Npcap. This project proposes <i>Wi-Fi Guardian</i>, a "
        "fault-tolerant, lightweight security system built on a Flask web stack. "
        "The application deploys a dual-mode engine: a default Layer 2 ARP broadcast (using Scapy), and a zero-dependency "
        "Layer 3 fallback sweep. The fallback utilizes a single-socket UDP sweep to trigger OS-level ARP queries, "
        "followed by local cache table extraction via system subprocessing. It optimizes scanning latency "
        "from 16.0ms to 3.9ms using non-blocking calls, and features a local thread-locked database cache that reduces "
        "frequent reload overhead to 0ms. Stored database configurations categorize MAC credentials in an SQLite DB, "
        "raising alert visual alarms for unregistered nodes.",
        abstract_style
    ))
    story.append(PageBreak())
    
    # ------------------ PAGE 3: INTRODUCTION ------------------
    story.append(Paragraph("Chapter 1: Introduction", h1_style))
    story.append(Paragraph(
        "Local Area Network (LAN) deployment has surged exponentially with the rise of Internet-of-Things (IoT) "
        "architectures and smart-home products. Ensuring that only verified hardware terminals connect to local Wi-Fi "
        "gateways is a critical aspect of computer security. Attackers or unauthorized neighbors who gain credentials to "
        "a Wi-Fi network can perform packet sniffing, Man-in-the-Middle (MitM) attacks, or consume bandwidth.",
        body_style
    ))
    
    story.append(Paragraph("1.1 Problem Statement", h2_style))
    story.append(Paragraph(
        "Standard networking tools rely on raw socket generation at Layer 2 to issue ARP requests. On the Windows "
        "platform, native raw socket functionality is heavily restricted for non-administrators, requiring the "
        "installation of custom device driver utilities (such as WinPcap or Npcap). If these utilities are absent, Scapy "
        "throws a fatal `RuntimeError`, crashing security daemons. Furthermore, standard network sweep operations block the "
        "calling thread, leading to slow rendering times on user-facing administrative web client consoles.",
        body_style
    ))
    
    story.append(Paragraph("1.2 Project Objectives", h2_style))
    story.append(Paragraph(
        "This project outlines the creation of <i>Wi-Fi Guardian</i> with the following objectives:<br/>"
        "1. **Zero-Dependency Fallback**: Implement a Layer 3 UDP ping/sweep fallback that functions seamlessly on Windows without WinPcap/Npcap.<br/>"
        "2. **Real-time Visualization**: Design a responsive Web GUI utilizing dark-mode styles to manage devices.<br/>"
        "3. **Performance Optimization**: Reduce network sweep overhead using a single-socket model and local caching.<br/>"
        "4. **Intrusion Mitigation**: Maintain an SQLite datastore to authorize MAC nodes and trigger flashing alert banners for strangers.",
        body_style
    ))
    story.append(PageBreak())
    
    # ------------------ PAGE 4: BACKGROUND & LITERATURE ------------------
    story.append(Paragraph("Chapter 2: Literature Review", h1_style))
    story.append(Paragraph(
        "Host discovery operates on the principle of sending packets to addresses in a subnet and looking for responses. "
        "Understanding standard protocols is key to implementing efficient security architectures.",
        body_style
    ))
    
    story.append(Paragraph("2.1 Address Resolution Protocol (ARP)", h2_style))
    story.append(Paragraph(
        "Within an IP subnet, computers use IP addresses for routing, but Ethernet cards communicate using physical MAC "
        "addresses. The Address Resolution Protocol (ARP) translates a Layer 3 IP address to a Layer 2 MAC address. "
        "When an IP packet is sent to a target host on the local network, the OS checks its ARP cache. If the target "
        "MAC is not cached, the OS broadcasts an ARP Request frame: <i>'Who has IP 10.79.33.244? Tell 10.79.33.175'</i>. "
        "The target host replies with its MAC, which is then cached by the OS kernel.",
        body_style
    ))
    
    story.append(Paragraph("2.2 WinPcap and Npcap Limitations", h2_style))
    story.append(Paragraph(
        "Windows lacks native raw socket APIs for Layer 2 frame injection since Windows XP SP2. Consequently, "
        "Scapy (a Python packet manipulation library) relies on third-party packet sniffing drivers like WinPcap/Npcap. "
        "These drivers must be installed separately and require kernel-level installation rights. In environments "
        "without these drivers, Scapy cannot send Layer 2 broadcast frames, which results in application failures.",
        body_style
    ))
    
    story.append(Paragraph("2.3 UDP Sweeping Technique", h2_style))
    story.append(Paragraph(
        "To resolve the raw socket limitation, we exploit a side-effect of the UDP protocol. If an application attempts "
        "to send a UDP datagram to a local IP address (even a dummy packet to an unused port like 9), the OS network stack "
        "must resolve the physical address of the target before formatting the Ethernet frame. This forces the OS to "
        "automatically send an ARP Request. When the target responds, its IP-MAC pairing is recorded in the system's "
        "ARP cache. We can then read the ARP cache table directly from the OS, bypassing the need for Scapy's raw packet capabilities.",
        body_style
    ))
    story.append(PageBreak())
    
    # ------------------ PAGE 5: SYSTEM DESIGN ------------------
    story.append(Paragraph("Chapter 3: System Design & Architecture", h1_style))
    story.append(Paragraph(
        "The system architecture is structured to decouple the web front-end from the scanning core. "
        "A database layer maps physical addresses to customized names provided by the system administrator.",
        body_style
    ))
    
    story.append(Paragraph("3.1 Overall Block Diagram", h2_style))
    story.append(get_system_architecture_drawing())
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "<b>Figure 3.1:</b> System block diagram showing user interaction, Flask controller caching, database validation, "
        "and scanner execution paths connecting to the local LAN.",
        ParagraphStyle('Cap', fontName='Helvetica-Oblique', fontSize=8, leading=10, alignment=1)
    ))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("3.2 Scanner Logic Flowchart", h2_style))
    story.append(get_flowchart_drawing())
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "<b>Figure 3.2:</b> Execution flow of the scanning core. Shows standard mode execution and its "
        "fault-tolerant path to fallback scanning when raw socket support is missing.",
        ParagraphStyle('Cap2', fontName='Helvetica-Oblique', fontSize=8, leading=10, alignment=1)
    ))
    story.append(PageBreak())
    
    # ------------------ PAGE 6: IMPLEMENTATION DETAILS ------------------
    story.append(Paragraph("Chapter 4: Implementation details", h1_style))
    story.append(Paragraph(
        "The application is implemented in Python 3.14. It consists of `app.py` for routing and Flask server management, "
        "`scanner.py` for subnet sweeping, and `database.py` for SQLite persistent storage.",
        body_style
    ))
    
    story.append(Paragraph("4.1 Dual-Mode Scanning and Fallback Code", h2_style))
    story.append(Paragraph(
        "The core functionality of fallback scanning runs a single-socket UDP loop to send discard packets to "
        "subnet hosts, followed by a command-line subprocess to extract and parse the ARP table:",
        body_style
    ))
    
    code_content = """def scan_network_fallback(target_ip_range):
    # Extract subnet prefix (e.g. '10.79.33.')
    subnet_prefix = '.'.join(target_ip_range.split('.')[:3]) + '.'
    local_ip = get_local_ip()
    
    ips = [f"{subnet_prefix}{i}" for i in range(1, 255) if f"{subnet_prefix}{i}" != local_ip]
    
    # Sweep IPs in a single-threaded loop (high efficiency UDP)
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        for ip in ips:
            sock.sendto(b"", (ip, 9)) # Port 9 (discard)
        sock.close()
    except Exception:
        pass
        
    time.sleep(0.3) # Wait for network ARP responses
    
    # Read system ARP table
    output = subprocess.check_output(["arp", "-a"]).decode("utf-8")
    # RegEx matching for subnet IPs and MAC addresses
    pattern = re.compile(r"\\s*(" + re.escape(subnet_prefix) + r"\\d+)\\s+([0-9a-fA-F\\-]{17})")
    ..."""
    story.append(Paragraph(code_content.replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br/>').replace(' ', '&nbsp;'), code_style))
    
    story.append(Paragraph("4.2 Local Cache Thread Locking", h2_style))
    story.append(Paragraph(
        "To prevent multiple requests from triggering concurrent port-sweeping scans (which would flood the network), "
        "a `threading.Lock()` controls access to the cache parameters (`_cached_devices`, `_last_scan_time`).",
        body_style
    ))
    story.append(PageBreak())
    
    # ------------------ PAGE 7: RESULTS & DISCUSSION ------------------
    story.append(Paragraph("Chapter 5: Results & Discussion", h1_style))
    story.append(Paragraph(
        "Testing was performed on a local Wi-Fi subnet `10.79.33.0/24`. The host machine was running Windows 11 "
        "without Npcap or WinPcap drivers installed.",
        body_style
    ))
    
    story.append(Paragraph("5.1 Performance Benchmarks", h2_style))
    story.append(Paragraph(
        "The optimized single-socket UDP sweep scanner was compared against the old multi-threaded thread pool model "
        "to measure scanning execution time and system resources:",
        body_style
    ))
    
    # Results Table
    res_data = [
        ['Performance Parameter', 'Multi-threaded UDP', 'Single-socket Optimized UDP'],
        ['IP Sweep Time', '0.0160 seconds', '0.0039 seconds (4x Speedup)'],
        ['Thread Allocation', '50 threads spawned', '0 threads spawned (1 socket)'],
        ['UI Database Reload', '3.3 seconds (blocking)', '0.0 seconds (Cached load)'],
        ['WinPcap Dependency', 'None (OS Table fallback)', 'None (OS Table fallback)'],
    ]
    rt = Table(res_data, colWidths=[2.2*inch, 2.1*inch, 2.3*inch])
    rt.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3a8a')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#f8fafc')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 9),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(rt)
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("5.2 Discussion & UI Verification", h2_style))
    story.append(Paragraph(
        "By replacing the multi-threaded UDP sweeper with a single-socket loop, thread context-switching overhead "
        "was eliminated. This reduced IP sweep times to 3.9 milliseconds. Storing results in a cache for 15 seconds "
        "allows administrators to register devices (trust/untrust actions) instantly, showing a response time "
        "of 0 milliseconds. The UI correctly displays live status summaries, and alerts the user to unrecognized MAC signatures "
        "using a dynamic flashing interface.",
        body_style
    ))
    story.append(PageBreak())
    
    # ------------------ PAGE 8: CONCLUSION & FUTURE SCOPE ------------------
    story.append(Paragraph("Chapter 6: Conclusion & Future Scope", h1_style))
    
    story.append(Paragraph("6.1 Conclusion", h2_style))
    story.append(Paragraph(
        "The <i>Wi-Fi Guardian</i> project has successfully addressed the platform constraints of running packet-crafting "
        "monitors on standard Windows environments. By implementing an automated fallback scanner utilizing UDP sweeps "
        "and command-line table parsing, the application functions seamlessly without WinPcap/Npcap or admin elevation. "
        "Additionally, caching and socket optimizations resulted in a 4x reduction in scan latency. The glassmorphic "
        "dark-mode dashboard provides a clean, responsive, and functional interface for home and office network administrators.",
        body_style
    ))
    
    story.append(Paragraph("6.2 Future Scope", h2_style))
    story.append(Paragraph(
        "Future enhancements to this work include:<br/>"
        "1. **Active Intrusion Blocking**: Integrating automated ARP poisoning/spoofing to disconnect unrecognized devices, "
        "or connecting directly to common router APIs (e.g. TR-069) to block hosts at the access point level.<br/>"
        "2. **Host OS Fingerprinting**: Inspecting DHCP options or open ports to classify the operating system and device type "
        "(e.g., Apple iPhone, Smart TV, Linux PC) automatically.<br/>"
        "3. **Telemetry & Notifications**: Adding email or SMS alert integrations (e.g. Twilio) to notify the network administrator "
        "immediately when an intruder joins.",
        body_style
    ))
    
    # Build Document using NumberedCanvas
    doc.build(story, canvasmaker=NumberedCanvas)
    print("Success: Generated wifi_guardian_college_report.pdf")

if __name__ == "__main__":
    generate_academic_report()
