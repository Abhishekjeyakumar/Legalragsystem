"""
Script to generate a realistic sample legal PDF for testing the Legal RAG System.
Run once: python create_sample_pdf.py
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable, PageBreak
)
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT

OUTPUT_PATH = "data/Sample_Employment_Law_Act.pdf"

# ── Document content ──────────────────────────────────────────────────────────

TITLE = "EMPLOYMENT RIGHTS AND LABOUR STANDARDS ACT"
SUBTITLE = "A Comprehensive Statute Governing Employment Relations"
YEAR = "2024 Edition"

CONTENT = [
    # ── Preamble ──
    ("heading1", "PREAMBLE"),
    ("body", (
        "WHEREAS it is necessary to establish a comprehensive legal framework "
        "governing the rights and obligations of employers and employees; "
        "AND WHEREAS the protection of workers from exploitation and unfair "
        "treatment is a fundamental objective of this legislation; "
        "NOW THEREFORE, the following provisions shall constitute the "
        "Employment Rights and Labour Standards Act."
    )),

    # ── Part I ──
    ("heading1", "PART I — GENERAL PROVISIONS"),

    ("heading2", "Article 1 — Short Title and Commencement"),
    ("body", (
        "1.1 This Act may be cited as the Employment Rights and Labour "
        "Standards Act, hereinafter referred to as 'the Act'."
    )),
    ("body", (
        "1.2 This Act shall come into force on the date of its publication "
        "in the Official Gazette, unless otherwise specified by the competent authority."
    )),
    ("body", (
        "1.3 The provisions of this Act shall apply to all employment "
        "relationships within the jurisdiction, including those governed by "
        "contracts of service, apprenticeships, and fixed-term agreements."
    )),

    ("heading2", "Article 2 — Definitions"),
    ("body", (
        "2.1 For the purposes of this Act, the following definitions shall apply:"
    )),
    ("body", (
        "(a) 'Employee' means any natural person who has entered into or works "
        "under a contract of employment, whether written, oral, or implied, "
        "and includes apprentices and trainees."
    )),
    ("body", (
        "(b) 'Employer' means any person, company, corporation, or organisation "
        "that employs one or more employees under a contract of employment, "
        "and includes the successors and assigns of such employer."
    )),
    ("body", (
        "(c) 'Wages' means all remuneration payable to an employee in respect "
        "of work done or to be done, including basic salary, allowances, "
        "overtime pay, and any other monetary benefit."
    )),
    ("body", (
        "(d) 'Working hours' means the period during which an employee is "
        "required to be at the disposal of the employer and to carry out "
        "their activities or duties."
    )),
    ("body", (
        "(e) 'Termination' means the ending of an employment contract by "
        "either party, whether by notice, summary dismissal, resignation, "
        "redundancy, or expiry of a fixed term."
    )),

    ("heading2", "Article 3 — Scope of Application"),
    ("body", (
        "3.1 This Act applies to all employers and employees in both the "
        "public and private sectors, unless expressly excluded by specific provisions."
    )),
    ("body", (
        "3.2 The following categories are excluded from the scope of this Act: "
        "(a) members of the armed forces; (b) police officers on active duty; "
        "(c) domestic workers governed by a separate domestic workers statute."
    )),
    ("body", (
        "3.3 Where any other law provides greater benefits or protections to "
        "employees than those provided under this Act, such other law shall "
        "prevail to the extent of the greater benefit."
    )),

    # ── Part II ──
    ("heading1", "PART II — EMPLOYMENT CONTRACTS"),

    ("heading2", "Article 4 — Formation of Employment Contract"),
    ("body", (
        "4.1 An employment contract may be concluded in writing, orally, or "
        "by conduct. However, every employer shall provide each employee with "
        "a written statement of the main terms and conditions of employment "
        "within fourteen (14) days of commencement of employment."
    )),
    ("body", (
        "4.2 The written statement required under Article 4.1 shall include: "
        "(a) the names of the employer and employee; (b) the date of commencement; "
        "(c) the nature of the work; (d) the place of work; (e) the rate of wages; "
        "(f) the hours of work; (g) the duration of the contract if fixed-term."
    )),
    ("body", (
        "4.3 Any term or condition of an employment contract that is less "
        "favourable to the employee than the minimum standards prescribed by "
        "this Act shall be void and of no effect, and the minimum standard "
        "prescribed by this Act shall apply in its place."
    )),

    ("heading2", "Article 5 — Probationary Period"),
    ("body", (
        "5.1 An employment contract may include a probationary period not "
        "exceeding six (6) months, during which either party may terminate "
        "the contract with a minimum notice of one (1) week."
    )),
    ("body", (
        "5.2 The probationary period may be extended once by mutual written "
        "agreement for a further period not exceeding three (3) months, "
        "provided that the total probationary period does not exceed nine (9) months."
    )),
    ("body", (
        "5.3 During the probationary period, the employee shall be entitled "
        "to all rights and benefits under this Act, including the right to "
        "a safe working environment and protection from unlawful discrimination."
    )),

    # ── Part III ──
    ("heading1", "PART III — WAGES AND REMUNERATION"),

    ("heading2", "Article 6 — Minimum Wage"),
    ("body", (
        "6.1 No employer shall pay any employee a wage that is less than the "
        "national minimum wage as prescribed by the Minister from time to time "
        "by notice published in the Official Gazette."
    )),
    ("body", (
        "6.2 The national minimum wage shall be reviewed at least once every "
        "two (2) years by the Wages Advisory Board, taking into account the "
        "cost of living, economic conditions, and the need to maintain "
        "employment levels."
    )),
    ("body", (
        "6.3 Any employer who pays wages below the prescribed minimum wage "
        "shall be liable to pay the employee the difference between the wages "
        "paid and the minimum wage, together with interest at the prescribed rate."
    )),

    ("heading2", "Article 7 — Payment of Wages"),
    ("body", (
        "7.1 Wages shall be paid at regular intervals not exceeding one (1) month. "
        "The employer and employee may agree on a shorter payment interval."
    )),
    ("body", (
        "7.2 Wages shall be paid on a working day and at or before the end of "
        "the agreed pay period. Payment shall be made in legal tender or by "
        "electronic transfer to a bank account designated by the employee."
    )),
    ("body", (
        "7.3 An employer shall not make any deduction from an employee's wages "
        "except: (a) deductions required by law (taxes, social security); "
        "(b) deductions authorised in writing by the employee; "
        "(c) deductions for overpayment of wages made in error."
    )),
    ("body", (
        "7.4 The total amount of deductions authorised under Article 7.3(b) "
        "shall not exceed twenty-five percent (25%) of the employee's net wages "
        "in any pay period."
    )),

    # ── Part IV ──
    ("heading1", "PART IV — WORKING HOURS AND REST PERIODS"),

    ("heading2", "Article 8 — Maximum Working Hours"),
    ("body", (
        "8.1 The normal working hours of an employee shall not exceed eight (8) "
        "hours per day or forty (40) hours per week, excluding meal breaks."
    )),
    ("body", (
        "8.2 An employer may require an employee to work overtime beyond the "
        "normal working hours, provided that the total working hours including "
        "overtime shall not exceed twelve (12) hours per day or sixty (60) "
        "hours per week."
    )),
    ("body", (
        "8.3 Overtime work shall be compensated at a rate not less than one "
        "and one-half (1.5) times the employee's normal hourly rate. Work "
        "performed on public holidays shall be compensated at double (2.0) "
        "the normal hourly rate."
    )),

    ("heading2", "Article 9 — Rest Periods and Breaks"),
    ("body", (
        "9.1 Every employee shall be entitled to a rest break of not less than "
        "thirty (30) minutes after every five (5) consecutive hours of work. "
        "This break shall not be counted as working time."
    )),
    ("body", (
        "9.2 Every employee shall be entitled to a minimum rest period of "
        "eleven (11) consecutive hours between the end of one working day "
        "and the commencement of the next."
    )),
    ("body", (
        "9.3 Every employee shall be entitled to at least one (1) full day of "
        "rest per week, which shall ordinarily be Sunday unless otherwise "
        "agreed in writing between the employer and employee."
    )),

    # ── Part V ──
    ("heading1", "PART V — LEAVE ENTITLEMENTS"),

    ("heading2", "Article 10 — Annual Leave"),
    ("body", (
        "10.1 Every employee who has completed twelve (12) months of continuous "
        "employment shall be entitled to a minimum of twenty-one (21) working "
        "days of paid annual leave per year."
    )),
    ("body", (
        "10.2 Annual leave shall be taken at a time mutually agreed between "
        "the employer and employee. The employer shall not unreasonably refuse "
        "a request for annual leave."
    )),
    ("body", (
        "10.3 An employee shall not be required to work during annual leave. "
        "Any agreement to work during annual leave shall be void and of no effect."
    )),
    ("body", (
        "10.4 Upon termination of employment, an employee shall be entitled "
        "to payment in lieu of any accrued but untaken annual leave, calculated "
        "at the employee's daily rate of pay."
    )),

    ("heading2", "Article 11 — Sick Leave"),
    ("body", (
        "11.1 Every employee shall be entitled to a minimum of ten (10) working "
        "days of paid sick leave per year, upon production of a medical "
        "certificate from a registered medical practitioner."
    )),
    ("body", (
        "11.2 An employee who is absent from work due to illness for more than "
        "two (2) consecutive days shall be required to produce a medical "
        "certificate to the employer within forty-eight (48) hours of return to work."
    )),
    ("body", (
        "11.3 An employer shall not dismiss an employee solely on the grounds "
        "of illness, provided that the employee has not exhausted their sick "
        "leave entitlement and the illness does not render the employee "
        "permanently incapable of performing their duties."
    )),

    ("heading2", "Article 12 — Maternity and Paternity Leave"),
    ("body", (
        "12.1 A female employee shall be entitled to maternity leave of not "
        "less than fourteen (14) weeks, of which at least six (6) weeks shall "
        "be taken after the birth of the child."
    )),
    ("body", (
        "12.2 During maternity leave, the employee shall be entitled to receive "
        "her full wages for the first eight (8) weeks and not less than "
        "sixty-six percent (66%) of her wages for the remaining period."
    )),
    ("body", (
        "12.3 A male employee shall be entitled to paternity leave of not less "
        "than five (5) working days at full pay, to be taken within four (4) "
        "weeks of the birth of his child."
    )),
    ("body", (
        "12.4 An employer shall not dismiss or give notice of dismissal to a "
        "female employee during her maternity leave or within six (6) months "
        "after her return from maternity leave."
    )),

    # ── Part VI ──
    ("heading1", "PART VI — TERMINATION OF EMPLOYMENT"),

    ("heading2", "Article 13 — Notice of Termination"),
    ("body", (
        "13.1 Either party wishing to terminate an employment contract shall "
        "give the other party written notice of termination. The minimum notice "
        "periods are as follows: (a) one (1) week for employment of less than "
        "six months; (b) two (2) weeks for employment of six months to two years; "
        "(c) four (4) weeks for employment of more than two years."
    )),
    ("body", (
        "13.2 An employer may pay the employee wages in lieu of notice instead "
        "of requiring the employee to work during the notice period. The payment "
        "in lieu shall be equivalent to the wages the employee would have earned "
        "during the notice period."
    )),
    ("body", (
        "13.3 Notice of termination shall be given in writing and shall state "
        "the reason for termination and the effective date of termination."
    )),

    ("heading2", "Article 14 — Unfair Dismissal"),
    ("body", (
        "14.1 An employer shall not dismiss an employee without a valid and "
        "fair reason. Valid reasons for dismissal include: (a) misconduct; "
        "(b) poor performance; (c) incapacity; (d) operational requirements "
        "(redundancy)."
    )),
    ("body", (
        "14.2 Before dismissing an employee for misconduct or poor performance, "
        "the employer shall follow a fair procedure, which includes: "
        "(a) informing the employee of the allegations; (b) giving the employee "
        "an opportunity to respond; (c) conducting a fair investigation."
    )),
    ("body", (
        "14.3 An employee who has been unfairly dismissed may lodge a complaint "
        "with the Labour Tribunal within ninety (90) days of the date of dismissal. "
        "The Tribunal may order reinstatement, re-engagement, or compensation."
    )),
    ("body", (
        "14.4 Compensation for unfair dismissal shall not exceed twenty-four (24) "
        "months' wages. In determining the amount of compensation, the Tribunal "
        "shall consider the employee's length of service, the circumstances of "
        "the dismissal, and the employee's efforts to find alternative employment."
    )),

    ("heading2", "Article 15 — Severance Pay"),
    ("body", (
        "15.1 An employee who is dismissed by reason of redundancy or whose "
        "employment is terminated by the employer for reasons other than "
        "misconduct shall be entitled to severance pay."
    )),
    ("body", (
        "15.2 Severance pay shall be calculated at the rate of not less than "
        "fifteen (15) days' wages for each completed year of service, "
        "subject to a maximum of twelve (12) months' wages."
    )),
    ("body", (
        "15.3 Severance pay shall be paid within thirty (30) days of the "
        "effective date of termination. Failure to pay severance pay within "
        "this period shall attract interest at the prescribed rate."
    )),

    # ── Part VII ──
    ("heading1", "PART VII — HEALTH, SAFETY AND WELFARE"),

    ("heading2", "Article 16 — Employer's Duty of Care"),
    ("body", (
        "16.1 Every employer shall take all reasonably practicable steps to "
        "ensure the health, safety, and welfare of all employees at the workplace. "
        "This duty includes providing and maintaining safe plant and equipment, "
        "safe systems of work, and a safe working environment."
    )),
    ("body", (
        "16.2 Every employer shall conduct a risk assessment of the workplace "
        "at least once every two (2) years and implement measures to eliminate "
        "or minimise identified risks."
    )),
    ("body", (
        "16.3 An employer shall not require or permit an employee to perform "
        "work that poses an imminent and serious risk to the employee's health "
        "or safety. An employee may refuse to perform such work without "
        "suffering any adverse consequences."
    )),

    ("heading2", "Article 17 — Workplace Injuries and Compensation"),
    ("body", (
        "17.1 An employee who sustains an injury or contracts a disease in the "
        "course of employment shall be entitled to compensation in accordance "
        "with the Workers' Compensation Act."
    )),
    ("body", (
        "17.2 Every employer shall maintain adequate workers' compensation "
        "insurance coverage for all employees. Failure to maintain such "
        "insurance shall render the employer personally liable for all "
        "compensation claims."
    )),

    # ── Part VIII ──
    ("heading1", "PART VIII — ANTI-DISCRIMINATION AND EQUAL OPPORTUNITY"),

    ("heading2", "Article 18 — Prohibition of Discrimination"),
    ("body", (
        "18.1 No employer shall discriminate against any employee or job "
        "applicant on the grounds of race, colour, sex, gender, religion, "
        "national origin, disability, age, marital status, pregnancy, "
        "or political opinion."
    )),
    ("body", (
        "18.2 Discrimination includes: (a) direct discrimination — treating "
        "a person less favourably because of a protected characteristic; "
        "(b) indirect discrimination — applying a provision, criterion, or "
        "practice that disadvantages persons with a protected characteristic."
    )),
    ("body", (
        "18.3 An employee who believes they have been subjected to discrimination "
        "may file a complaint with the Equal Opportunity Commission within "
        "one hundred and eighty (180) days of the discriminatory act."
    )),

    ("heading2", "Article 19 — Equal Pay"),
    ("body", (
        "19.1 Every employer shall pay male and female employees equal wages "
        "for work of equal value. Differences in wages based solely on sex "
        "are prohibited."
    )),
    ("body", (
        "19.2 In determining whether work is of equal value, regard shall be "
        "had to the nature of the work, the conditions under which it is "
        "performed, the qualifications required, and the effort and responsibility involved."
    )),

    # ── Part IX ──
    ("heading1", "PART IX — ENFORCEMENT AND PENALTIES"),

    ("heading2", "Article 20 — Labour Inspectorate"),
    ("body", (
        "20.1 The Minister shall appoint Labour Inspectors who shall have the "
        "power to enter any workplace at any reasonable time to inspect "
        "compliance with this Act."
    )),
    ("body", (
        "20.2 Labour Inspectors may examine records, interview employees and "
        "employers, and issue compliance notices requiring employers to remedy "
        "any contravention of this Act within a specified period."
    )),

    ("heading2", "Article 21 — Penalties"),
    ("body", (
        "21.1 Any employer who contravenes any provision of this Act shall be "
        "guilty of an offence and liable on conviction to a fine not exceeding "
        "fifty thousand dollars ($50,000) or imprisonment for a term not "
        "exceeding two (2) years, or both."
    )),
    ("body", (
        "21.2 Where the offence is a continuing one, the employer shall be "
        "liable to an additional fine not exceeding five hundred dollars ($500) "
        "for each day the offence continues after conviction."
    )),
    ("body", (
        "21.3 In addition to any criminal penalty, an employer found to have "
        "contravened this Act may be ordered by the Labour Tribunal to pay "
        "compensation to the affected employee."
    )),

    # ── Part X ──
    ("heading1", "PART X — MISCELLANEOUS PROVISIONS"),

    ("heading2", "Article 22 — Record Keeping"),
    ("body", (
        "22.1 Every employer shall keep accurate records of all employees, "
        "including their names, addresses, dates of commencement, wages paid, "
        "hours worked, and leave taken. Such records shall be retained for "
        "a minimum of five (5) years."
    )),
    ("body", (
        "22.2 An employee shall have the right to inspect their own employment "
        "records at any reasonable time and to obtain copies thereof."
    )),

    ("heading2", "Article 23 — Dispute Resolution"),
    ("body", (
        "23.1 Any dispute arising from the interpretation or application of "
        "this Act shall first be referred to conciliation before the Labour "
        "Relations Commission. If conciliation fails, the dispute may be "
        "referred to the Labour Tribunal for adjudication."
    )),
    ("body", (
        "23.2 The Labour Tribunal shall have jurisdiction to hear and determine "
        "all disputes relating to employment rights under this Act. "
        "The Tribunal's decisions shall be final and binding on both parties, "
        "subject to appeal to the High Court on questions of law only."
    )),

    ("heading2", "Article 24 — Savings and Transitional Provisions"),
    ("body", (
        "24.1 Any employment contract in existence at the commencement of this "
        "Act shall be deemed to be modified to the extent necessary to comply "
        "with the provisions of this Act."
    )),
    ("body", (
        "24.2 Any proceedings commenced under the previous employment legislation "
        "shall continue and be concluded under that legislation as if this Act "
        "had not been enacted."
    )),

    ("heading2", "Article 25 — Repeal"),
    ("body", (
        "25.1 The Employment Act (Chapter 47) and the Labour Standards Act "
        "(Chapter 52) are hereby repealed. Any subsidiary legislation made "
        "under those Acts shall remain in force until revoked or replaced "
        "under this Act."
    )),
]


def build_pdf():
    doc = SimpleDocTemplate(
        OUTPUT_PATH,
        pagesize=A4,
        rightMargin=2.5 * cm,
        leftMargin=2.5 * cm,
        topMargin=2.5 * cm,
        bottomMargin=2.5 * cm,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "LegalTitle",
        parent=styles["Title"],
        fontSize=18,
        textColor=colors.HexColor("#0a1628"),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName="Helvetica-Bold",
    )
    subtitle_style = ParagraphStyle(
        "LegalSubtitle",
        parent=styles["Normal"],
        fontSize=11,
        textColor=colors.HexColor("#1a3a5c"),
        spaceAfter=4,
        alignment=TA_CENTER,
        fontName="Helvetica-Oblique",
    )
    h1_style = ParagraphStyle(
        "LegalH1",
        parent=styles["Heading1"],
        fontSize=13,
        textColor=colors.HexColor("#0a1628"),
        spaceBefore=18,
        spaceAfter=8,
        fontName="Helvetica-Bold",
        borderPad=4,
        backColor=colors.HexColor("#e8f0f8"),
        borderWidth=0,
        leftIndent=0,
    )
    h2_style = ParagraphStyle(
        "LegalH2",
        parent=styles["Heading2"],
        fontSize=11,
        textColor=colors.HexColor("#1a3a5c"),
        spaceBefore=12,
        spaceAfter=6,
        fontName="Helvetica-Bold",
    )
    body_style = ParagraphStyle(
        "LegalBody",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#1a1a1a"),
        spaceAfter=6,
        leading=15,
        alignment=TA_JUSTIFY,
        fontName="Helvetica",
        leftIndent=12,
    )

    story = []

    # Title page
    story.append(Spacer(1, 1.5 * cm))
    story.append(Paragraph(TITLE, title_style))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(SUBTITLE, subtitle_style))
    story.append(Paragraph(YEAR, subtitle_style))
    story.append(Spacer(1, 0.5 * cm))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#c9a84c")))
    story.append(Spacer(1, 0.5 * cm))

    # Body content
    for kind, text in CONTENT:
        if kind == "heading1":
            story.append(Spacer(1, 0.3 * cm))
            story.append(Paragraph(text, h1_style))
        elif kind == "heading2":
            story.append(Paragraph(text, h2_style))
        elif kind == "body":
            story.append(Paragraph(text, body_style))

    doc.build(story)
    print(f"PDF created: {OUTPUT_PATH}")


if __name__ == "__main__":
    build_pdf()
