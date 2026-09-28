import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def create_presentation():
    # Initialize Presentation
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # Style colors (Dark Theme)
    BG_COLOR    = RGBColor(8, 7, 16)       # #080710 Dark Sky
    TEXT_MAIN   = RGBColor(241, 240, 247)  # #f1f0f7 Soft White
    TEXT_MUTED  = RGBColor(158, 155, 180)  # #9e9bb4 Quiet Gray
    PRIMARY     = RGBColor(157, 78, 221)   # #9d4edd Magic Purple
    SECONDARY   = RGBColor(67, 97, 238)    # #4361ee Deep Blue
    ACCENT      = RGBColor(76, 201, 240)   # #4cc9f0 Bright Cyan
    CARD_BG     = RGBColor(22, 20, 38)     # #161426 Card Dark
    CARD_BORDER = RGBColor(50, 48, 70)     # #323046 Border Gray
    SUCCESS     = RGBColor(56, 176, 0)
    WARNING     = RGBColor(255, 159, 28)
    DANGER      = RGBColor(217, 4, 41)

    # ── Helpers ──────────────────────────────────────────────────────────────

    def set_slide_background(slide):
        fill = slide.background.fill
        fill.solid()
        fill.fore_color.rgb = BG_COLOR

    def add_slide_with_header(title, category, slide_num, total=15):
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        set_slide_background(slide)

        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(4), Inches(0.4))
        p_cat = cat_box.text_frame.paragraphs[0]
        p_cat.text = category.upper()
        p_cat.font.name = 'Arial'; p_cat.font.size = Pt(10)
        p_cat.font.bold = True;    p_cat.font.color.rgb = PRIMARY

        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.0), Inches(0.8))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        p_title = tf_title.paragraphs[0]
        p_title.text = title
        p_title.font.name = 'Arial'; p_title.font.size = Pt(28)
        p_title.font.bold = True;    p_title.font.color.rgb = TEXT_MAIN

        divider = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.5), Inches(11.733), Inches(0.02))
        divider.fill.solid(); divider.fill.fore_color.rgb = CARD_BORDER
        divider.line.color.rgb = CARD_BORDER

        footer_box = slide.shapes.add_textbox(Inches(0.8), Inches(6.8), Inches(11.733), Inches(0.4))
        p_foot = footer_box.text_frame.paragraphs[0]
        p_foot.text = f"Arianna AI  |  Slide {slide_num} of {total}"
        p_foot.font.name = 'Arial'; p_foot.font.size = Pt(9)
        p_foot.font.color.rgb = TEXT_MUTED

        return slide

    def draw_card(slide, left, top, width, height, title, text,
                  border_color=None, bg_color=None):
        border_color = border_color or CARD_BORDER
        bg_color = bg_color or CARD_BG
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid(); card.fill.fore_color.rgb = bg_color
        card.line.color.rgb = border_color; card.line.width = Pt(1.5)

        tb = slide.shapes.add_textbox(left + Inches(0.25), top + Inches(0.2),
                                      width - Inches(0.5), height - Inches(0.4))
        tf = tb.text_frame; tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = title
        p.font.name = 'Arial'; p.font.size = Pt(16)
        p.font.bold = True;    p.font.color.rgb = TEXT_MAIN
        p.space_after = Pt(10)

        p2 = tf.add_paragraph()
        p2.text = text
        p2.font.name = 'Arial'; p2.font.size = Pt(12)
        p2.font.color.rgb = TEXT_MUTED

        return card

    def add_text(slide, text, left, top, width, height,
                 size=14, bold=False, color=None, italic=False, align=PP_ALIGN.LEFT):
        color = color or TEXT_MUTED
        tb = slide.shapes.add_textbox(left, top, width, height)
        tf = tb.text_frame; tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = text; p.alignment = align
        p.font.name = 'Arial'; p.font.size = Pt(size)
        p.font.bold = bold; p.font.color.rgb = color
        p.font.italic = italic

    # ═══════════════════════════════════════════════════════════════════════
    # SLIDE 1 — Title
    # ═══════════════════════════════════════════════════════════════════════
    s1 = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_background(s1)

    logo_circle = s1.shapes.add_shape(MSO_SHAPE.OVAL, Inches(5.666), Inches(1.0), Inches(2), Inches(2))
    logo_circle.fill.solid(); logo_circle.fill.fore_color.rgb = CARD_BG
    logo_circle.line.color.rgb = PRIMARY; logo_circle.line.width = Pt(3)

    add_text(s1, "Arianna", Inches(5.666), Inches(1.5), Inches(2), Inches(1),
             size=28, bold=True, color=PRIMARY, align=PP_ALIGN.CENTER)

    t_box = s1.shapes.add_textbox(Inches(1.5), Inches(3.4), Inches(10.333), Inches(1.4))
    tf_t = t_box.text_frame
    p_t = tf_t.paragraphs[0]
    p_t.alignment = PP_ALIGN.CENTER
    p_t.text = "Arianna AI: Your Friendly Chatbot Helper!"
    p_t.font.name = 'Arial'; p_t.font.size = Pt(38)
    p_t.font.bold = True;    p_t.font.color.rgb = TEXT_MAIN

    p_sub = tf_t.add_paragraph()
    p_sub.alignment = PP_ALIGN.CENTER
    p_sub.text = "Ask anything, get simple answers fast — powered by Google Gemini!"
    p_sub.font.name = 'Arial'; p_sub.font.size = Pt(16)
    p_sub.font.color.rgb = TEXT_MUTED; p_sub.space_before = Pt(10)

    meta = s1.shapes.add_textbox(Inches(3.5), Inches(5.3), Inches(6.333), Inches(0.6))
    p_m = meta.text_frame.paragraphs[0]
    p_m.alignment = PP_ALIGN.CENTER
    p_m.text = "Project Proposal  |  Easy for Everyone  |  2026"
    p_m.font.name = 'Arial'; p_m.font.size = Pt(12)
    p_m.font.bold = True;    p_m.font.color.rgb = PRIMARY

    # ═══════════════════════════════════════════════════════════════════════
    # SLIDE 2 — What is Arianna AI?
    # ═══════════════════════════════════════════════════════════════════════
    s2 = add_slide_with_header("What is Arianna AI?", "Introduction", 2)

    draw_card(s2, Inches(0.8), Inches(2.0), Inches(5.5), Inches(4.2),
              "Meet Arianna! 🤖",
              "Arianna AI is a smart chatbot — like a super-helpful friend you can chat with "
              "on a computer anytime. Just type your question, and she answers right away!")

    draw_card(s2, Inches(6.8), Inches(2.0), Inches(5.7), Inches(2.0),
              "You Talk, She Listens 💬",
              "Type a question like sending a text message. Arianna reads it and replies instantly!")

    draw_card(s2, Inches(6.8), Inches(4.3), Inches(5.7), Inches(1.9),
              "Powered by Google Gemini 🧠",
              "Arianna uses one of the smartest AI brains in the world to think and answer you.")

    # ═══════════════════════════════════════════════════════════════════════
    # SLIDE 3 — The Problem
    # ═══════════════════════════════════════════════════════════════════════
    s3 = add_slide_with_header("The Problem We Are Solving", "The Problem", 3)

    desc3 = s3.shapes.add_textbox(Inches(0.8), Inches(2.0), Inches(5.5), Inches(4.2))
    tf3 = desc3.text_frame; tf3.word_wrap = True

    p3a = tf3.paragraphs[0]
    p3a.text = "Getting help can be really hard!"
    p3a.font.name = 'Arial'; p3a.font.size = Pt(20)
    p3a.font.bold = True;    p3a.font.color.rgb = TEXT_MAIN
    p3a.space_after = Pt(12)

    p3b = tf3.add_paragraph()
    p3b.text = ("Imagine you need help with homework, but your teacher is busy, "
                "and Google shows 1,000 complicated pages. That is so annoying!")
    p3b.font.name = 'Arial'; p3b.font.size = Pt(14); p3b.font.color.rgb = TEXT_MUTED
    p3b.space_after = Pt(10)

    p3c = tf3.add_paragraph()
    p3c.text = "You just want a simple, friendly answer — not a textbook full of big words!"
    p3c.font.name = 'Arial'; p3c.font.size = Pt(14); p3c.font.color.rgb = TEXT_MUTED

    draw_card(s3, Inches(6.8), Inches(2.0), Inches(5.7), Inches(4.2),
              "Common Struggles 😩",
              "• Too Complicated: Search engines show confusing results with huge words.\n\n"
              "• No One to Ask: Sometimes nobody is around to help you right now.\n\n"
              "• Hard AI Tools: Other AI apps are confusing and need lots of setup.")

    # ═══════════════════════════════════════════════════════════════════════
    # SLIDE 4 — The Solution
    # ═══════════════════════════════════════════════════════════════════════
    s4 = add_slide_with_header("Arianna AI Is the Answer!", "Solution", 4)

    draw_card(s4, Inches(0.8), Inches(2.2), Inches(3.6), Inches(3.8),
              "Just Type & Ask 💬",
              "Type any question in plain English, just like texting a friend. "
              "Arianna understands you perfectly!")

    draw_card(s4, Inches(4.8), Inches(2.2), Inches(3.6), Inches(3.8),
              "Get Fast Answers ⚡",
              "Arianna replies in seconds — no waiting, no searching, "
              "no confusing links to click through!")

    draw_card(s4, Inches(8.8), Inches(2.2), Inches(3.6), Inches(3.8),
              "Your Chats Stay Private 🔒",
              "All your conversations are saved only on YOUR computer. "
              "Nobody else can ever read your chats!")

    # ═══════════════════════════════════════════════════════════════════════
    # SLIDE 5 — How It Works
    # ═══════════════════════════════════════════════════════════════════════
    s5 = add_slide_with_header("How Does Arianna Work?", "How It Works", 5)

    add_text(s5, "It is as easy as 1 — 2 — 3! 😊",
             Inches(0.8), Inches(1.8), Inches(11.733), Inches(0.5),
             size=14, align=PP_ALIGN.CENTER)

    draw_card(s5, Inches(0.8), Inches(2.5), Inches(3.2), Inches(3.8),
              "Step 1: You Type ✏️",
              "Type your question in the chat box — just like sending a message to a friend!")

    add_text(s5, "----->", Inches(4.1), Inches(4.0), Inches(1.0), Inches(0.6),
             size=14, bold=True, color=PRIMARY, align=PP_ALIGN.CENTER)

    draw_card(s5, Inches(5.1), Inches(2.5), Inches(3.2), Inches(3.8),
              "Step 2: App Sends It 📡",
              "The app secretly passes your question to a super smart computer in the cloud!")

    add_text(s5, "----->", Inches(8.4), Inches(4.0), Inches(1.0), Inches(0.6),
             size=14, bold=True, color=PRIMARY, align=PP_ALIGN.CENTER)

    draw_card(s5, Inches(9.4), Inches(2.5), Inches(3.2), Inches(3.8),
              "Step 3: Arianna Answers 🤖",
              "Arianna types her answer back to you, word by word, right on your screen!")

    # ═══════════════════════════════════════════════════════════════════════
    # SLIDE 6 — What Can Arianna Do?
    # ═══════════════════════════════════════════════════════════════════════
    s6 = add_slide_with_header("What Can Arianna Help You With?", "Features", 6)

    draw_card(s6, Inches(0.8), Inches(2.0), Inches(2.7), Inches(3.8),
              "Homework Help 📚",
              "Ask about math, history, or science. Arianna explains things simply!")

    draw_card(s6, Inches(3.78), Inches(2.0), Inches(2.7), Inches(3.8),
              "Writing Help ✍️",
              "Need to write a story or email? Arianna helps you put your ideas into words!")

    draw_card(s6, Inches(6.76), Inches(2.0), Inches(2.7), Inches(3.8),
              "Answer Questions 💡",
              "Curious about something? Ask Arianna! She explains almost anything simply.")

    draw_card(s6, Inches(9.74), Inches(2.0), Inches(2.7), Inches(3.8),
              "Just Chat! 😊",
              "Want to share ideas or just talk? Arianna is always here to listen and chat!")

    # ═══════════════════════════════════════════════════════════════════════
    # SLIDE 7 — Chat Demo
    # ═══════════════════════════════════════════════════════════════════════
    s7 = add_slide_with_header("See Arianna in Action!", "Demo", 7)

    left_box = s7.shapes.add_textbox(Inches(0.8), Inches(2.0), Inches(5.6), Inches(4.5))
    tf7 = left_box.text_frame; tf7.word_wrap = True

    p7t = tf7.paragraphs[0]
    p7t.text = "A Real Conversation Example 💬"
    p7t.font.name = 'Arial'; p7t.font.size = Pt(18)
    p7t.font.bold = True;    p7t.font.color.rgb = TEXT_MAIN
    p7t.space_after = Pt(10)

    # User bubble
    u_sh = s7.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.2), Inches(3.0), Inches(4.8), Inches(0.8))
    u_sh.fill.solid(); u_sh.fill.fore_color.rgb = RGBColor(20, 25, 45)
    u_sh.line.color.rgb = SECONDARY
    u_sh.text_frame.word_wrap = True
    p_u = u_sh.text_frame.paragraphs[0]
    p_u.text = "You: What is photosynthesis? Explain it simply."
    p_u.font.name = 'Arial'; p_u.font.size = Pt(11); p_u.font.color.rgb = TEXT_MAIN

    # AI bubble
    a_sh = s7.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.2), Inches(4.0), Inches(4.8), Inches(1.4))
    a_sh.fill.solid(); a_sh.fill.fore_color.rgb = RGBColor(25, 20, 35)
    a_sh.line.color.rgb = PRIMARY
    a_sh.text_frame.word_wrap = True
    p_a = a_sh.text_frame.paragraphs[0]
    p_a.text = ("Arianna: Sure! 🌿 Photosynthesis is how plants make their own food. "
                "They use sunlight, water, and air to create sugar. "
                "It's like a plant cooking lunch using the sun as a stove!")
    p_a.font.name = 'Arial'; p_a.font.size = Pt(11); p_a.font.color.rgb = TEXT_MAIN

    draw_card(s7, Inches(6.8), Inches(2.0), Inches(5.7), Inches(4.2),
              "Why Arianna is Awesome ✨",
              "• Simple Answers: No big confusing words — just plain language!\n\n"
              "• Replies Instantly: No waiting like a Google search!\n\n"
              "• Feels Like a Friend: Like talking to someone who knows a lot.\n\n"
              "• Remembers the Chat: Ask follow-up questions and she remembers!")

    # ═══════════════════════════════════════════════════════════════════════
    # SLIDE 8 — Tech (kid-friendly)
    # ═══════════════════════════════════════════════════════════════════════
    s8 = add_slide_with_header("The Tech Behind Arianna", "Tech Stuff", 8)

    add_text(s8, "Don't worry — we will explain it like building with LEGO blocks! 🧱",
             Inches(0.8), Inches(1.8), Inches(11.733), Inches(0.5),
             size=13, align=PP_ALIGN.CENTER)

    draw_card(s8, Inches(0.8), Inches(2.5), Inches(3.6), Inches(3.8),
              "The Website 🌐 (Frontend)",
              "The chat screen you see and click on. Built with HTML, CSS, and JavaScript — "
              "the same languages that make all websites look pretty!")

    draw_card(s8, Inches(4.8), Inches(2.5), Inches(3.6), Inches(3.8),
              "The Engine ⚙️ (Backend)",
              "A hidden helper running on your computer using Python and FastAPI. "
              "It takes your message and passes it to the smart brain.")

    draw_card(s8, Inches(8.8), Inches(2.5), Inches(3.6), Inches(3.8),
              "The Brain 🧠 (Gemini AI)",
              "Google Gemini is the super-smart engine that thinks and creates the answer — "
              "like the world's biggest library plus the smartest librarian!")

    # ═══════════════════════════════════════════════════════════════════════
    # SLIDE 9 — Real-Time Streaming
    # ═══════════════════════════════════════════════════════════════════════
    s9 = add_slide_with_header("Watch Arianna Think in Real Time!", "Cool Feature", 9)

    left9 = s9.shapes.add_textbox(Inches(0.8), Inches(2.0), Inches(5.6), Inches(4.2))
    tf9 = left9.text_frame; tf9.word_wrap = True

    p9t = tf9.paragraphs[0]
    p9t.text = "Like Watching Someone Type!"
    p9t.font.name = 'Arial'; p9t.font.size = Pt(18)
    p9t.font.bold = True;    p9t.font.color.rgb = TEXT_MAIN
    p9t.space_after = Pt(10)

    p9d = tf9.add_paragraph()
    p9d.text = ("When you ask Arianna a question, you can watch the words appear one by one — "
                "like magic! This is called real-time streaming. You never stare at a blank screen!\n\n"
                "And if Arianna talks too much? Just click the red Stop button to make her stop!")
    p9d.font.name = 'Arial'; p9d.font.size = Pt(13); p9d.font.color.rgb = TEXT_MUTED

    draw_card(s9, Inches(6.8), Inches(2.0), Inches(5.7), Inches(4.2),
              "What Arianna Thinks Before Replying 🤔",
              "Thinking... 4 seconds\n\n"
              "Reading your question... searching knowledge... picking simple words... organizing answer...\n\n"
              "Then her answer appears word by word on your screen!")

    # ═══════════════════════════════════════════════════════════════════════
    # SLIDE 10 — App Design
    # ═══════════════════════════════════════════════════════════════════════
    s10 = add_slide_with_header("It Looks Amazing Too!", "App Design", 10)

    draw_card(s10, Inches(0.8), Inches(2.0), Inches(5.7), Inches(4.2),
              "Cool Design Features 🎨",
              "• Dark Mode: Easy on the eyes, especially at night!\n\n"
              "• Glowing Buttons: Hover over them and they light up!\n\n"
              "• Clean Fonts: Easy to read — like a modern phone app.\n\n"
              "• Smooth Animations: Everything slides and fades nicely.")

    right10 = s10.shapes.add_textbox(Inches(6.8), Inches(2.0), Inches(5.6), Inches(4.2))
    tf10 = right10.text_frame; tf10.word_wrap = True

    p10t = tf10.paragraphs[0]
    p10t.text = "Arianna's Color Palette"
    p10t.font.name = 'Arial'; p10t.font.size = Pt(18)
    p10t.font.bold = True;    p10t.font.color.rgb = TEXT_MAIN
    p10t.space_after = Pt(12)

    p10d = tf10.add_paragraph()
    p10d.text = "Each color has a meaning:\n• Dark Base = Background\n• Magic Purple = Arianna / AI\n• Deep Blue = You / User\n• Green = Good / Success\n• Red = Stop / Alert"
    p10d.font.name = 'Arial'; p10d.font.size = Pt(13); p10d.font.color.rgb = TEXT_MUTED

    # ═══════════════════════════════════════════════════════════════════════
    # SLIDE 11 — Who Is It For?
    # ═══════════════════════════════════════════════════════════════════════
    s11 = add_slide_with_header("Who Is Arianna AI For?", "Users", 11)

    draw_card(s11, Inches(0.8), Inches(2.2), Inches(3.6), Inches(3.8),
              "Students 📖",
              "Get homework help, essay tips, and explanations in simple language. "
              "No more hours of searching Google for a simple answer!")

    draw_card(s11, Inches(4.8), Inches(2.2), Inches(3.6), Inches(3.8),
              "Teachers 👩‍🏫",
              "Create lesson plans, quiz questions, or draft parent letters. "
              "Arianna helps teachers save lots of time on daily tasks!")

    draw_card(s11, Inches(8.8), Inches(2.2), Inches(3.6), Inches(3.8),
              "Small Businesses 🏪",
              "Need to write product descriptions or plan your business? "
              "Arianna helps small shop owners with everyday writing tasks!")

    # ═══════════════════════════════════════════════════════════════════════
    # SLIDE 12 — Comparison
    # ═══════════════════════════════════════════════════════════════════════
    s12 = add_slide_with_header("Arianna AI vs. Other Chatbots", "Why Arianna?", 12)

    rows, cols = 5, 4
    tbl_shape = s12.shapes.add_table(rows, cols, Inches(0.8), Inches(2.0), Inches(11.733), Inches(4.2))
    tbl = tbl_shape.table

    headers = ["Feature", "Hard AI Tools", "Other Chatbots", "Arianna AI"]
    hdr_colors = [TEXT_MAIN, DANGER, WARNING, SUCCESS]
    for i, (h, c) in enumerate(zip(headers, hdr_colors)):
        cell = tbl.cell(0, i)
        cell.fill.solid(); cell.fill.fore_color.rgb = CARD_BG
        p = cell.text_frame.paragraphs[0]
        p.text = h; p.font.name = 'Arial'; p.font.size = Pt(13)
        p.font.bold = True; p.font.color.rgb = c

    data12 = [
        ["Ease of Use",      "Lots of confusing settings.",       "OK but can be complicated.",    "Super simple! Just type! 😊"],
        ["Privacy",          "Chats stored on their servers.",     "May use your chats for training.", "Stays only on YOUR computer! 🔒"],
        ["Cost",             "Expensive subscriptions.",           "Monthly fees required.",         "Very affordable — use your own key! 💰"],
        ["Real-time Stream", "Answer only shown when fully done.", "Sometimes streams, sometimes not.", "Always streams word-by-word! ⚡"],
    ]

    for r, row in enumerate(data12):
        for c, val in enumerate(row):
            cell = tbl.cell(r + 1, c)
            cell.fill.solid(); cell.fill.fore_color.rgb = RGBColor(14, 12, 28)
            p = cell.text_frame.paragraphs[0]
            p.text = val; p.font.name = 'Arial'; p.font.size = Pt(11)
            p.font.color.rgb = TEXT_MAIN if (c == 0 or c == 3) else TEXT_MUTED
            p.font.bold = (c == 0)

    # ═══════════════════════════════════════════════════════════════════════
    # SLIDE 13 — Roadmap
    # ═══════════════════════════════════════════════════════════════════════
    s13 = add_slide_with_header("What's Coming Next?", "Roadmap", 13)

    draw_card(s13, Inches(0.8), Inches(2.2), Inches(3.6), Inches(3.8),
              "Phase 1: Chat (Now! ✅)",
              "The basic chatting with Arianna is already built!\n\n"
              "• Type questions and get answers.\n"
              "• Real-time word-by-word streaming.\n"
              "• Chats saved privately on your computer.",
              border_color=SUCCESS)

    draw_card(s13, Inches(4.8), Inches(2.2), Inches(3.6), Inches(3.8),
              "Phase 2: File Uploads 📄",
              "Upload PDF files and Arianna will read them!\n\n"
              "• Upload homework PDFs.\n"
              "• Ask questions about the file.\n"
              "• Download Arianna's summaries.",
              border_color=WARNING)

    draw_card(s13, Inches(8.8), Inches(2.2), Inches(3.6), Inches(3.8),
              "Phase 3: Voice Chat 🎙️",
              "Just speak to Arianna and she replies!\n\n"
              "• Talk instead of typing.\n"
              "• Hear Arianna's voice back.\n"
              "• Like having a real voice assistant!",
              border_color=PRIMARY)

    # ═══════════════════════════════════════════════════════════════════════
    # SLIDE 14 — Timeline
    # ═══════════════════════════════════════════════════════════════════════
    s14 = add_slide_with_header("Our 6-Month Plan", "Timeline", 14)

    add_text(s14, "Here is a simple plan showing what we will build and when!",
             Inches(0.8), Inches(1.8), Inches(11.733), Inches(0.5),
             size=13, align=PP_ALIGN.CENTER)

    line = s14.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.5), Inches(3.5), Inches(10.333), Inches(0.04))
    line.fill.solid(); line.fill.fore_color.rgb = CARD_BORDER; line.line.color.rgb = CARD_BORDER

    prog = s14.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.5), Inches(3.5), Inches(4.133), Inches(0.04))
    prog.fill.solid(); prog.fill.fore_color.rgb = PRIMARY; prog.line.color.rgb = PRIMARY

    nodes = [
        ("Month 1", "Build chat screen",     1.5,  True),
        ("Month 2", "Connect Arianna brain", 3.56, True),
        ("Month 3", "Test & fix bugs",       5.62, False),
        ("Month 4", "Add file uploads",      7.68, False),
        ("Month 5", "Add voice chat",        9.74, False),
        ("Month 6", "Launch! 🎉",            11.8, False),
    ]

    for title, desc, x, completed in nodes:
        dot = s14.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x - 0.15), Inches(3.37), Inches(0.3), Inches(0.3))
        dot.fill.solid()
        if completed:
            dot.fill.fore_color.rgb = PRIMARY; dot.line.color.rgb = PRIMARY
        else:
            dot.fill.fore_color.rgb = CARD_BG; dot.line.color.rgb = CARD_BORDER

        tb = s14.shapes.add_textbox(Inches(x - 0.9), Inches(3.8), Inches(1.8), Inches(1.2))
        tf = tb.text_frame; tf.word_wrap = True
        p_t = tf.paragraphs[0]
        p_t.alignment = PP_ALIGN.CENTER; p_t.text = title
        p_t.font.name = 'Arial'; p_t.font.size = Pt(12)
        p_t.font.bold = True;    p_t.font.color.rgb = TEXT_MAIN

        p_d = tf.add_paragraph()
        p_d.alignment = PP_ALIGN.CENTER; p_d.text = desc
        p_d.font.name = 'Arial'; p_d.font.size = Pt(9); p_d.font.color.rgb = TEXT_MUTED

    # ═══════════════════════════════════════════════════════════════════════
    # SLIDE 15 — Conclusion & Q&A
    # ═══════════════════════════════════════════════════════════════════════
    s15 = add_slide_with_header("Let's Build Arianna Together!", "Conclusion", 15)

    left15 = s15.shapes.add_textbox(Inches(0.8), Inches(2.0), Inches(5.6), Inches(4.2))
    tf15 = left15.text_frame; tf15.word_wrap = True

    p15a = tf15.paragraphs[0]
    p15a.text = "Arianna AI in One Sentence:"
    p15a.font.name = 'Arial'; p15a.font.size = Pt(20)
    p15a.font.bold = True;    p15a.font.color.rgb = TEXT_MAIN
    p15a.space_after = Pt(12)

    p15b = tf15.add_paragraph()
    p15b.text = ('"A super friendly chatbot that answers your questions simply, '
                 'privately, and instantly — powered by Google Gemini!"')
    p15b.font.name = 'Arial'; p15b.font.size = Pt(14)
    p15b.font.color.rgb = PRIMARY; p15b.font.italic = True
    p15b.space_after = Pt(20)

    p15c = tf15.add_paragraph()
    p15c.text = "Try it: http://localhost:8000\nContact: support@arianna.ai"
    p15c.font.name = 'Arial'; p15c.font.size = Pt(13)
    p15c.font.color.rgb = TEXT_MAIN; p15c.font.bold = True

    draw_card(s15, Inches(6.8), Inches(2.0), Inches(5.7), Inches(4.2),
              "Any Questions? 🙋",
              "Let's talk about:\n\n"
              "• How do we make Arianna even smarter?\n\n"
              "• What subjects should she be best at?\n\n"
              "• What new features would you love to see added?")

    # ── Save ─────────────────────────────────────────────────────────────────
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_path = os.path.join(parent_dir, "frontend", "arianna_ai_proposal.pptx")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    prs.save(output_path)
    print(f"Presentation saved to {output_path}")


if __name__ == "__main__":
    create_presentation()
