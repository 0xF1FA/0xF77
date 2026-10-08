from pathlib import Path
from html import escape
import json
import math
from reportlab.pdfgen import canvas
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph,
    Spacer, PageBreak, Table, TableStyle, Preformatted, KeepTogether)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Polygon
from report_data import FEATURES, CANDIDATES, SOURCES

ROOT=Path(__file__).parent
OUT=ROOT/'output/pdf/0xF77-CARBON-research-report.pdf'
OUT.parent.mkdir(parents=True,exist_ok=True)
for name,file in [('Body','DejaVuSerif.ttf'),('Sans','DejaVuSans.ttf'),
                  ('SansB','DejaVuSans-Bold.ttf'),('Mono','DejaVuSansMono.ttf')]:
    pdfmetrics.registerFont(TTFont(name,'/usr/share/fonts/truetype/dejavu/'+file))
INK=colors.HexColor('#172B2A'); TEAL=colors.HexColor('#176A60')
RUST=colors.HexColor('#B35035'); PALE=colors.HexColor('#EDF4F0')
MUTED=colors.HexColor('#546762'); RULE=colors.HexColor('#B7C9C3')
W,H=612,792
styles={
 'body':ParagraphStyle('body',fontName='Body',fontSize=9.4,leading=13.7,spaceAfter=8,textColor=INK),
 'small':ParagraphStyle('small',fontName='Sans',fontSize=8,leading=11.2,spaceAfter=6,textColor=MUTED),
 'h1':ParagraphStyle('h1',fontName='SansB',fontSize=22,leading=27,spaceAfter=16,textColor=INK),
 'h2':ParagraphStyle('h2',fontName='SansB',fontSize=12.5,leading=17,spaceBefore=10,spaceAfter=7,textColor=TEAL),
 'h3':ParagraphStyle('h3',fontName='SansB',fontSize=10.5,leading=14,spaceBefore=8,spaceAfter=5,textColor=INK),
 'cell':ParagraphStyle('cell',fontName='Sans',fontSize=8,leading=10.8,textColor=INK),
 'head':ParagraphStyle('head',fontName='SansB',fontSize=8,leading=10.5,textColor=colors.white),
 'code':ParagraphStyle('code',fontName='Mono',fontSize=8,leading=11.8,spaceAfter=10,textColor=INK,
       backColor=PALE,borderPadding=9),
 'label':ParagraphStyle('label',fontName='SansB',fontSize=8.5,leading=11,spaceAfter=8,textColor=RUST),
 'title':ParagraphStyle('title',fontName='SansB',fontSize=49,leading=53,textColor=INK,spaceAfter=14),
 'deck':ParagraphStyle('deck',fontName='Body',fontSize=17,leading=23,textColor=TEAL,spaceAfter=20),
}
pdfmetrics.registerFontFamily('Body',normal='Body',bold='SansB',italic='Body',boldItalic='SansB')
pdfmetrics.registerFontFamily('Sans',normal='Sans',bold='SansB',italic='Sans',boldItalic='SansB')
story=[]
def p(s,kind='body'):
    story.append(Paragraph(s,styles[kind]))
def h(s): p(s,'h2')
def page(title,kicker='0xF77 / RESEARCH AND DESIGN'):
    if story: story.append(PageBreak())
    p(kicker,'label'); p(title,'h1')
def code(s): story.append(Preformatted(s,styles['code']))
def table(headers,rows,widths):
    data=[[Paragraph(escape(str(x)),styles['head']) for x in headers]]
    data += [[Paragraph(escape(str(x)),styles['cell']) for x in row] for row in rows]
    t=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT')
    t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),TEAL),('VALIGN',(0,0),(-1,-1),'TOP'),
        ('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),
        ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,PALE]),
        ('LINEBELOW',(0,-1),(-1,-1),0.6,RULE)]))
    story.append(t);story.append(Spacer(1,10))
def arrow(d,x1,y1,x2,y2,color=TEAL):
    d.add(Line(x1,y1,x2,y2,strokeColor=color,strokeWidth=1.5))
    a=math.atan2(y2-y1,x2-x1); b=6
    pts=[x2,y2,x2-b*math.cos(a-.45),y2-b*math.sin(a-.45),
         x2-b*math.cos(a+.45),y2-b*math.sin(a+.45)]
    d.add(Polygon(pts,fillColor=color,strokeColor=color))
def topology():
    d=Drawing(516,260)
    def box(x,y,w,ht,title,sub):
        d.add(Rect(x,y,w,ht,rx=5,fillColor=PALE,strokeColor=RULE))
        d.add(String(x+w/2,y+ht-20,title,fontName='SansB',fontSize=11,textAnchor='middle',fillColor=INK))
        d.add(String(x+w/2,y+14,sub,fontName='Sans',fontSize=8.1,textAnchor='middle',fillColor=MUTED))
    box(25,175,206,59,'PLATE: 32 INTEGER words','native FORMAT + data + word 26')
    box(285,175,205,59,'Native formatted WRITE','copy / mark / decimal / repair')
    box(285,61,205,59,'External character record','next format and next marks')
    box(25,61,206,59,'A4 absorption','record becomes numeric words')
    arrow(d,231,204,285,204)
    arrow(d,387,175,387,120)
    arrow(d,285,90,231,90)
    arrow(d,127,120,127,175)
    d.add(String(83,144,'next tick',fontName='Sans',fontSize=8,fillColor=TEAL,textAnchor='middle'))
    d.add(String(393,144,'fresh record',fontName='Sans',fontSize=8,fillColor=TEAL))
    d.add(String(25,24,'Checkpoint: the same 32 words form one unformatted spool record.',
                 fontName='Sans',fontSize=9,fillColor=RUST))
    return d

page('CARBON','0xF77 / EXPLORATION DOSSIER / UPDATED 08 OCTOBER 2026')
story[-1]=Paragraph('CARBON',styles['title'])
p('A printout that rewrites the machine<br/>that will print it next.','deck')
p('The strongest opening is in the boundary between a numeric word, a character record and a native FORMAT. CARBON gives the same integer array all three roles. Its printed number changes a positioning instruction; that instruction moves a mark; the mark changes the number. The complete state can be put on a native unformatted spool and restarted in another process.')
story.append(topology())
table(['Delivered','Evidence'],[
 ('28 mechanisms / 10 distinct concepts','Historical classification, affordance map and nine-criterion ranking'),
 ('One selected architecture','72-line fixed-form engine and an inspectable 128-column specimen'),
 ('37 checks passed','Three optimization levels, restart equivalence, feedback ablation and dialect rejection'),
 ('One unexpected seam','Internal and external legacy A input disagree on the measured toolchain'),
],[182,334])
p('<b>Classification:</b> executable research prototype; F77-era compatibility machine, not strict ANSI FORTRAN 77. The architecture is a proposed synthesis. General computational power, historical priority and cross-compiler portability remain unproved.','small')
p('Revision 2 incorporates the later CARBON II GitHub research. The closing update records its independently reproduced 1,584 traces, the recovered baseline, and the runtime explanation of the comma seam. Historical results remain separately identified.','small')

page('What the investigation establishes')
h('The language boundary is the design material')
p('The brief excludes the obvious label-addressed virtual machine. This design has no assigned GOTO program counter, alternate-return scheduler, COMMON-backed RAM, EQUIVALENCE heap or user-defined instruction decoder. The host advances generations. The compiler runtime interprets an existing language: FORMAT. Its ordinary record-editing machinery creates the next generation of its own grammar.')
p('The selected mechanism is stronger than a character-string self-printer. A four-character field is also a live numeric word, and its numeric value changes subsequent layout. Eliminating that feedback destroys the observed cycle. Thus the representation boundary is causally necessary to this specimen, not an ornamental historical spelling.')
h('Four categories must remain separate')
table(['Category','Meaning in this report'],[
 ('Standard F77','A mechanism present in the language, such as external formatted records, T positioning and output H editing.'),
 ('Compatibility extension','Numeric-array FORMAT, numeric Hollerith storage and noncharacter A editing. Appendix C is guidance, not a claim of standard conformance.'),
 ('Processor convention','Word width, byte order, ABI, binary framing and archive behavior. A named profile is required.'),
 ('Unestablished behavior','A measured discrepancy or proposed composition whose general rule has not been shown. It remains a question, not alternate physics by declaration.'),
],[125,391])
p('A successful -std=legacy build is not a strict F77 certificate. GNU has no -std=f77 mode. Conversely, obsolescent does not mean deleted: modern Fortran retains many old mechanisms. Claims about modern standard status below use the public Fortran 2023 draft as the baseline. [S01-S03]')
h('Nearest predecessors, and the actual novelty claim')
p('Bratley and Millo published a FORTRAN self-reproducing card-image program in 1972. Carlini\'s IOCCC 2020 entry implements game logic through iterated printf formatting. Neither self-reproduction nor computation in formatting is new. [S35,S36]')
p('CARBON\'s proposed contribution is a compact, restartable specimen in which native numeric FORMAT, character absorption into words, decimal overprinting and physical record state form one exposed loop. This is an engineering synthesis to investigate. The searches performed do not establish that nobody has built the same combination before.')

for start in range(0,len(FEATURES),3):
    page('Feature archaeology %02d-%02d'%(start+1,min(start+3,len(FEATURES))),
         '01 / MECHANISMS, PROVENANCE AND ARCHITECTURAL CONSEQUENCES')
    for fid,name,intent,law,gnu,weird,compose in FEATURES[start:start+3]:
        h(fid+'  '+escape(name))
        p('<b>Original purpose.</b> '+escape(intent))
        p('<b>Historical and modern status.</b> '+escape(law))
        p('<b>GNU support.</b> '+escape(gnu))
        p('<b>Unusual affordance.</b> '+escape(weird))
        p('<b>Composition and architecture.</b> '+escape(compose))
    if start==27:
        h('A boundary against attractive mistakes')
        p('Undefined behavior is not an undocumented instruction set. An experiment can preserve a surprising outcome without granting it stability. A useful dialect law needs a specified compiler/runtime, a small reproducer, an optimization check, and a clear account of which behavior is merely observed.')
        p('The architecture does not need to extract control flow from a crash, reuse a dangling ENTRY argument, read uninitialized padding, write through a constant actual argument, or assume that every logical operand is evaluated. Those ideas would buy uncertainty rather than a coherent machine.')

page('Strange affordance map','02 / COMPOSITIONS')
p('These are architectural combinations, not a bag of interchangeable tricks. "Observed" refers to the supplied CARBON experiment; the remaining rows are design hypotheses or documented primitives awaiting composition tests.')
table(['Mechanisms','What the combination could make','Status / boundary'],[
 ('11 + 12 + 07 + 09','A numeric format prints, patches and reabsorbs its successor.','Observed: CARBON rewrite loop.'),
 ('12 + I editing + 07','Raw text words become decimal ink that changes a future field position.','Observed: feedback changes T102 to T108.'),
 ('11 + 13 + 14','Executable state survives as a native record and resumes in another process.','Observed: reload frame 4, reproduce its future.'),
 ('04 + 05 + 06','A record array is a native formatting workspace with list-driven row tiling.','Standard mechanisms; multi-record machine proposed.'),
 ('07 + 08 + 04','Several numeric lenses read the same spatial field, producing distinct feedback dynamics.','Proposed; blank and exponent rules must be explicit.'),
 ('01 + 02 + 03','One deck exposes different code and state planes under selected compiler profiles.','Proposed: CARD REEF.'),
 ('16 + 17 + 18','Linking assembles initial worlds and reveals which data fragments exist.','Proposed: RELIQUARY; verify archive extraction.'),
 ('19 + 20 + 22','A saved segment has several named entrances with distinct valid arguments.','Proposed; no implicit coroutine stack.'),
 ('15 + 21','Record geometry and array sequence views become a spatial data instrument.','Proposed; obey extent and connection rules.'),
 ('25 + 13','Raw records and the accumulated printed page have different histories.','Proposed: physical rendering needs a named model.'),
 ('26 + 18 + 13','Executable rooms replace one another while a limited state spine survives.','Proposed; requires an actual overlay manager.'),
 ('27 + 19','Missing fields become native sparse updates to defined persistent cells.','Proposed: NULL GARDEN.'),
],[120,226,170])
p('The strongest triangle is representation + spatial editing + record persistence. The other mechanisms are entrances for future experiments, not dependencies that the flagship must accumulate.','small')

for lo,hi in [(0,5),(5,10)]:
    page('Ten distinct artifacts / '+str(lo+1)+'-'+str(hi),'03 / CANDIDATE GENERATION')
    for key,name,tag,desc,risk,scores in CANDIDATES[lo:hi]:
        h(key+'  '+name+' / '+tag)
        p(escape(desc))
        p('<b>Failure test.</b> '+escape(risk),'small')

page('Ranked shortlist','04 / SELECTION')
p('Scores are design judgments from 1 (weak) to 5 (strong), not measured probabilities. Each of the nine criteria has equal weight. A concept must also have a credible local prototype path; a high total cannot conceal an unavailable substrate.')
ranked=sorted(CANDIDATES,key=lambda x:-sum(x[-1]))
table(['Artifact','W','F','D','E','C','X','A','M','S','/45'],
      [[c[1]]+c[-1]+[sum(c[-1])] for c in ranked],
      [166]+[31]*9+[71])
p('W: WTF factor; F: FORTRAN specificity; D: depth; E: extensibility; C: coherence; X: executability; A: archaeological value; M: modern contrast; S: surprise potential.','small')
h('1. CARBON / 43')
p('It gives an observer a concrete impossible-looking event: changing a printed mark changes a number, which edits the instruction that will print the next mark. A 72-line driver exposes the entire mechanism. The source representation and the binary spool can both be inspected. Its depth score remains four because larger composition has not been demonstrated.')
h('2. RELIQUARY / 40')
p('It turns build composition into a persistent-world operation and offers fertile seams for linker specialists. It deserves an independent small experiment: two disjoint initializer fragments, an archive, and three link maps. It loses priority because archive-driven data selection has substantial analogues outside Fortran.')
h('3. CARD REEF / 40')
p('It makes source geometry part of the object rather than an aesthetic. A strong prototype would demonstrate a genuine two-plane deck and a controlled change of compiler projection. RELIQUARY wins the tie on coherence and depth; CARD REEF is more immediately visible but easier to reduce to a familiar quine.')
p('DIALECT ZOO is the natural research environment around these artifacts. GHOST TYPEWRITER has an excellent historical seam but fails the immediate gfortran execution gate. Neither is substituted for the selected working machine.','small')

page('The selected architecture','05 / CARBON')
p('CARBON is a self-rewriting record transducer and a specimen laboratory. Its live object is a 32-word INTEGER array called PLATE. Its public surface is the exact 128-character plate, its numeric word values and its native checkpoint spool. It can be read as a tiny language, a printing mechanism, a dynamical system or an executable file format.')
story.append(topology())
table(['Physical region','Role'],[
 ('Columns 1-58','The native FORMAT text. It is stored across INTEGER words, not a CHARACTER format variable.'),
 ('Column 29','The mutable final digit of T102 / T108. This determines a future mark position.'),
 ('Columns 100-109','A ten-character field cleared to zeroes and marked by the current format.'),
 ('Word 26 = columns 101-104','A numeric feedback tap over four characters in that field.'),
 ('All 32 words','Complete transition state and the payload of one unformatted snapshot record.'),
],[162,354])
h('What the user experiences')
p('Run sh run.sh, see the instruction alternate between T102 and T108, and watch the mark follow one tick later. Open the seed and the exact frame images. Stop the process, resume frame 4 from the binary spool, and get the same future. Change one literal in a copied specimen and discover whether it settles, cycles or fails to parse.')
p('The current capability is real but bounded: self-directed format rewriting, inspectable evolution and exact same-profile restart. It is not yet a general-purpose language, a cellular-automaton platform or a useful database.')

page('One tick, with the machinery exposed','05 / CARBON / TRANSITION')
p('The seed is a 128-column record, padded with spaces except for a zero-filled field at columns 100-109. Its operative grammar occupies the first 58 columns:')
code('(32A4,T100,10H0000000000,T102,1H1,T20,I10,T20,9H00000,T10)')
table(['Step inside native WRITE','Effect on the fresh output record'],[
 ('32A4','Consume the 32 integer words as raw four-character fields, copying the entire current plate.'),
 ('T100,10H0000000000','Clear the ten-column mark field.'),
 ('T102,1H1','Place the mark at the current instruction\'s chosen column. In another state this is T108.'),
 ('T20,I10','Consume the additional item PLATE(26), printing its decimal integer value into columns 20-29.'),
 ('T20,9H00000,T10','Restore columns 20-28. The last decimal digit in column 29 survives as part of the next positioning instruction.'),
],[176,340])
p('The format is read from the old PLATE while a separate external record is written. Only after formatting finishes does A4 input absorb the new record into PLATE. There is no in-place mutation of an active format object and no conflicting dummy-argument write.')
code('      REWIND 11\n      WRITE(11,PLATE) PLATE,PLATE(26)\n      REWIND 11\n      READ(11,\'(32A4)\') PLATE')
p('The host adds bounded iteration, error checks, a one-record check and persistence. It does not parse FORMAT, compute a modulo, select T102/T108, increment a state register, or implement an opcode table. Native I/O performs the transition. The complete driver is in core/carbon.f.')
h('Why the numbers move the mark')
p('On the measured little-endian, four-byte ASCII profile, the field 0000 represents the integer 808464432; the field 0100 represents 808464688. Their last decimal digits are 2 and 8. I10 followed by a nine-character repair extracts that last digit spatially. The extraction occurs through printing and overprinting, not through arithmetic in the driver. These values are experiment-derived, not universal Fortran constants.')

page('State, time and evidence','05 / CARBON / OBSERVED BEHAVIOR')
table(['Frame','Next target','Mark field','Word 26'],[
 ('0 / seed','102','0000000000','808464432'),
 ('1','102','0010000000','808464688'),
 ('2','108','0010000000','808464688'),
 ('3','108','0000000010','808464432'),
 ('4','102','0000000010','808464432'),
 ('5 = frame 1','102','0010000000','808464688'),
],[65,90,190,171])
p('A four-state orbit follows a one-step transient. Looking only at the mark hides half the state: two successive frames can display the same mark while carrying different instructions. This is a useful demonstration of why output, state and transition law cannot be casually separated here.')
h('Persistence is the same object in another medium')
p('Each snapshot writes PLATE as one native unformatted record. On this run the payload was 128 bytes with a four-byte marker on either side. The test verified every payload against the corresponding text frame. A fresh process loaded frame 4 and reproduced frames 4-12 exactly. The driver\'s displayed tick count restarts; it is not part of the machine state. [S14; E02]')
p('This is not an arbitrary-process checkpoint. It saves a deliberately complete plate state. It makes no promise about atomic writes after power loss, portable record markers, foreign byte order or preservation of compiler-runtime internals.')
h('A useful failed optimization')
p('An attempted shortcut replaced the external record with an internal CHARACTER file while retaining A editing into INTEGER. The same plate then lost or displaced commas and failed as a format. A smaller reproducer reads (I4,I4) through 4A4: the external route preserved the text; the internal route produced (I4 I followed by blanks. [E03]')
p('The original investigation left the cause unresolved. The later CARBON II work reduced the symptom to ordinary CHARACTER input and located the legacy comma-scanning path in GNU runtime source. Its static GNU 13.3 controls were reproduced on 08 October; the baseline also reproduced with an explicitly selected shared 14.2 runtime. Under GNU/f95 controls the CHARACTER read preserves commas. The closing update distinguishes this finding from the baseline\'s nonstandard A-to-INTEGER transfer and corrects the earlier runtime attribution. [S39-S41]')

page('Why this substrate matters','05 / CARBON / BOUNDARIES AND SEAMS')
h('Modern Fortran can compute the same result')
p('A claim that modern Fortran cannot reproduce CARBON would be false. Character formats, positional editing and record I/O survive. TRANSFER can explicitly recreate the bit-pattern bridge, and quoted literals can replace output H editing. A modern implementation can therefore reproduce the finite-state experiment. [S34]')
p('What changes is the native object model: standard modern I/O does not accept an INTEGER array as the format expression and does not make ordinary A editing the standard text/number bridge. A faithful port must name that representation operation and preserve the selected byte/word rules. The tested strict-F2018 compiler rejection isolates the numeric-format boundary. Merely translating fixed form to free form is not the necessary transformation.')
h('The counterfactual that matters')
p('If PLATE becomes ordinary text and word 26 becomes the decimal number spelled by four digits, 0000 becomes zero rather than 808464432. That is a different dynamical system. If the words remain numerically meaningful via an explicit representation conversion, the programmer has deliberately preserved the old machine. The historical semantics carry identity, not exclusive computational power.')
h('Exposed intervention points')
table(['Seam','Contribution that would count'],[
 ('specimens/','A new plate with a different measured transition, full state trace and a minimal explanation of its native descriptors.'),
 ('core/','A new I/O-list contract or multi-record mode with causal tests showing why the added machinery is necessary.'),
 ('dialects/','A compiler/runtime profile with word widths, character encoding, flags and exact observed semantics.'),
 ('experiments/','A minimized counterexample, including a failed idea that helps map a boundary.'),
 ('evidence/','Compiler identity, exact records, failures, source digest and recurrence/restart checks.'),
 ('PHENOMENA.md','What happens, why if known, standard status, scope of observation, stability and possible compositions.'),
],[111,405])
p('The host should stay small. Avoid a layer of generic opcodes that hides the native formatting rules. A pretty viewer may point to fields and words, but the raw plate and record framing remain first-class evidence.')

page('Smallest proof and actual results','06 / FALSIFIABLE PROTOTYPE')
h('The experiment to run before building a platform')
p('Use one 128-character seed, one 32-word state array, one numeric feedback tap and one external scratch record. Execute 12 transitions; write both textual frames and native unformatted snapshots. Reload a middle frame in a fresh process. A successful run needs changing grammar as well as a changing visible mark.')
table(['Claim','Falsification condition','Observed result'],[
 ('Native feedback drives the orbit','Replacing the feedback word with a constant still gives the same orbit.','Ablation settles to one state; feedback is causal.'),
 ('State is complete','A new process produces a different suffix after loading a saved frame.','Frame 4 plus eight steps matches uninterrupted frames 4-12.'),
 ('The specimen is stable on this profile','-O0, -O2 and -O3 differ with runtime checks enabled.','All three produce identical complete frame sequences.'),
 ('Representation is explicit','Eight-byte default INTEGER silently runs the four-byte specimen.','The profile guard rejects the altered word size.'),
 ('Old syntax materially matters','Strict F2018 accepts the isolated numeric FORMAT expression.','Compiler rejects it; the test contains no Hollerith constant.'),
 ('I/O route is interchangeable','Internal A absorption exactly matches the external route.','False on this toolchain; reduced counterexample retained.'),
],[124,206,186])
p('<b>Measured result:</b> 37/37 checks passed. These include build/run checks and several independent behavioral assertions, not 37 independent machines or compilers. Compiler: GNU Fortran 13.3.0 (Ubuntu), x86-64 Linux, 2026-10-07. <b>Runtime correction, 08 October:</b> the original report named the installed libgfortran5 14.2 package without a linkage witness. The recovered build selects the static GNU 13.3 archive. Separately recorded new runs pass with both that archive and an explicitly bound shared 14.2 library.')
h('Run it')
code('cd baseline/carbon\nsh run.sh\npython3 tests/check.py\n\n# After the first run, restart from a saved frame:\nmkdir -p build/resumed\ncd build/resumed\nprintf \'1 8 4\\n../demo/spool.dat\\n\' | ../carbon')
p('The archive includes source, the seed, checks, exact evidence and a small dialect document. Compiler packages and generated executables are not bundled. This is local experimental software for deliberate specimens; the runner is not a sandbox for arbitrary formats.','small')

page('Someone will eventually discover...','07 / PREDICTIONS, NOT COMPLETED FEATURES')
predictions=[
 ('A plate can compute through a different decimal window.',
  'I10 plus nine-column repair currently keeps one trailing digit. Other widths and repair masks may select several digits or convert word values into multiple descriptor parameters. First probe: produce two changing T positions using two taps and compare the complete orbit.'),
 ('Literal lengths can change what counts as grammar.',
  'Editing an H count could expose punctuation previously swallowed as literal data, or hide active descriptors inside the literal body. First probe: two valid formats that alternate between those interpretations without ever passing through malformed syntax.'),
 ('A pair of records can couple through native format reversion.',
  'Two plates might write fragments of one another using the I/O list and a multi-record contract. The current driver intentionally rejects more than one output record. First probe: a documented two-record transducer whose coupling survives an ablation test.'),
 ('Another runtime turns the failed internal route into a different machine.',
  'The comma discrepancy may be a compatibility rule, implementation detail or defect. First probe: run the minimized program on a second GNU runtime and a different compiler; inspect the runtime source before assigning a universal explanation.'),
 ('A seed can be an object-file artifact rather than a text file.',
  'A BLOCK DATA seed could initialize a plate, and a snapshot could be emitted as a new initializer unit. This would join CARBON to RELIQUARY. First probe: explicit object linking with one initialized block, then controlled archive extraction. No duplicate definitions.'),
 ('Word boundaries are an active coupling topology.',
  'Moving a field by one column changes which bytes share the numeric tap. A word-boundary editor might reveal phase changes without changing the visible glyph vocabulary. First probe: sweep offsets and record cycles, fixed points and parse failures.'),
 ('The printout can acquire an additional physical interpretation.',
  'A carriage-control rendering could make several records occupy the same visible row while the machine still keeps them distinct. First probe: retain the raw spool alongside a precisely specified renderer; test which observations disappear when records overprint.'),
 ('A contributor will find a useful non-oscillatory specimen.',
  'The decisive extension would be a native-format selector, small counter, checksum-like transform or coupled pattern generator with a clear external use. Require a causal explanation and an input/output test, rather than declaring universality from visual complexity.'),
]
for name,body in predictions[:4]: h(name);p(body)
p('These predictions identify visible attachment points. They are not a promise that all eight constructions are possible under the existing one-record contract.','small')
page('More doors into the machine room','07 / PREDICTIONS CONTINUED')
for name,body in predictions[4:]: h(name);p(body)
h('A phenomenon record should stay small')
p('Record the symptom, exact specimen, compiler and runtime, flags, encoding and word profile, expected versus observed records, standard/extension status, repeatability, known cause or explicit uncertainty, and the architectural consequence. Include one composition to try next. A failed experiment belongs here when it closes a plausible door.')
p('The repository should invite one new mechanism per contribution. A newcomer can first run the specimen, then inspect the plate, then add a reduced experiment. No framework rewrite is necessary to add a new dialect finding or another plate.')

page('Open questions and next work','08 / RESEARCH FRONTIER')
questions=[
 ('Runtime semantics','The GNU 13.3 source and CHARACTER controls explain the legacy comma path. Which additional runtime versions retain it, and what other input descriptors or character kinds expose different behavior?'),
 ('Independent implementation','Does a second compiler support all three legacy bridges with the same record result? Which requires explicit vendor switches?'),
 ('Representation physics','How do byte order, character encoding and word width change the orbit under an intentionally adapted profile? The current program rejects incompatible profiles; it does not simulate them.'),
 ('Expressive capability','Can two causal feedback taps form a useful gate, counter or selector without adding application-level arithmetic? What is the reachable-state structure?'),
 ('Grammar boundaries','Can varying H counts or descriptor widths produce valid, stable syntax-changing specimens rather than only parser failures?'),
 ('Format caching','When and how do runtimes cache variable formats? Does changing an array at the same address reliably trigger interpretation of new content? The supplied run worked; other runtimes are untested.'),
 ('Record topology','Which multi-record or direct-access compositions are conforming, and which require explicit extensions? Can a meaningful lattice use native reversion?'),
 ('Persistence','Which compiler/runtime and conversion-option changes preserve a spool? What header and external manifest would make mismatches detectable before loading?'),
 ('Linkage','Does the old g77 EXTERNAL/BLOCK DATA archive technique work on selected current gfortran/linker combinations, including LTO and dead-section collection?'),
 ('Historical priority','What closer FORTRAN format-driven automata or evolving quines exist in manuals, recreational-computing journals or surviving program libraries? The search is not exhaustive.'),
]
table(['Question','Experiment needed'],questions,[111,405])
h('The next three increments')
p('The 08 October update advances the first two steps: the baseline was recovered and retested on static 13.3 and shared 14.2 runtimes; CARBON II supplies useful pattern and parity transitions. The next step is an external record store with stable writes and explicit host services, followed by another compiler implementation and compact raw-symbol encodings. The original predictions remain invitations, not claims that every proposed construction now exists.')
p('Do not build a general language workbench yet. The next success criterion is one outsider-supplied trick that adds capability while making the native machinery easier to inspect.')

for group, (start, stop) in enumerate([(0,10),(10,19),(19,28),(28,38)], 1):
    page('Primary-source register / '+str(group),'REFERENCES / ACCESSED 07 OCTOBER 2026')
    p('Source markers identify documentation or prior work. E01-E03 identify original experiments in the accompanying archive. Proposed architectural consequences and candidate scores are this report\'s inferences. Vendor manuals describe extensions alongside standard forms; their titles are not conformance guarantees.','small')
    for sid,title,url,note in SOURCES[start:stop]:
        p('<b>['+sid+'] '+escape(title)+'</b><br/>'+escape(note)+'<br/>'+
          '<link href="'+escape(url,quote=True)+'" color="#176A60">'+escape(url)+'</link>','small')

page('What GitHub added overnight','09 / FORWARD WORK / 08 OCTOBER 2026')
p('The repository now contains a draft research branch, research/carbon-ii-20261008, pinned at 5db3e835d2d14ceeef414ae5910a565a08a05bbc. Its CARBON II research was produced after the original exploration. Main still contained only the license when checked. The branch is substantial forward work, not evidence that the original architecture should be discarded. [S41]')
h('A FORMAT description becomes a state selector')
code('      READ(TABLE,STATE) ROW\n      READ(ROW,SYMBOL) STATE')
p('TABLE contains a finite transition relation assembled before execution. STATE is a 32-character FORMAT description selecting a row. SYMBOL is another FORMAT description selecting a successor description within that row. Reading the successor replaces STATE, so it determines the next row selection. Fortran\'s native parser and positional A editing perform both selections.')
p('The host runs a finite DO clock, transports input and logs state. Python assembles the records and checks expected traces outside the Fortran transition path. There is no state arithmetic, conditional dispatch or state-indexed application array access inside that path. Selecting a field from a record is still a lookup; assigning it to FORMAT does not make selection disappear.')
table(['Artifact','Distinct causal mechanism'],[
 ('CARBON baseline','Numeric word bits become a decimal digit that rewrites a positioning instruction. One integer object is native FORMAT, data, feedback and checkpoint.'),
 ('CARBON II','Character FORMAT descriptions select rows and successor programs from records. This standard CHARACTER route does not require the baseline\'s numeric storage bridges.'),
 ('Shared substrate','Native formatting, record position and mutable executable descriptions. Each experiment keeps its host clock explicit.'),
],[121,395])
h('What the new capability buys')
p('The supplied examples recognize whether an a-b pattern has appeared and compute cumulative parity of raw binary digits. The pattern input is pre-encoded as selector descriptions; the separate parity specimen handles raw digits. The new suite also demonstrates list-exhaustion control, bounded reversion, indirect addresses, syntax construction, shifts and recurrent composition of individually idempotent maps.')
p('<b>Boundary:</b> the table is 8,192 characters, the row 512, and the program cell 32. The assembler permits at most 16 symbols and states x symbols x 32 &lt;= 8,192. These are finite-state machines with bounded spatial memory and an explicit host clock. No growing tape, general autonomous predicate instruction, unbounded stack or universality is established.','small')

page('The evidence chain is now complete','09 / REPRODUCTION AND RUNTIME PHYSICS')
h('Reproduced, rather than accepted on reputation')
table(['Measurement','08 October result'],[
 ('CARBON II finite tables','528 traces at each of -O0, -O2 and -O3; 1,584 passed. Corpus hashes match the published run.'),
 ('External controls','Five representative automata per optimization level passed. The full 528-trace corpus remains internal.'),
 ('Demos','Internal and external pattern demos passed; raw parity 10110100111 produced 11011000101.'),
 ('Recovered baseline','37/37 checks passed with static GNU 13.3; another 37/37 passed with shared libgfortran 14.2.'),
 ('Historical payloads','frames.txt, spool.dat, trace.txt and internal-a.txt exactly match the original bytes under both baseline runtime bindings.'),
],[132,384])
p('The recovered baseline retains the original 72-line source, tests, specimen and evidence without edits. A wrapper copies it to a temporary directory before rerunning checks, so a new observation cannot silently overwrite the original measurements. The 07 October date embedded in the old harness is a historical report label; the wrapper records the new observation timestamp, compiler command and runtime linkage.')
p('<b>Provenance correction:</b> the original report inferred the runtime from an installed 14.2 package. The recovered compiler setup has no unversioned shared-library link and falls back to its static 13.3 archive. The new shared-14.2 experiment explicitly supplies that link and records the actual core\'s loaded-library path and hash. Historical baseline documentation is retained as evidence; this update corrects its runtime label.','small')
h('The comma is compiler physics, not a numeric-storage requirement')
p('For ordinary CHARACTER input containing AB,CDXYZ, -std=legacy internal A8 reads produced AB followed by spaces, while external A8 preserved the full text. With -std=gnu and -std=f95, both media preserved it. The comma-containing internal transducer failed in legacy mode; the colon vocabulary passed. Both outcomes remain in evidence.')
p('GNU 13.3 transfer.c selects a comma-scanning internal-input path when the legacy compile options disable standard warnings. That path does not consult the character-read comma flag. read.c clears that flag for A editing; the external transfer path checks it. The exact source blobs match CARBON II\'s audit. This explains the CHARACTER control and supports the causal account of the inherited seam; it is not proof about every GNU release. [S39-S40]')
p('The alternative colon representation is valid because the colon descriptor has no terminating effect while an I/O-list item remains. It changes the machine\'s written vocabulary while preserving the demonstrated finite-table behavior. The result shows one shared construction across media; it does not establish expressive equivalence of all internal and external record machines.')

page('Recovered baseline and next experiments','09 / HANDOFF AND PRIMARY EVIDENCE')
h('The forward work remains intact')
p('The reconciliation follow-up builds on the existing CARBON II research branch. It adds baseline/carbon/, tools/reverify_baseline.py, RECONCILIATION.md and separately dated evidence. Its branch is research/carbon-reconciled-20261008; the existing draft PR #1 remains separate. The historical CARBON II results.json and source audit remain unchanged. The original brief\'s feature archaeology, candidate ranking and architecture stay in this report, with the new findings explicitly updating the frontier.')
h('Three useful next experiments')
p('<b>Stable writable record memory:</b> demonstrate a FORMAT-selected address that can be read, overwritten and read again without host transition logic. Then investigate capacity growth separately. List REWIND, REC=, allocation and record creation as host services, rather than calling them edit descriptors.')
p('<b>Another implementation:</b> test a second compiler/runtime and preserve the same source, records and flags wherever possible. Separate parse acceptance, descriptor behavior, numeric storage extensions and binary spool compatibility. A second GNU runtime version is not an independent compiler implementation.')
p('<b>Input representation:</b> investigate compact raw-symbol selectors and comma-driven rewriting. Compare full states and retain failures. The present pattern assembler supplies executable selectors; the parity specimen demonstrates one raw-digit route, not a general raw-input compiler.')
h('Primary additions to the source register')
for sid,title,url,note in [
 ('S39','GNU 13.3 libgfortran/io/transfer.c','https://github.com/gcc-mirror/gcc/blob/releases/gcc-13.3.0/libgfortran/io/transfer.c','Inspected blob ebad096eeabf7f914751f27711efbee93db9dda6. Compare read_sf_internal and read_sf; the latter checks sf_read_comma.'),
 ('S40','GNU 13.3 libgfortran/io/read.c','https://github.com/gcc-mirror/gcc/blob/releases/gcc-13.3.0/libgfortran/io/read.c','Inspected blob bf2500fc5d050b392144feccbc257ec649dc73b8. read_a disables comma separation during character reads.'),
 ('S41','CARBON II source and evidence','https://github.com/0xF1FA/0xF77/tree/5db3e835d2d14ceeef414ae5910a565a08a05bbc','Private source repository. Draft PR #1; specimens, instruction_set.csv, assessment.md and evidence/results.json. Independently rerun in this workspace on 08 October.'),
]:
    p('<b>['+sid+'] '+escape(title)+'</b><br/>'+escape(note)+'<br/>'+
      '<link href="'+escape(url,quote=True)+'" color="#176A60">'+escape(url)+'</link>','small')
p('The result is still a provocation engine. The next contribution should add one capability while exposing its native mechanism. The recovered numeric plate and the newer character selectors give outsiders two distinct doors into the same machine room.')

class NumberedCanvas(canvas.Canvas):
    def __init__(self,*a,**k):
        canvas.Canvas.__init__(self,*a,**k);self._saved=[]
    def showPage(self):
        self._saved.append(dict(self.__dict__));self._startPage()
    def save(self):
        count=len(self._saved)
        for st in self._saved:
            self.__dict__.update(st)
            self.setStrokeColor(RULE);self.setLineWidth(.5)
            self.line(48,43,564,43)
            self.setFillColor(MUTED);self.setFont('Sans',7.5)
            self.drawString(48,29,'0xF77  /  CARBON + CARBON II  /  REVISION 2 / 2026-10-08')
            self.drawRightString(564,29,f'{self._pageNumber:02d} / {count:02d}')
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

doc=BaseDocTemplate(str(OUT),pagesize=(W,H),leftMargin=48,rightMargin=48,
                    topMargin=43,bottomMargin=57,title='0xF77: CARBON - research and design',
                    author='0xF77 research',subject='Fortran archaeology and a working native FORMAT record machine')
doc.addPageTemplates([PageTemplate(id='main',frames=[Frame(48,57,516,692,
    leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)])])
doc.build(story,canvasmaker=NumberedCanvas)
print(OUT)
