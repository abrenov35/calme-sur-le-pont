from reportlab.lib.pagesizes import A5
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, 
                                  PageBreak, Image, HRFlowable, KeepTogether)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.platypus.flowables import Flowable
from PIL import Image as PILImage
import os, io

# A5 dimensions
W, H = A5  # 148 x 210 mm

# Margins
ML = MR = 15*mm
MT = 18*mm
MB = 18*mm

# ── Image paths (mapped to chapters) ──────────────────────────────────────
IMG = {
    "cover":        "/mnt/user-data/uploads/IMG_E6E60110-8955-4C0A-B8C1-715E06811BC7.jpeg",  # Image 3 - page de titre
    "art_barre":    "/mnt/user-data/uploads/IMG_A1B3D048-7FA5-42B3-B57A-6CB5161A1A92.jpeg",  # L'Art de tenir la barre
    "preambule":    "/mnt/user-data/uploads/IMG_C5E09905-EAF7-4288-8BAC-6BC7E25E788F.jpeg",  # Image 1 - préambule
    "ch1":          "/mnt/user-data/uploads/IMG_C208DC8F-B7E8-4A05-A5C9-6CAFBA648090.jpeg",
    "ch2":          "/mnt/user-data/uploads/IMG_EF3E5530-5DE8-440C-978E-CE11643D6EF9.jpeg",
    "ch3":          "/mnt/user-data/uploads/IMG_D15303C1-EF41-406A-A589-DEF5EDDD1B73.jpeg",
    "ch4":          "/mnt/user-data/uploads/IMG_BDF95AD7-A8DD-4C0C-9464-979C39570313.jpeg",
    "ch4bis":       "/mnt/user-data/uploads/IMG_A72F1A61-F8CC-452C-8CCB-6B9725B06B95.jpeg",
    "ch5":          "/mnt/user-data/uploads/IMG_F1459D8B-EA86-4DF1-81A7-4B50BCCC25AD.jpeg",  # Image 2 - long cours
    "epilogue":     "/mnt/user-data/uploads/IMG_B304B62C-8B4B-46E7-BC27-F96B4B7FCEDB.jpeg",
}

def make_img(key, width_mm=118):
    """Return a ReportLab Image flowable, proportionally sized."""
    path = IMG[key]
    pil = PILImage.open(path)
    w, h = pil.size
    ratio = h / w
    rl_w = width_mm * mm
    rl_h = rl_w * ratio
    return Image(path, width=rl_w, height=rl_h)

# ── Styles ─────────────────────────────────────────────────────────────────
def styles():
    base_font = "Helvetica"   # fallback; will look like clean serif-ish

    S = {}

    S["cover_title"] = ParagraphStyle("cover_title",
        fontName="Helvetica-Bold", fontSize=22, leading=28,
        alignment=TA_CENTER, textColor=colors.HexColor("#1a1a1a"),
        spaceAfter=6)

    S["cover_sub"] = ParagraphStyle("cover_sub",
        fontName="Helvetica-Oblique", fontSize=11, leading=15,
        alignment=TA_CENTER, textColor=colors.HexColor("#444444"),
        spaceAfter=4)

    S["cover_author"] = ParagraphStyle("cover_author",
        fontName="Helvetica", fontSize=12, leading=16,
        alignment=TA_CENTER, textColor=colors.HexColor("#1a1a1a"),
        spaceAfter=4)

    S["cover_collab"] = ParagraphStyle("cover_collab",
        fontName="Helvetica-Oblique", fontSize=9, leading=13,
        alignment=TA_CENTER, textColor=colors.HexColor("#777777"),
        spaceAfter=0)

    S["quote"] = ParagraphStyle("quote",
        fontName="Helvetica-Oblique", fontSize=9, leading=14,
        alignment=TA_CENTER, textColor=colors.HexColor("#555555"),
        spaceAfter=3, leftIndent=10*mm, rightIndent=10*mm)

    S["quote_attr"] = ParagraphStyle("quote_attr",
        fontName="Helvetica", fontSize=9, leading=13,
        alignment=TA_CENTER, textColor=colors.HexColor("#555555"),
        spaceAfter=0)

    S["section_label"] = ParagraphStyle("section_label",
        fontName="Helvetica", fontSize=8, leading=12,
        alignment=TA_CENTER, textColor=colors.HexColor("#888888"),
        spaceAfter=2, spaceBefore=0, tracking=2)

    S["chapter_title"] = ParagraphStyle("chapter_title",
        fontName="Helvetica-Bold", fontSize=15, leading=20,
        alignment=TA_CENTER, textColor=colors.HexColor("#1a1a1a"),
        spaceAfter=10, spaceBefore=4)

    S["body"] = ParagraphStyle("body",
        fontName="Helvetica", fontSize=10, leading=16,
        alignment=TA_JUSTIFY, textColor=colors.HexColor("#1a1a1a"),
        spaceAfter=8, firstLineIndent=0)

    S["body_intro"] = ParagraphStyle("body_intro",
        fontName="Helvetica", fontSize=10, leading=16,
        alignment=TA_JUSTIFY, textColor=colors.HexColor("#1a1a1a"),
        spaceAfter=8, firstLineIndent=0)

    S["italic_body"] = ParagraphStyle("italic_body",
        fontName="Helvetica-Oblique", fontSize=10, leading=16,
        alignment=TA_JUSTIFY, textColor=colors.HexColor("#1a1a1a"),
        spaceAfter=8)

    S["closing_quote"] = ParagraphStyle("closing_quote",
        fontName="Helvetica-Oblique", fontSize=11, leading=16,
        alignment=TA_CENTER, textColor=colors.HexColor("#444444"),
        spaceAfter=0, spaceBefore=10)

    S["back_title"] = ParagraphStyle("back_title",
        fontName="Helvetica-Bold", fontSize=13, leading=18,
        alignment=TA_CENTER, textColor=colors.HexColor("#1a1a1a"),
        spaceAfter=8)

    S["back_body"] = ParagraphStyle("back_body",
        fontName="Helvetica", fontSize=9.5, leading=15,
        alignment=TA_JUSTIFY, textColor=colors.HexColor("#222222"),
        spaceAfter=8)

    S["back_author"] = ParagraphStyle("back_author",
        fontName="Helvetica-Bold", fontSize=10, leading=14,
        alignment=TA_CENTER, textColor=colors.HexColor("#1a1a1a"),
        spaceAfter=0)

    return S

# ── Thin decorative rule ───────────────────────────────────────────────────
def rule():
    return HRFlowable(width="80%", thickness=0.5, color=colors.HexColor("#cccccc"),
                      spaceAfter=8, spaceBefore=2)

# ── Build story ────────────────────────────────────────────────────────────
def build():
    S = styles()
    story = []
    sp = lambda n: Spacer(1, n*mm)

    # ── PAGE DE TITRE ──────────────────────────────────────────────────────
    story += [
        sp(10),
        Paragraph("LE CALME SUR LE PONT", S["cover_title"]),
        sp(3),
        rule(),
        sp(3),
        Paragraph("Chroniques maritimes sur le bruit du monde<br/>et la sérénité des horizons", S["cover_sub"]),
        sp(6),
        make_img("cover", width_mm=108),
        sp(6),
        Paragraph("Younès Belgnaoui", S["cover_author"]),
        sp(2),
        Paragraph("Coécrit au fil d'un voyage avec Claude, Gemini et ChatGPT.", S["cover_collab"]),
        PageBreak(),
    ]

    # ── PAGE BLANCHE ──────────────────────────────────────────────────────
    story += [sp(1), PageBreak()]

    # ── PAGE CITATION + TITRE INTÉRIEUR ───────────────────────────────────
    story += [
        sp(18),
        Paragraph("LE CALME SUR LE PONT", S["cover_title"]),
        sp(3),
        rule(),
        sp(3),
        Paragraph("Chroniques maritimes sur le bruit du monde<br/>et la sérénité des horizons", S["cover_sub"]),
        sp(14),
        Paragraph("« Tout marin, pour dompter les vents et les courants,<br/>met tour à tour le cap sur des points différents. »", S["quote"]),
        sp(1),
        Paragraph("— Victor Hugo", S["quote_attr"]),
        sp(10),
        Paragraph("Younès Belgnaoui", S["cover_author"]),
        sp(1),
        Paragraph("Coécrit au fil d'un voyage avec Claude, Gemini et ChatGPT.", S["cover_collab"]),
        PageBreak(),
    ]

    # ── L'ART DE TENIR LA BARRE ───────────────────────────────────────────
    story += [
        sp(8),
        Paragraph("L'ART DE TENIR LA BARRE", S["chapter_title"]),
        rule(),
        sp(4),
        Paragraph("Bien avant que le navire ne prenne le large, il faut comprendre une chose essentielle : le Capitaine n'est pas un individu seul, mais une fonction. C'est une part de nous-mêmes, un état d'esprit que l'on enfile comme une vareuse lorsque les vents forcent ou, plus difficilement, lorsque la mer devient d'huile.", S["body"]),
        Paragraph("Sur ce navire, le rôle du Capitaine n'est pas de tout diriger, mais de savoir protéger la « cabine ». C'est cet endroit — réel ou symbolique — où l'on se réfugie pour préserver sa clarté, pour anticiper les courants plutôt que de subir chaque clapotis, et pour ne pas laisser le tumulte du pont dicter la route.", S["body"]),
        Paragraph("Certains d'entre nous sont des Capitaines nés : ils excellent dans l'action brute, là où la tempête exige des décisions immédiates. Ils sont les rois du large, les maîtres des manœuvres complexes. Pourtant, ces mêmes Capitaines se trouvent parfois démunis face au calme plat, là où l'absence d'urgence devient, paradoxalement, une source d'angoisse.", S["body"]),
        Paragraph("Ce livre n'est pas le récit d'une personne en particulier, mais le voyage d'une conscience. Il explore cette quête permanente : comment rester maître de son cap, que l'on soit en pleine tempête ou dans le silence trompeur des jours sans vent.", S["body"]),
        Paragraph("À travers ces chroniques, le Capitaine observe, prépare, protège et veille. Mais il découvre surtout que le véritable leadership ne consiste pas à être le plus fort dans la tourmente, mais à être celui qui, par sa seule présence apaisée, permet à tout l'équipage de naviguer avec sérénité.", S["body"]),
        Paragraph("Peu importe qui tient la barre, ce qui compte, c'est de savoir quand se retirer dans sa cabine, quand écouter le bruit de fond, et quand décider, en toute conscience, que le navire est prêt à affronter l'océan.", S["body"]),
        sp(4),
        Paragraph("Embarquez. Vous y reconnaîtrez peut-être le Capitaine qui sommeille en vous.", S["italic_body"]),
        sp(6),
        make_img("art_barre"),
        PageBreak(),
    ]

    # ── PRÉAMBULE ─────────────────────────────────────────────────────────
    story += [
        sp(6),
        Paragraph("PRÉAMBULE", S["section_label"]),
        Paragraph("L'HÉRITAGE DU LARGE", S["chapter_title"]),
        rule(),
        sp(4),
        Paragraph("Bien avant que notre Capitaine ne tienne la barre, un autre navire ouvrait la route.", S["body"]),
        Paragraph("C'était un bâtiment imposant, connu de tous les marins de la région. Lorsque les vents forçaient ou que les brumes recouvraient la mer, sa simple présence suffisait souvent à rassurer les autres équipages.", S["body"]),
        Paragraph("Pendant des années, il traversa les saisons sans jamais quitter sa mission.", S["body"]),
        Paragraph("Puis vint le jour où il prit la direction du large.", S["body"]),
        Paragraph("Sa silhouette s'éloigna peu à peu jusqu'à disparaître derrière l'horizon.", S["body"]),
        Paragraph("La mer resta la même. Les vents continuèrent de souffler. Les étoiles poursuivirent leur course au-dessus des mâts.", S["body"]),
        Paragraph("Mais pour ceux qui restaient, quelque chose avait changé.", S["body"]),
        Paragraph("Les navires durent apprendre à poursuivre leur route sans ce repère familier.", S["body"]),
        Paragraph("Parmi eux se trouvait un jeune capitaine.", S["body"]),
        Paragraph("Il n'avait ni l'expérience ni la renommée de son prédécesseur. Pourtant, il possédait une qualité particulière : il observait.", S["body"]),
        Paragraph("Il remarquait les détails que d'autres laissaient passer. Une voile légèrement détendue. Un cordage usé. Un changement de vent presque imperceptible. Une réserve qui diminuait plus vite que prévu.", S["body"]),
        Paragraph("Avec les années, cette attention constante devint une habitude.", S["body"]),
        Paragraph("Chaque soir, il préparait le lendemain. Chaque traversée commençait bien avant le départ.", S["body"]),
        Paragraph("Peu à peu, les marins apprirent à lui faire confiance.", S["body"]),
        Paragraph("Et lorsqu'ils regardaient sa manière de tenir le cap, certains retrouvaient parfois quelque chose de familier.", S["body"]),
        Paragraph("Comme un sillage ancien qui continuait d'avancer sous la surface.", S["body"]),
        Paragraph("Comme un héritage transmis par la mer elle-même.", S["body"]),
        sp(6),
        make_img("preambule"),
        PageBreak(),
    ]

    # ── CHAPITRE 1 ────────────────────────────────────────────────────────
    story += [
        sp(6),
        Paragraph("CHAPITRE 1", S["section_label"]),
        Paragraph("LE DON DU CAPITAINE", S["chapter_title"]),
        rule(),
        sp(4),
        Paragraph("Le soleil n'était pas encore levé lorsque le Capitaine monta sur le pont.", S["body"]),
        Paragraph("Une légère brume flottait au-dessus de l'eau. Le port sommeillait encore tandis que les derniers préparatifs du départ s'achevaient dans le calme.", S["body"]),
        Paragraph("Comme avant chaque traversée, il parcourut lentement le navire.", S["body"]),
        Paragraph("Il observa les amarres. Examina les voiles. Inspecta les cales. Vérifia les réserves.", S["body"]),
        Paragraph("Ce rituel pouvait sembler excessif. Pourtant, il remarquait souvent ce que personne d'autre n'avait vu.", S["body"]),
        Paragraph("Ce matin-là, une caisse de matériel avait été arrimée du mauvais côté de la cale.", S["body"]),
        Paragraph("L'erreur paraissait insignifiante. Elle fut simplement déplacée.", S["body"]),
        Paragraph("Quelques heures plus tard, la mer se forma davantage que prévu. Le navire prit de la gîte. Plusieurs chargements glissèrent légèrement sous l'effet du roulis.", S["body"]),
        Paragraph("Tous, sauf celui qui avait été corrigé avant le départ.", S["body"]),
        Paragraph("La traversée se poursuivit sans incident.", S["body"]),
        Paragraph("Au fil de la journée, le Capitaine fit également remplacer une poulie qui commençait à fatiguer, vérifier les réserves d'eau douce et renforcer un cordage dont les fibres montraient des signes d'usure.", S["body"]),
        Paragraph("Rien d'extraordinaire. Seulement une succession d'ajustements modestes.", S["body"]),
        Paragraph("Lorsque le soleil commença à disparaître derrière l'horizon, le navire poursuivait sa route avec la même régularité qu'au matin.", S["body"]),
        Paragraph("Le Capitaine tenait la barre en silence.", S["body"]),
        Paragraph("Au loin, quelques oiseaux tournaient lentement au-dessus des vagues. Il observa leur trajectoire et modifia légèrement le cap.", S["body"]),
        Paragraph("Personne ne posa de question.", S["body"]),
        Paragraph("À bord, chacun savait désormais que certaines difficultés étaient souvent résolues bien avant d'apparaître.", S["body"]),
        sp(6),
        make_img("ch1"),
        PageBreak(),
    ]

    # ── CHAPITRE 2 ────────────────────────────────────────────────────────
    story += [
        sp(6),
        Paragraph("CHAPITRE 2", S["section_label"]),
        Paragraph("LE CALME SUR LE PONT", S["chapter_title"]),
        rule(),
        sp(4),
        Paragraph("La mer était si calme que les nuages semblaient flotter à sa surface.", S["body"]),
        Paragraph("Depuis l'aube, le navire avançait sous un vent régulier. Les voiles étaient parfaitement établies. Les cordages demeuraient immobiles. Rien ne troublait la traversée.", S["body"]),
        Paragraph("Pourtant, le Capitaine continuait à parcourir le pont.", S["body"]),
        Paragraph("Il vérifiait les amarres. Puis les réserves. Puis les voiles. Puis les lanternes. Puis revenait vers les amarres.", S["body"]),
        Paragraph("Autour de lui, tout fonctionnait pourtant comme prévu. Les marins occupaient leurs postes. Le mécanicien entretenait son matériel. Les hommes de quart surveillaient l'horizon. Le navire avançait sans difficulté.", S["body"]),
        Paragraph("Au fil de la matinée, le Capitaine ralentit peu à peu son pas.", S["body"]),
        Paragraph("Il observa simplement le travail de l'équipage. Les gestes étaient précis. Les habitudes bien installées. Le bateau semblait connaître sa route autant que ceux qui le dirigeaient.", S["body"]),
        Paragraph("Alors, pour une fois, il s'accorda quelques instants de repos près de la barre.", S["body"]),
        Paragraph("Le soleil poursuivit sa course. La mer demeura paisible. Personne ne courut. Personne n'éleva la voix. Le navire continua son voyage avec la même assurance.", S["body"]),
        Paragraph("Au coucher du soleil, le Capitaine regarda les voiles teintées d'or.", S["body"]),
        Paragraph("Il réalisa que le navire avait parfaitement poursuivi sa route sans qu'il ait eu besoin d'intervenir à chaque instant.", S["body"]),
        Paragraph("Les marins avaient accompli leur travail. Les voiles avaient porté le bâtiment. Le vent avait soufflé comme prévu.", S["body"]),
        Paragraph("Et la mer semblait savoir exactement ce qu'elle avait à faire.", S["body"]),
        sp(6),
        make_img("ch2"),
        PageBreak(),
    ]

    # ── CHAPITRE 3 ────────────────────────────────────────────────────────
    story += [
        sp(6),
        Paragraph("CHAPITRE 3", S["section_label"]),
        Paragraph("LE BRUIT DE FOND", S["chapter_title"]),
        rule(),
        sp(4),
        Paragraph("La journée avait commencé comme beaucoup d'autres. Un vent léger soufflait du large. Le ciel était dégagé. Le navire avançait régulièrement.", S["body"]),
        Paragraph("Au milieu de la matinée, une voile se coinça légèrement dans un cordage usé.", S["body"]),
        Paragraph("L'incident était mineur. Le bateau poursuivait sa route. Le vent restait favorable. Le cap ne changeait pas.", S["body"]),
        Paragraph("Pourtant, l'information circula rapidement d'un bout à l'autre du navire.", S["body"]),
        Paragraph("À mesure qu'elle se propageait, chacun y ajoutait ses suppositions. On évoqua des retards. Des complications. D'autres problèmes qui pourraient survenir.", S["body"]),
        Paragraph("Le sujet occupa bientôt davantage les conversations que la navigation elle-même.", S["body"]),
        Paragraph("Pendant ce temps, la voile restait exactement dans le même état. Ni plus ni moins.", S["body"]),
        Paragraph("Finalement, le vieux maître d'équipage examina le cordage. La partie usée fut remplacée. Quelques minutes plus tard, tout fonctionnait de nouveau parfaitement.", S["body"]),
        Paragraph("L'incident était terminé. Le navire poursuivit sa route.", S["body"]),
        Paragraph("Le soir venu, tandis que le soleil descendait lentement vers l'horizon, la traversée semblait n'avoir connu aucun événement particulier.", S["body"]),
        Paragraph("La voile était réparée. Le vent soufflait toujours. La mer demeurait calme.", S["body"]),
        Paragraph("Seul le bruit qui avait entouré le problème avait été plus important que le problème lui-même.", S["body"]),
        Paragraph("Au large, les vagues continuaient de naître puis de disparaître. Comme elles l'avaient toujours fait.", S["body"]),
        sp(6),
        make_img("ch3"),
        PageBreak(),
    ]

    # ── CHAPITRE 4 ────────────────────────────────────────────────────────
    story += [
        sp(6),
        Paragraph("CHAPITRE 4", S["section_label"]),
        Paragraph("LES INSTRUMENTS DE BORD", S["chapter_title"]),
        rule(),
        sp(4),
        Paragraph("Depuis plusieurs jours, le navire naviguait sous un ciel changeant.", S["body"]),
        Paragraph("Les vents restaient favorables, mais une légère brume apparaissait régulièrement à l'horizon. Rien d'inquiétant. Rien d'exceptionnel. Seulement cette fine couche grise qui effaçait parfois les repères les plus lointains.", S["body"]),
        Paragraph("Le Capitaine connaissait bien ces conditions. Dans ce genre de traversée, l'œil seul ne suffisait plus toujours. Il fallait faire confiance aux instruments.", S["body"]),
        Paragraph("Le compas indiquait le cap. Les cartes confirmaient la route. Les relevés correspondaient aux prévisions. Tout était cohérent.", S["body"]),
        Paragraph("Pourtant, le Capitaine revenait régulièrement consulter les mêmes informations. Il vérifiait une première fois. Puis une seconde. Puis encore une autre.", S["body"]),
        Paragraph("Chaque contrôle confirmait exactement la même chose. Le navire suivait sa route.", S["body"]),
        Paragraph("Les jours passèrent ainsi. Chaque matin, les instruments donnaient les mêmes indications. Chaque soir, le navire se trouvait exactement là où il devait être.", S["body"]),
        Paragraph("Peu à peu, le Capitaine commença à observer autre chose. Il remarqua le calme des marins. La confiance du maître d'équipage. La précision des hommes de quart.", S["body"]),
        Paragraph("Personne ne semblait inquiet. Personne ne remettait constamment en question la direction prise. Tous accomplissaient simplement leur tâche. Comme si la route était déjà connue.", S["body"]),
        Paragraph("Un matin, alors que la brume recouvrait encore la mer, le Capitaine resta quelques instants immobile devant le compas.", S["body"]),
        Paragraph("L'aiguille indiquait le nord. Comme elle l'avait fait la veille. Comme elle le ferait probablement le lendemain.", S["body"]),
        Paragraph("Ce jour-là, il referma la carte un peu plus tôt que d'habitude.", S["body"]),
        Paragraph("Non parce qu'il cessait d'être prudent. Non parce qu'il abandonnait sa vigilance. Simplement parce que tout ce qui devait être vérifié l'avait déjà été.", S["body"]),
        Paragraph("Le navire poursuivit sa route. Les voiles restèrent bien orientées. Le vent demeura constant. Les instruments continuèrent silencieusement leur travail.", S["body"]),
        Paragraph("À la tombée du jour, la brume se dissipa peu à peu. L'horizon réapparut.", S["body"]),
        Paragraph("Le Capitaine regarda longtemps la ligne claire où le ciel rejoignait la mer.", S["body"]),
        Paragraph("Il comprit alors qu'il n'était pas seul à guider le voyage. Les cartes étaient là. Les instruments aussi. L'équipage également. Tout un ensemble de repères veillait déjà sur la traversée.", S["body"]),
        Paragraph("La nuit tomba lentement sur l'océan. Le compas continuait de pointer sa direction avec la même discrétion qu'au premier jour.", S["body"]),
        Paragraph("Et le navire avançait toujours.", S["body"]),
        sp(6),
        make_img("ch4"),
        PageBreak(),
    ]

    # ── CHAPITRE 5 ────────────────────────────────────────────────────────
    story += [
        sp(6),
        Paragraph("CHAPITRE 5", S["section_label"]),
        Paragraph("LE VENT CONTRAIRE", S["chapter_title"]),
        rule(),
        sp(4),
        Paragraph("La traversée avait été préparée avec soin.", S["body"]),
        Paragraph("Les cartes avaient été vérifiées. Les réserves chargées. Les voiles inspectées. Les cordages remplacés lorsque cela était nécessaire. Rien n'avait été laissé au hasard.", S["body"]),
        Paragraph("Le matin du départ, la mer était calme. Le vent soufflait dans la bonne direction. L'horizon était dégagé. Tout semblait promettre une traversée paisible.", S["body"]),
        Paragraph("Durant les premiers jours, le navire avança exactement comme prévu. Les milles défilaient. Les quarts s'enchaînaient. Le voyage suivait la route tracée sur les cartes.", S["body"]),
        Paragraph("Puis, un matin, le vent changea.", S["body"]),
        Paragraph("Rien de spectaculaire. Aucun grain à l'horizon. Aucune tempête. Simplement un vent qui décida de souffler autrement.", S["body"]),
        Paragraph("Les voiles furent ajustées. Le navire ralentit. La progression devint moins directe. Il fallut modifier l'allure. Rechercher d'autres angles. Composer avec la mer.", S["body"]),
        Paragraph("Le Capitaine consulta les cartes. Elles étaient exactes. Il vérifia les instruments. Ils fonctionnaient parfaitement. Il observa les voiles. Elles étaient correctement réglées. Tout était en ordre.", S["body"]),
        Paragraph("Et pourtant, le vent demeurait contraire.", S["body"]),
        Paragraph("Pendant plusieurs jours, la situation resta la même. Le navire avançait toujours. Mais moins vite. Chaque mille parcouru demandait davantage de patience.", S["body"]),
        Paragraph("Certains marins regardaient régulièrement l'horizon en espérant voir le vent tourner. D'autres calculaient le retard accumulé. Le Capitaine observait simplement la mer.", S["body"]),
        Paragraph("Il connaissait cette situation. Tous les marins la connaissaient un jour.", S["body"]),
        Paragraph("Il existe des traversées où rien n'est cassé. Rien n'est perdu. Rien n'est mal préparé. Et pourtant, le voyage devient plus difficile. La mer possède parfois ses propres intentions.", S["body"]),
        Paragraph("Au fil des jours, le Capitaine comprit une chose que les cartes ne mentionnaient jamais.", S["body"]),
        Paragraph("Préparer parfaitement un voyage ne donne pas le pouvoir de choisir le vent.", S["body"]),
        Paragraph("Aucun marin ne commande les courants. Aucun capitaine ne décide de la météo. Tout ce qu'il peut faire est préparer son navire du mieux possible lorsque la mer est calme. Puis poursuivre sa route lorsque les conditions changent.", S["body"]),
        Paragraph("Un soir, alors que le soleil disparaissait derrière les vagues, le vent commença enfin à tourner. D'abord légèrement. Puis davantage. Les voiles retrouvèrent progressivement leur pleine puissance. Le navire reprit de la vitesse. L'étrave fendit de nouveau l'eau avec assurance. L'équipage retrouva le sourire.", S["body"]),
        Paragraph("Le voyage reprit son rythme.", S["body"]),
        Paragraph("Ce n'était pas le retour du vent favorable qu'il retenait. C'était autre chose.", S["body"]),
        Paragraph("Durant tout ce temps, malgré les détours, malgré les ralentissements et malgré les journées plus longues que prévu, le navire n'avait jamais cessé d'avancer.", S["body"]),
        Paragraph("La route avait changé. Le rythme avait changé. Mais le voyage avait continué.", S["body"]),
        Paragraph("Le vent n'avait pas toujours soufflé dans la direction espérée. La route n'avait pas toujours été celle qui figurait sur les cartes.", S["body"]),
        Paragraph("Et pourtant, le navire avançait toujours.", S["body"]),
        Paragraph("Devant lui, l'horizon s'ouvrait de nouveau. Comme il l'avait toujours fait.", S["body"]),
        sp(6),
        make_img("ch4bis"),
        PageBreak(),
    ]

    # ── CHAPITRE 6 ────────────────────────────────────────────────────────
    story += [
        sp(6),
        Paragraph("CHAPITRE 6", S["section_label"]),
        Paragraph("LE LONG COURS", S["chapter_title"]),
        rule(),
        sp(4),
        Paragraph("Le voyage durait depuis de nombreuses semaines.", S["body"]),
        Paragraph("Les ports visités commençaient à se mélanger dans les souvenirs. Certaines escales semblaient proches. D'autres appartenaient déjà à une autre saison.", S["body"]),
        Paragraph("Le Capitaine avait connu des mers calmes. Des vents contraires. Des journées lumineuses. Quelques nuits plus difficiles. Comme tous les marins qui naviguent longtemps.", S["body"]),
        Paragraph("Avec les années, il avait compris une chose que les jeunes capitaines découvrent rarement dès leurs premières traversées.", S["body"]),
        Paragraph("Un océan ne se franchit pas en une journée.", S["body"]),
        Paragraph("Il ne se franchit pas non plus en restant continuellement debout à surveiller chaque vague.", S["body"]),
        Paragraph("La mer est patiente. Le voyage aussi.", S["body"]),
        Paragraph("Certains matins, le vent pousse naturellement le navire. D'autres jours, il faut accepter d'avancer plus lentement. Parfois, il suffit simplement de tenir le cap.", S["body"]),
        Paragraph("Au fil du temps, le Capitaine apprit à respecter ce rythme. Il continua à observer. À préparer. À anticiper. Mais il apprit aussi à s'économiser. À laisser l'équipage prendre le quart. À partager certaines responsabilités. À accepter que chaque instant ne dépende pas uniquement de lui.", S["body"]),
        Paragraph("Un soir d'été, alors que la mer était particulièrement calme, il resta longtemps à regarder le soleil disparaître derrière l'horizon.", S["body"]),
        Paragraph("Les voiles se découpaient en ombres noires sur le ciel rougeoyant. Le navire avançait paisiblement. Les hommes occupaient leurs postes. Tout semblait à sa place.", S["body"]),
        Paragraph("Pour la première fois depuis longtemps, le Capitaine quitta le pont avant la tombée complète de la nuit.", S["body"]),
        Paragraph("Il descendit lentement vers sa cabine.", S["body"]),
        Paragraph("Derrière lui, rien ne s'arrêta. Le vent continua de souffler. Les vagues continuèrent de porter le navire. Les marins poursuivirent leur veille. La traversée continua.", S["body"]),
        Paragraph("Quelques heures plus tard, lorsqu'il remonta sur le pont, les premières lueurs de l'aube apparaissaient déjà à l'est.", S["body"]),
        Paragraph("Le navire avait parcouru plusieurs milles. La route était bonne. Le cap était maintenu. L'océan s'étendait toujours devant eux.", S["body"]),
        Paragraph("Le Capitaine observa l'horizon puis esquissa un léger sourire.", S["body"]),
        Paragraph("La mer n'avait pas eu besoin de lui pendant chaque minute de la nuit.", S["body"]),
        Paragraph("Et pourtant, le voyage avançait toujours.", S["body"]),
        Paragraph("Devant l'étrave, les premiers rayons du soleil vinrent éclairer la surface de l'eau.", S["body"]),
        Paragraph("Le navire poursuivait sa route vers le large. Comme il l'avait toujours fait. Comme il continuerait encore longtemps à le faire.", S["body"]),
        sp(6),
        make_img("ch5"),
        PageBreak(),
    ]

    # ── ÉPILOGUE ──────────────────────────────────────────────────────────
    story += [
        sp(6),
        Paragraph("ÉPILOGUE", S["section_label"]),
        Paragraph("LE PORT", S["chapter_title"]),
        rule(),
        sp(4),
        Paragraph("Le soleil descendait lentement derrière les quais.", S["body"]),
        Paragraph("Le navire était amarré depuis plusieurs heures. Les voiles avaient été pliées. Les cordages reposaient sans tension. L'équipage avait quitté le pont depuis longtemps.", S["body"]),
        Paragraph("Quelques mouettes tournaient encore au-dessus du port.", S["body"]),
        Paragraph("Le Capitaine resta seul quelques instants à observer la mer. Au loin, l'horizon se confondait avec le ciel du soir.", S["body"]),
        Paragraph("Il repensa aux traversées passées. Aux vents favorables. Aux tempêtes. Aux longues nuits de veille. Aux routes parcourues.", S["body"]),
        Paragraph("Le navire avait changé. L'équipage aussi. Et lui également.", S["body"]),
        Paragraph("Il y avait eu un temps où il croyait devoir surveiller chaque corde, chaque voile et chaque mouvement de la mer.", S["body"]),
        Paragraph("Aujourd'hui, le bateau reposait paisiblement contre le quai. Solide. Fiable. Prêt pour d'autres voyages.", S["body"]),
        Paragraph("Le Capitaine regarda une dernière fois l'horizon.", S["body"]),
        Paragraph("Puis il quitta le pont.", S["body"]),
        Paragraph("Derrière lui, le navire demeura immobile.", S["body"]),
        Paragraph("Comme s'il lui rappelait doucement qu'il savait désormais tenir la mer lui aussi.", S["body"]),
        sp(8),
        Paragraph("« Le sillage était toujours là. »", S["closing_quote"]),
        sp(6),
        make_img("epilogue"),
        PageBreak(),
    ]

    # ── QUATRIÈME DE COUVERTURE ───────────────────────────────────────────
    story += [
        sp(10),
        rule(),
        sp(6),
        Paragraph("LE CALME SUR LE PONT", S["back_title"]),
        sp(4),
        Paragraph("Au large, les tempêtes ne sont pas toujours celles que l'on croit.", S["back_body"]),
        Paragraph("À travers les chroniques d'un Capitaine et de son équipage, ce livre raconte des histoires simples de navigation : une voile qui se bloque, une mer soudainement calme, un instrument que l'on consulte trop souvent, un vent qui change de direction ou un horizon que l'on peine à distinguer.", S["back_body"]),
        Paragraph("Au fil des traversées, le Capitaine observe, anticipe, protège et veille sur son navire.", S["back_body"]),
        Paragraph("Mais la mer lui enseigne parfois que les plus longues routes ne se parcourent pas seul, que certains vents ne se commandent pas et que même les bâtiments les mieux préparés doivent apprendre à composer avec l'océan.", S["back_body"]),
        Paragraph("Entre récits maritimes, souvenirs du large et horizons lointains, <i>Le Calme sur le Pont</i> est une invitation à embarquer pour un voyage où chacun reconnaîtra peut-être une part de sa propre traversée.", S["back_body"]),
        sp(8),
        rule(),
        sp(4),
        Paragraph("Younès Belgnaoui", S["back_author"]),
    ]

    return story


# ── Page numbering ─────────────────────────────────────────────────────────
def on_page(canvas, doc):
    if doc.page > 4:  # skip title pages
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#999999"))
        canvas.drawCentredString(W/2, 10*mm, str(doc.page - 4))
        canvas.restoreState()


# ── Main ───────────────────────────────────────────────────────────────────
out = "/mnt/user-data/outputs/Le_Calme_sur_le_Pont_IMPRESSION.pdf"

doc = SimpleDocTemplate(
    out,
    pagesize=A5,
    leftMargin=ML, rightMargin=MR,
    topMargin=MT, bottomMargin=MB,
    title="Le Calme sur le Pont",
    author="Younès Belgnaoui",
)

doc.build(build(), onFirstPage=on_page, onLaterPages=on_page)
print(f"✓ PDF généré : {out}")
EOF