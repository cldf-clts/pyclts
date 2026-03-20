from pyclts.ipachart import *


def test_ipa_charts():
    inventory = [
        Segment('x', 'voiced alveolar nasal consonant', href='http://example.org', css_class='abc'),
        Segment('a', 'rounded close back vowel', href='http://example.org', css_class='abc')
    ]
    html, covered = ipa_charts(inventory)
    assert covered == {0, 1}
    assert html == HTML_NO_COLORSPEC
    html, covered = ipa_charts(inventory, colorspec={'abc': ('red', 'solid 1px green')})
    assert html == HTML_WITH_COLORSPEC


HTML_WITH_COLORSPEC = """\
<html>
<head>
<style>
body {font-family: sans-serif}
table caption {text-align: left;}
figure {display: table; margin-left: 0px;}
figcaption {display: table-caption; caption-side: top; font-size: 120%;}
#pulmonic-consonants a {text-decoration: none; font-size: smaller;}
#pulmonic-consonants a {color: black;}
#pulmonic-consonants a {outline: solid 1px solid 1px white;}
#pulmonic-consonants a.abc text, text svg|a.abc {fill: red;}
#pulmonic-consonants a.abc {outline: solid 1px green;}
#vowel-trapezoid {height: 300px; width: 100%; min-width: 800px;}
#vowel-trapezoid .label {font-size: 150%;}
#vowel-trapezoid .glyph {font-size: 170%;}
</style>
</head>
<body>
<div><table id="pulmonic-consonants" style="font-size:125%; margin-right:1.0em; margin-bottom:0.5em; text-align:center; vertical-align:bottom; border-collapse:collapse; background:transparent;" border="1" cellpadding="1" cellspacing="0" align="left">
    <caption>Pulmonic Consonants</caption>
    <thead>
    <tr style="vertical-align:top; line-height:2.0em; font-size:75%;">
        <td style="border:2px solid; border-width:0px 2px 0px 1px; text-align:right">
            <a title="Place of articulation">Place</a>&#160;&#8594;
        </td>
        <td colspan="5" style="border:1px solid; border-width:0px 1px 1px 0">Labial</td>
        <td colspan="10" style="border:1px solid; border-width:0px 1px 1px 0">Coronal</td>
        <td colspan="6" style="border:1px solid; border-width:0px 1px 1px 0">Dorsal</td>
        <td colspan="5" style="border:1px solid; border-width:0px 1px 1px 0">Laryngeal</td>
    </tr>
    <tr style="vertical-align:top; font-size:75%; border:2px solid; border-width:0px 0px 2px">
        <td style="width:*; border:2px solid; border-width:0px 2px 2px 1px; vertical-align:bottom; text-align:left;">
            &#8595;&#160;<a title="Manner of articulation">Manner</a>
        </td>
        <td colspan="2" style="border:1px solid; border-width:0px 1px 0">Bilabial</td>
        <td colspan="2" style="border:1px solid; border-width:0px 1px 0">Labio&#173;dental</td>
        <td colspan="2" style="border:1px solid; border-width:0px 1px 0">Linguo&#173;labial</td>
        <td colspan="2" style="border:1px solid; border-width:0px 1px 0">Dental</td>
        <td colspan="2" style="border:1px solid; border-width:0px 1px 0">Alveolar</td>
        <td colspan="2" style="border:1px solid; border-width:0px 1px 0">Palato-<br />alveolar</td>
        <td colspan="2" style="border:1px solid; border-width:0px 1px 0">Retroflex</td>
        <td colspan="2" style="border:1px solid; border-width:0px 1px 0">Alveolo-<br />palatal</td>
        <td colspan="2" style="border:1px solid; border-width:0px 1px 0">Palatal</td>
        <td colspan="2" style="border:1px solid; border-width:0px 1px 0">Velar</td>
        <td colspan="2" style="border:1px solid; border-width:0px 1px 0">Uvular</td>
        <td colspan="2" style="border:1px solid; border-width:0px 1px 0">Pharyngeal<br />/&#160;Epiglottal</td>
        <td colspan="2" style="border:1px solid; border-width:0px 1px 1px 0">Glottal</td>
    </tr>
    </thead>
    <tbody>
    <tr>
        <td style="text-align:left; font-size:75%; border:2px solid; border-width:0px 2px 0px 1px">Nasal</td>
        <td class="voiceless-bilabial-nasal" />
        <td class="voiced-bilabial-nasal" />
        <td class="voiceless-labiodental-nasal" />
        <td class="voiced-labiodental-nasal" />
        <td class="voiceless-linguolabial-nasal" />
        <td class="voiced-linguolabial-nasal" />
        <td class="voiceless-dental-nasal" />
        <td class="voiced-dental-nasal" />
        <td class="voiceless-alveolar-nasal" />
        <td class="voiced-alveolar-nasal"><a href="http://example.org" class="abc" title="voiced alveolar nasal consonant">x</a></td>
        <td class="voiceless-postalveolar-nasal" />
        <td class="voiced-postalveolar-nasal" />
        <td class="voiceless-retroflex-nasal" />
        <td class="voiced-retroflex-nasal" />
        <td class="voiceless-alveolopalatal-nasal" />
        <td class="voiced-alveolopalatal-nasal" />
        <td class="voiceless-palatal-nasal" />
        <td class="voiced-palatal-nasal" />
        <td class="voiceless-velar-nasal" />
        <td class="voiced-velar-nasal" />
        <td class="voiceless-uvular-nasal" />
        <td class="voiced-uvular-nasal" />
        <td class="voiceless-epiglottal-nasal" style="border:1px solid; background:#ccc;" />
        <td class="voiced-epiglottal-nasal" style="border:1px solid; background:#ccc;" />
        <td class="voiceless-glottal-nasal" style="border:1px solid; background:#ccc;" />
        <td class="voiced-glottal-nasal" style="border:1px solid; background:#ccc;" />
    </tr>
    <tr>
        <td style="font-size:75%; text-align:left; border:2px solid; border-width:0px 2px 0px 1px">Stop</td>
        <td class="voiceless-bilabial-stop" />
        <td class="voiced-bilabial-stop" />
        <td class="voiceless-labiodental-stop" />
        <td class="voiced-labiodental-stop" />
        <td class="voiceless-linguolabial-stop" />
        <td class="voiced-linguolabial-stop" />
        <td class="voiceless-dental-stop" />
        <td class="voiced-dental-stop" />
        <td class="voiceless-alveolar-stop" />
        <td class="voiced-alveolar-stop" />
        <td class="voiceless-postalveolar-stop" />
        <td class="voiced-postalveolar-stop" />
        <td class="voiceless-retroflex-stop" />
        <td class="voiced-retroflex-stop" />
        <td class="voiceless-alveolopalatal-stop" />
        <td class="voiced-alveolopalatal-stop" />
        <td class="voiceless-palatal-stop" />
        <td class="voiced-palatal-stop" />
        <td class="voiceless-velar-stop" />
        <td class="voiced-velar-stop" />
        <td class="voiceless-uvular-stop" />
        <td class="voiced-uvular-stop" />
        <td class="voiceless-epiglottal-stop" />
        <td class="voiced-epiglottal-stop" />
        <td class="voiceless-glottal-stop" />
        <td class="voiced-glottal-stop" style="border:1px solid; border-left:none; background:#ccc" />
    </tr>
    <tr>
        <td style="font-size:75%; text-align:left; border:2px solid; border-width:0px 2px 0px 1px">Sibilant affricate</td>
        <td class="voiceless-bilabial-sibilant-affricate" style="border:1px solid; background:#ccc;" />
        <td class="voiced-bilabial-sibilant-affricate" style="border:1px solid; background:#ccc;" />
        <td class="voiceless-labiodental-sibilant-affricate" style="border:1px solid; background:#ccc;" />
        <td class="voiced-labiodental-sibilant-affricate" style="border:1px solid; background:#ccc;" />
        <td class="voiceless-linguolabial-sibilant-affricate" style="border:1px solid; background:#ccc;" />
        <td class="voiced-linguolabial-sibilant-affricate" style="border:1px solid; background:#ccc;" />
        <td class="voiceless-dental-sibilant-affricate" />
        <td class="voiced-dental-sibilant-affricate" />
        <td class="voiceless-alveolar-sibilant-affricate" />
        <td class="voiced-alveolar-sibilant-affricate" />
        <td class="voiceless-postalveolar-sibilant-affricate" />
        <td class="voiced-postalveolar-sibilant-affricate" />
        <td class="voiceless-retroflex-sibilant-affricate" />
        <td class="voiced-retroflex-sibilant-affricate" />
        <td class="voiceless-alveolopalatal-sibilant-affricate" />
        <td class="voiced-alveolopalatal-sibilant-affricate" />
        <td class="voiceless-palatal-sibilant-affricate" style="border:1px solid; background:#ccc;" />
        <td class="voiced-palatal-sibilant-affricate" style="border:1px solid; background:#ccc;" />
        <td class="voiceless-velar-sibilant-affricate" style="border:1px solid; background:#ccc;" />
        <td class="voiced-velar-sibilant-affricate" style="border:1px solid; background:#ccc;" />
        <td class="voiceless-uvular-sibilant-affricate" style="border:1px solid; background:#ccc;" />
        <td class="voiced-uvular-sibilant-affricate" style="border:1px solid; background:#ccc;" />
        <td class="voiceless-epiglottal-sibilant-affricate" style="border:1px solid; background:#ccc;" />
        <td class="voiced-epiglottal-sibilant-affricate" style="border:1px solid; background:#ccc;" />
        <td class="voiceless-glottal-sibilant-affricate" style="border:1px solid; background:#ccc;" />
        <td class="voiced-glottal-sibilant-affricate" style="border:1px solid; border-left:none; background:#ccc" />
    </tr>
    <tr>
        <td style="font-size:75%; text-align:left; border:2px solid; border-width:0px 2px 0px 1px">Non-sibilant affricate</td>
        <td class="voiceless-bilabial-NONsibilant-NONlateral-affricate" />
        <td class="voiced-bilabial-NONsibilant-NONlateral-affricate" />
        <td class="voiceless-labiodental-NONsibilant-NONlateral-affricate" />
        <td class="voiced-labiodental-NONsibilant-NONlateral-affricate" />
        <td class="voiceless-linguolabial-NONsibilant-NONlateral-affricate" />
        <td class="voiced-linguolabial-NONsibilant-NONlateral-affricate" />
        <td class="voiceless-dental-NONsibilant-NONlateral-affricate" />
        <td class="voiced-dental-NONsibilant-NONlateral-affricate" />
        <td class="voiceless-alveolar-NONsibilant-NONlateral-affricate" />
        <td class="voiced-alveolar-NONsibilant-NONlateral-affricate" />
        <td class="voiceless-postalveolar-NONsibilant-NONlateral-affricate" />
        <td class="voiced-postalveolar-NONsibilant-NONlateral-affricate" />
        <td class="voiceless-retroflex-NONsibilant-NONlateral-affricate" />
        <td class="voiced-retroflex-NONsibilant-NONlateral-affricate" />
        <td class="voiceless-alveolopalatal-NONsibilant-NONlateral-affricate" />
        <td class="voiced-alveolopalatal-NONsibilant-NONlateral-affricate" />
        <td class="voiceless-palatal-NONsibilant-NONlateral-affricate" />
        <td class="voiced-palatal-NONsibilant-NONlateral-affricate" />
        <td class="voiceless-velar-NONsibilant-NONlateral-affricate" />
        <td class="voiced-velar-NONsibilant-NONlateral-affricate" />
        <td class="voiceless-uvular-NONsibilant-NONlateral-affricate" />
        <td class="voiced-uvular-NONsibilant-NONlateral-affricate" />
        <td class="voiceless-epiglottal-NONsibilant-NONlateral-affricate" />
        <td class="voiced-epiglottal-NONsibilant-NONlateral-affricate" />
        <td class="voiceless-glottal-NONsibilant-NONlateral-affricate" />
        <td class="voiced-glottal-NONsibilant-NONlateral-affricate" style="border:1px solid; border-left:none; background:#ccc" />
    </tr>
    <tr>
        <td style="font-size:75%; text-align:left; border:2px solid; border-width:0px 2px 0px 1px">Sibilant fricative</td>
        <td class="voiceless-bilabial-sibilant-fricative" style="border:1px solid; background:#ccc;" />
        <td class="voiced-bilabial-sibilant-fricative" style="border:1px solid; background:#ccc;" />
        <td class="voiceless-labiodental-sibilant-fricative" style="border:1px solid; background:#ccc;" />
        <td class="voiced-labiodental-sibilant-fricative" style="border:1px solid; background:#ccc;" />
        <td class="voiceless-linguolabial-sibilant-fricative" style="border:1px solid; background:#ccc;" />
        <td class="voiced-linguolabial-sibilant-fricative" style="border:1px solid; background:#ccc;" />
        <td class="voiceless-dental-sibilant-fricative" />
        <td class="voiced-dental-sibilant-fricative" />
        <td class="voiceless-alveolar-sibilant-fricative" />
        <td class="voiced-alveolar-sibilant-fricative" />
        <td class="voiceless-postalveolar-sibilant-fricative" />
        <td class="voiced-postalveolar-sibilant-fricative" />
        <td class="voiceless-retroflex-sibilant-fricative" />
        <td class="voiced-retroflex-sibilant-fricative" />
        <td class="voiceless-alveolopalatal-sibilant-fricative" />
        <td class="voiced-alveolopalatal-sibilant-fricative" />
        <td class="voiceless-palatal-sibilant-fricative" style="border:1px solid; background:#ccc;" />
        <td class="voiced-palatal-sibilant-fricative" style="border:1px solid; background:#ccc;" />
        <td class="voiceless-velar-sibilant-fricative" style="border:1px solid; background:#ccc;" />
        <td class="voiced-velar-sibilant-fricative" style="border:1px solid; background:#ccc;" />
        <td class="voiceless-uvular-sibilant-fricative" style="border:1px solid; background:#ccc;" />
        <td class="voiced-uvular-sibilant-fricative" style="border:1px solid; background:#ccc;" />
        <td class="voiceless-epiglottal-sibilant-fricative" style="border:1px solid; background:#ccc;" />
        <td class="voiced-epiglottal-sibilant-fricative" style="border:1px solid; background:#ccc;" />
        <td class="voiceless-glottal-sibilant-fricative" style="border:1px solid; background:#ccc;" />
        <td class="voiced-glottal-sibilant-fricative" style="border:1px solid; border-left:none; background:#ccc" />
    </tr>
    <tr>
        <td style="font-size:75%; text-align:left; border:2px solid; border-width:0px 2px 0px 1px">Non-sibilant fricative</td>
        <td class="voiceless-bilabial-NONsibilant-NONlateral-fricative" />
        <td class="voiced-bilabial-NONsibilant-NONlateral-fricative" />
        <td class="voiceless-labiodental-NONsibilant-NONlateral-fricative" />
        <td class="voiced-labiodental-NONsibilant-NONlateral-fricative" />
        <td class="voiceless-linguolabial-NONsibilant-NONlateral-fricative" />
        <td class="voiced-linguolabial-NONsibilant-NONlateral-fricative" />
        <td class="voiceless-dental-NONsibilant-NONlateral-fricative" />
        <td class="voiced-dental-NONsibilant-NONlateral-fricative" />
        <td class="voiceless-alveolar-NONsibilant-NONlateral-fricative" />
        <td class="voiced-alveolar-NONsibilant-NONlateral-fricative" />
        <td class="voiceless-postalveolar-NONsibilant-NONlateral-fricative" />
        <td class="voiced-postalveolar-NONsibilant-NONlateral-fricative" />
        <td class="voiceless-retroflex-NONsibilant-NONlateral-fricative" />
        <td class="voiced-retroflex-NONsibilant-NONlateral-fricative" />
        <td class="voiceless-alveolopalatal-NONsibilant-NONlateral-fricative" />
        <td class="voiced-alveolopalatal-NONsibilant-NONlateral-fricative" />
        <td class="voiceless-palatal-NONsibilant-NONlateral-fricative" />
        <td class="voiced-palatal-NONsibilant-NONlateral-fricative" />
        <td class="voiceless-velar-NONsibilant-NONlateral-fricative" />
        <td class="voiced-velar-NONsibilant-NONlateral-fricative" />
        <td class="voiceless-uvular-NONsibilant-NONlateral-fricative" />
        <td class="voiced-uvular-NONsibilant-NONlateral-fricative" />
        <td class="voiceless-epiglottal-NONsibilant-NONlateral-fricative voiceless-pharyngeal-NONsibilant-NONlateral-fricative" />
        <td class="voiced-epiglottal-NONsibilant-NONlateral-fricative voiced-pharyngeal-NONsibilant-NONlateral-fricative" />
        <td class="voiceless-glottal-NONsibilant-NONlateral-fricative" />
        <td class="voiced-glottal-NONsibilant-NONlateral-fricative" />
    </tr>
    <tr>
        <td style="font-size:75%; text-align:left; border:2px solid; border-width:0px 2px 0px 1px"><a title="Approximant consonant">Approximant</a></td>
        <td class="voiceless-bilabial-approximant" />
        <td class="voiced-bilabial-approximant" />
        <td class="voiceless-labiodental-approximant" />
        <td class="voiced-labiodental-approximant" />
        <td class="voiceless-linguolabial-approximant" />
        <td class="voiced-linguolabial-approximant" />
        <td class="voiceless-dental-approximant" />
        <td class="voiced-dental-approximant" />
        <td class="voiceless-alveolar-approximant" />
        <td class="voiced-alveolar-approximant" />
        <td class="voiceless-postalveolar-approximant" />
        <td class="voiced-postalveolar-approximant" />
        <td class="voiceless-retroflex-approximant" />
        <td class="voiced-retroflex-approximant" />
        <td class="voiceless-alveolopalatal-approximant" />
        <td class="voiced-alveolopalatal-approximant" />
        <td class="voiceless-palatal-approximant" />
        <td class="voiced-palatal-approximant" />
        <td class="voiceless-velar-approximant" />
        <td class="voiced-velar-approximant" />
        <td class="voiceless-uvular-approximant" />
        <td class="voiced-uvular-approximant" />
        <td class="voiceless-epiglottal-approximant" />
        <td class="voiced-epiglottal-approximant" />
        <td class="voiceless-glottal-approximant" />
        <td class="voiced-glottal-approximant" />
    </tr>
    <tr>
        <td style="font-size:75%; text-align:left; border:2px solid; border-width:0px 2px 0px 1px"><a title="Flap consonant">Flap or tap</a></td>
        <td class="voiceless-bilabial-tap" />
        <td class="voiced-bilabial-tap" />
        <td class="voiceless-labiodental-tap" />
        <td class="voiced-labiodental-tap" />
        <td class="voiceless-linguolabial-tap" />
        <td class="voiced-linguolabial-tap" />
        <td class="voiceless-dental-tap" />
        <td class="voiced-dental-tap" />
        <td class="voiceless-alveolar-tap" />
        <td class="voiced-alveolar-tap" />
        <td class="voiceless-postalveolar-tap" />
        <td class="voiced-postalveolar-tap" />
        <td class="voiceless-retroflex-tap" />
        <td class="voiced-retroflex-tap" />
        <td class="voiceless-alveolopalatal-tap" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiced-alveolopalatal-tap" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiceless-palatal-tap" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiced-palatal-tap" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiceless-velar-tap" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiced-velar-tap" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiceless-uvular-tap" />
        <td class="voiced-uvular-tap" />
        <td class="voiceless-epiglottal-tap" />
        <td class="voiced-epiglottal-tap" />
        <td class="voiceless-glottal-tap" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiced-glottal-tap" style="border:1px solid; border-left:none; background:#ccc" />
    </tr>
    <tr>
        <td style="font-size:75%; text-align:left; border:2px solid; border-width:0px 2px 0px 1px"><a title="Trill consonant">Trill</a></td>
        <td class="voiceless-bilabial-trill" />
        <td class="voiced-bilabial-trill" />
        <td class="voiceless-labiodental-trill" />
        <td class="voiced-labiodental-trill" />
        <td class="voiceless-linguolabial-trill" />
        <td class="voiced-linguolabial-trill" />
        <td class="voiceless-dental-trill" />
        <td class="voiced-dental-trill" />
        <td class="voiceless-alveolar-trill" />
        <td class="voiced-alveolar-trill" />
        <td class="voiceless-postalveolar-trill" />
        <td class="voiced-postalveolar-trill" />
        <td class="voiceless-retroflex-trill" />
        <td class="voiced-retroflex-trill" />
        <td class="voiceless-alveolopalatal-trill" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiced-alveolopalatal-trill" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiceless-palatal-trill" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiced-palatal-trill" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiceless-velar-trill" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiced-velar-trill" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiceless-uvular-trill" />
        <td class="voiced-uvular-trill" />
        <td class="voiceless-epiglottal-trill" />
        <td class="voiced-epiglottal-trill" />
        <td class="voiceless-glottal-trill" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiced-glottal-trill" style="border:1px solid; border-left:none; background:#ccc" />
    </tr>
    <tr>
        <td style="font-size:75%; text-align:left; border:2px solid; border-width:0px 2px 0px 1px"><a title="Lateral consonant">Lateral</a>&#160;<a title="Affricate consonant">affricate</a></td>
        <td class="voiceless-bilabial-lateral-affricate" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiced-bilabial-lateral-affricate" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiceless-labiodental-lateral-affricate" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiced-labiodental-lateral-affricate" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiceless-linguolabial-lateral-affricate" />
        <td class="voiced-linguolabial-lateral-affricate" />
        <td class="voiceless-dental-lateral-affricate" />
        <td class="voiced-dental-lateral-affricate" />
        <td class="voiceless-alveolar-lateral-affricate" />
        <td class="voiced-alveolar-lateral-affricate" />
        <td class="voiceless-postalveolar-lateral-affricate" />
        <td class="voiced-postalveolar-lateral-affricate" />
        <td class="voiceless-retroflex-lateral-affricate" />
        <td class="voiced-retroflex-lateral-affricate" />
        <td class="voiceless-alveolopalatal-lateral-affricate" />
        <td class="voiced-alveolopalatal-lateral-affricate" />
        <td class="voiceless-palatal-lateral-affricate" />
        <td class="voiced-palatal-lateral-affricate" />
        <td class="voiceless-velar-lateral-affricate" />
        <td class="voiced-velar-lateral-affricate" />
        <td class="voiceless-uvular-lateral-affricate" />
        <td class="voiced-uvular-lateral-affricate" />
        <td class="voiceless-epiglottal-lateral-affricate" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiced-epiglottal-lateral-affricate" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiceless-glottal-lateral-affricate" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiced-glottal-lateral-affricate" style="border:1px solid; border-left:none; background:#ccc" />
    </tr>
    <tr>
        <td style="font-size:75%; text-align:left; border:2px solid; border-width:0px 2px 0px 1px"><a title="Lateral consonant">Lateral</a>&#160;<a title="Fricative consonant">fricative</a></td>
        <td class="voiceless-bilabial-lateral-fricative" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiced-bilabial-lateral-fricative" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiceless-labiodental-lateral-fricative" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiced-labiodental-lateral-fricative" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiceless-linguolabial-lateral-fricative" />
        <td class="voiced-linguolabial-lateral-fricative" />
        <td class="voiceless-dental-lateral-fricative" />
        <td class="voiced-dental-lateral-fricative" />
        <td class="voiceless-alveolar-lateral-fricative" />
        <td class="voiced-alveolar-lateral-fricative" />
        <td class="voiceless-postalveolar-lateral-fricative" />
        <td class="voiced-postalveolar-lateral-fricative" />
        <td class="voiceless-retroflex-lateral-fricative" />
        <td class="voiced-retroflex-lateral-fricative" />
        <td class="voiceless-alveolopalatal-lateral-fricative" />
        <td class="voiced-alveolopalatal-lateral-fricative" />
        <td class="voiceless-palatal-lateral-fricative" />
        <td class="voiced-palatal-lateral-fricative" />
        <td class="voiceless-velar-lateral-fricative" />
        <td class="voiced-velar-lateral-fricative" />
        <td class="voiceless-uvular-lateral-fricative" />
        <td class="voiced-uvular-lateral-fricative" />
        <td class="voiceless-epiglottal-lateral-fricative" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiced-epiglottal-lateral-fricative" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiceless-glottal-lateral-fricative" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiced-glottal-lateral-fricative" style="border:1px solid; border-left:none; background:#ccc" />
    </tr>
    <tr>
        <td style="font-size:75%; text-align:left; border:2px solid; border-width:0px 2px 0px 1px"><a title="Lateral consonant">Lateral</a>&#160;<a title="Approximant consonant">approximant</a></td>
        <td class="voiceless-bilabial-lateral-approximant" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiced-bilabial-lateral-approximant" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiceless-labiodental-lateral-approximant" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiced-labiodental-lateral-approximant" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiceless-linguolabial-lateral-approximant" />
        <td class="voiced-linguolabial-lateral-approximant" />
        <td class="voiceless-dental-lateral-approximant" />
        <td class="voiced-dental-lateral-approximant" />
        <td class="voiceless-alveolar-lateral-approximant" />
        <td class="voiced-alveolar-lateral-approximant" />
        <td class="voiceless-postalveolar-lateral-approximant" />
        <td class="voiced-postalveolar-lateral-approximant" />
        <td class="voiceless-retroflex-lateral-approximant" />
        <td class="voiced-retroflex-lateral-approximant" />
        <td class="voiceless-alveolopalatal-lateral-approximant" />
        <td class="voiced-alveolopalatal-lateral-approximant" />
        <td class="voiceless-palatal-lateral-approximant" />
        <td class="voiced-palatal-lateral-approximant" />
        <td class="voiceless-velar-lateral-approximant" />
        <td class="voiced-velar-lateral-approximant" />
        <td class="voiceless-uvular-lateral-approximant" />
        <td class="voiced-uvular-lateral-approximant" />
        <td class="voiceless-epiglottal-lateral-approximant" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiced-epiglottal-lateral-approximant" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiceless-glottal-lateral-approximant" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiced-glottal-lateral-approximant" style="border:1px solid; border-left:none; background:#ccc" />
    </tr>
    <tr>
        <td style="font-size:75%; text-align:left; border:2px solid; border-width:0px 2px 1px 1px"><a title="Lateral flap">Lateral flap</a></td>
        <td class="voiceless-bilabial-lateral-tap" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiced-bilabial-lateral-tap" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiceless-labiodental-lateral-tap" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiced-labiodental-lateral-tap" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiceless-linguolabial-lateral-tap" />
        <td class="voiced-linguolabial-lateral-tap" />
        <td class="voiceless-dental-lateral-tap" />
        <td class="voiced-dental-lateral-tap" />
        <td class="voiceless-alveolar-lateral-tap" />
        <td class="voiced-alveolar-lateral-tap" />
        <td class="voiceless-postalveolar-lateral-tap" />
        <td class="voiced-postalveolar-lateral-tap" />
        <td class="voiceless-retroflex-lateral-tap" />
        <td class="voiced-retroflex-lateral-tap" />
        <td class="voiceless-alveolopalatal-lateral-tap" />
        <td class="voiced-alveolopalatal-lateral-tap" />
        <td class="voiceless-palatal-lateral-tap" />
        <td class="voiced-palatal-lateral-tap" />
        <td class="voiceless-velar-lateral-tap" />
        <td class="voiced-velar-lateral-tap" />
        <td class="voiceless-uvular-lateral-tap" />
        <td class="voiced-uvular-lateral-tap" />
        <td class="voiceless-epiglottal-lateral-tap" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiced-epiglottal-lateral-tap" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiceless-glottal-lateral-tap" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiced-glottal-lateral-tap" style="border:1px solid; border-left:none; background:#ccc" />
    </tr>
    <tr>
        <td style="font-size:75%; text-align:left; border:2px solid; border-width:0px 2px 1px 1px">Implosive</td>
        <td class="voiceless-bilabial-lateral-implosive" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiced-bilabial-lateral-implosive" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiceless-labiodental-lateral-implosive" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiced-labiodental-lateral-implosive" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiceless-linguolabial-lateral-implosive" />
        <td class="voiced-linguolabial-lateral-implosive" />
        <td class="voiceless-dental-lateral-implosive" />
        <td class="voiced-dental-lateral-implosive" />
        <td class="voiceless-alveolar-lateral-implosive" />
        <td class="voiced-alveolar-lateral-implosive" />
        <td class="voiceless-postalveolar-lateral-implosive" />
        <td class="voiced-postalveolar-lateral-implosive" />
        <td class="voiceless-retroflex-lateral-implosive" />
        <td class="voiced-retroflex-lateral-implosive" />
        <td class="voiceless-alveolopalatal-lateral-implosive" />
        <td class="voiced-alveolopalatal-lateral-implosive" />
        <td class="voiceless-palatal-lateral-implosive" />
        <td class="voiced-palatal-lateral-implosive" />
        <td class="voiceless-velar-lateral-implosive" />
        <td class="voiced-velar-lateral-implosive" />
        <td class="voiceless-uvular-lateral-implosive" />
        <td class="voiced-uvular-lateral-implosive" />
        <td class="voiceless-epiglottal-lateral-implosive" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiced-epiglottal-lateral-implosive" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiceless-glottal-lateral-implosive" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiced-glottal-lateral-implosive" style="border:1px solid; border-left:none; background:#ccc" />
    </tr>
    </tbody>
</table></div>
<div><figure><svg xmlns="http://www.w3.org/2000/svg" id="vowel-trapezoid" version="1.1" x="0px" y="0px" viewBox="130 130 800 450" enable-background="new 130 130 800 450" preserveAspectRatio="xMinYMin meet" xml:space="preserve">

    <text x="295" y="170" text-anchor="middle" class="label">Front</text>
    <text x="440" y="170" text-anchor="middle" class="label">Near-front</text>
    <text x="585" y="170" text-anchor="middle" class="label">Central</text>
    <text x="730" y="170" text-anchor="middle" class="label">Near-back</text>
    <text x="875" y="170" text-anchor="middle" class="label">Back</text>

    <text x="150" y="205" alignment-baseline="baseline" class="label">Close</text>
    <text x="150" y="265" alignment-baseline="baseline" class="label">Near-close</text>
    <text x="150" y="325" alignment-baseline="baseline" class="label">Close-mid</text>
    <text x="150" y="385" alignment-baseline="baseline" class="label">Mid</text>
    <text x="150" y="445" alignment-baseline="baseline" class="label">Open-mid</text>
    <text x="150" y="505" alignment-baseline="baseline" class="label">Near-open</text>
    <text x="150" y="565" alignment-baseline="baseline" class="label">Open</text>

    <g id="Layer_3">
        <line fill="none" stroke="#dddddd" stroke-width="3.2" x2="295" y2="200" x1="585" y1="560" />
        <line fill="none" stroke="#dddddd" stroke-width="3.2" x1="585" y1="200" x2="730" y2="560" />
        <line fill="none" stroke="#dddddd" stroke-width="3.2" x1="875" y1="200" x2="875" y2="560" />

        <line fill="none" stroke="#dddddd" stroke-width="3.2" x1="295" y1="200" x2="875" y2="200" />
        <line fill="none" stroke="#dddddd" stroke-width="3.2" x1="390" y1="320" x2="876" y2="320" />
        <line fill="none" stroke="#dddddd" stroke-width="3.2" x1="485" y1="440" x2="876" y2="440" />
        <line fill="none" stroke="#dddddd" stroke-width="3.2" x1="585" y1="560" x2="876" y2="560" />
    </g>
    <circle fill="#dddddd" cx="295" cy="200" r="10" />
    <text x="295" y="205" text-anchor="middle" class="glyph" id="close-front"> </text>
    <circle fill="#dddddd" cx="585" cy="200" r="10" />
    <text x="585" y="205" text-anchor="middle" class="glyph" id="close-central"> </text>
    <circle fill="#dddddd" cx="875" cy="200" r="10" />
    <text x="875" y="205" text-anchor="middle" class="glyph" id="close-back"> <a href="http://example.org" class="abc">a<title>rounded close back vowel</title></a></text>

    <circle fill="#dddddd" cx="481" cy="260" r="10" />
    <text x="481" y="265" text-anchor="middle" class="glyph" id="nearclose-nearfront"> </text>
    <circle fill="#dddddd" cx="761" cy="260" r="10" />
    <text x="761" y="265" text-anchor="middle" class="glyph" id="nearclose-nearback"> </text>

    <circle fill="#dddddd" cx="390" cy="320" r="10" />
    <text x="390" y="325" text-anchor="middle" class="glyph" id="closemid-front"> </text>
    <circle fill="#dddddd" cx="633" cy="320" r="10" />
    <text x="633" y="325" text-anchor="middle" class="glyph" id="closemid-central"> </text>
    <circle fill="#dddddd" cx="875" cy="320" r="10" />
    <text x="876" y="325" text-anchor="middle" class="glyph" id="closemid-back"> </text>

    <circle fill="#dddddd" cx="658" cy="380" r="10" />
    <text x="658" y="385" text-anchor="middle" class="glyph" id="mid-central"> </text>

    <circle fill="#dddddd" cx="486" cy="440" r="10" />
    <text x="486" y="445" text-anchor="middle" class="glyph" id="openmid-front"> </text>
    <circle fill="#dddddd" cx="682" cy="440" r="10" />
    <text x="682" y="445" text-anchor="middle" class="glyph" id="openmid-central"> </text>
    <circle fill="#dddddd" cx="875" cy="440" r="10" />
    <text x="875" y="445" text-anchor="middle" class="glyph" id="openmid-back"> </text>

    <circle fill="#dddddd" cx="536" cy="500" r="10" />
    <text x="536" y="505" text-anchor="middle" class="glyph" id="nearopen-front"> </text>
    <circle fill="#dddddd" cx="706" cy="500" r="10" />
    <text x="706" y="505" text-anchor="middle" class="glyph" id="nearopen-central"> </text>

    <circle fill="#dddddd" cx="585" cy="560" r="10" />
    <text x="585" y="565" text-anchor="middle" class="glyph" id="open-front"> </text>
    <circle fill="#dddddd" cx="730" cy="560" r="10" />
    <text x="730" y="565" text-anchor="middle" class="glyph" id="open-central"> </text>
    <circle fill="#dddddd" cx="875" cy="560" r="10" />
    <text x="875" y="565" text-anchor="middle" class="glyph" id="open-back"> </text>
<style>@namespace svg url(http://www.w3.org/2000/svg);
svg|a:link, svg|a:visited {cursor: pointer;}
svg|a text, text svg|a {fill: black;}
svg|a {outline: solid 1px white;}
svg|a:hover, svg|a:active {outline: dotted 1px blue;}
svg|a.abc text, text svg|a.abc {fill: red;}
svg|a.abc {outline: solid 1px green;}
svg|a.abc {text-decoration: underline;}
svg|a.abc {text-decoration-style: solid;}
svg|a.abc {text-decoration-color: green;}
</style></svg><figcaption>Vowels</figcaption></figure></div>
</body>
</html>"""


HTML_NO_COLORSPEC = """\
<html>
<head>
<style>
body {font-family: sans-serif}
table caption {text-align: left;}
figure {display: table; margin-left: 0px;}
figcaption {display: table-caption; caption-side: top; font-size: 120%;}
#pulmonic-consonants a {text-decoration: none; font-size: smaller;}
#pulmonic-consonants a {color: black;}
#pulmonic-consonants a {outline: solid 1px solid 1px white;}
#vowel-trapezoid {height: 300px; width: 100%; min-width: 800px;}
#vowel-trapezoid .label {font-size: 150%;}
#vowel-trapezoid .glyph {font-size: 170%;}
</style>
</head>
<body>
<div><table id="pulmonic-consonants" style="font-size:125%; margin-right:1.0em; margin-bottom:0.5em; text-align:center; vertical-align:bottom; border-collapse:collapse; background:transparent;" border="1" cellpadding="1" cellspacing="0" align="left">
    <caption>Pulmonic Consonants</caption>
    <thead>
    <tr style="vertical-align:top; line-height:2.0em; font-size:75%;">
        <td style="border:2px solid; border-width:0px 2px 0px 1px; text-align:right">
            <a title="Place of articulation">Place</a>&#160;&#8594;
        </td>
        <td colspan="5" style="border:1px solid; border-width:0px 1px 1px 0">Labial</td>
        <td colspan="10" style="border:1px solid; border-width:0px 1px 1px 0">Coronal</td>
        <td colspan="6" style="border:1px solid; border-width:0px 1px 1px 0">Dorsal</td>
        <td colspan="5" style="border:1px solid; border-width:0px 1px 1px 0">Laryngeal</td>
    </tr>
    <tr style="vertical-align:top; font-size:75%; border:2px solid; border-width:0px 0px 2px">
        <td style="width:*; border:2px solid; border-width:0px 2px 2px 1px; vertical-align:bottom; text-align:left;">
            &#8595;&#160;<a title="Manner of articulation">Manner</a>
        </td>
        <td colspan="2" style="border:1px solid; border-width:0px 1px 0">Bilabial</td>
        <td colspan="2" style="border:1px solid; border-width:0px 1px 0">Labio&#173;dental</td>
        <td colspan="2" style="border:1px solid; border-width:0px 1px 0">Linguo&#173;labial</td>
        <td colspan="2" style="border:1px solid; border-width:0px 1px 0">Dental</td>
        <td colspan="2" style="border:1px solid; border-width:0px 1px 0">Alveolar</td>
        <td colspan="2" style="border:1px solid; border-width:0px 1px 0">Palato-<br />alveolar</td>
        <td colspan="2" style="border:1px solid; border-width:0px 1px 0">Retroflex</td>
        <td colspan="2" style="border:1px solid; border-width:0px 1px 0">Alveolo-<br />palatal</td>
        <td colspan="2" style="border:1px solid; border-width:0px 1px 0">Palatal</td>
        <td colspan="2" style="border:1px solid; border-width:0px 1px 0">Velar</td>
        <td colspan="2" style="border:1px solid; border-width:0px 1px 0">Uvular</td>
        <td colspan="2" style="border:1px solid; border-width:0px 1px 0">Pharyngeal<br />/&#160;Epiglottal</td>
        <td colspan="2" style="border:1px solid; border-width:0px 1px 1px 0">Glottal</td>
    </tr>
    </thead>
    <tbody>
    <tr>
        <td style="text-align:left; font-size:75%; border:2px solid; border-width:0px 2px 0px 1px">Nasal</td>
        <td class="voiceless-bilabial-nasal" />
        <td class="voiced-bilabial-nasal" />
        <td class="voiceless-labiodental-nasal" />
        <td class="voiced-labiodental-nasal" />
        <td class="voiceless-linguolabial-nasal" />
        <td class="voiced-linguolabial-nasal" />
        <td class="voiceless-dental-nasal" />
        <td class="voiced-dental-nasal" />
        <td class="voiceless-alveolar-nasal" />
        <td class="voiced-alveolar-nasal"><a href="http://example.org" class="abc" title="voiced alveolar nasal consonant">x</a></td>
        <td class="voiceless-postalveolar-nasal" />
        <td class="voiced-postalveolar-nasal" />
        <td class="voiceless-retroflex-nasal" />
        <td class="voiced-retroflex-nasal" />
        <td class="voiceless-alveolopalatal-nasal" />
        <td class="voiced-alveolopalatal-nasal" />
        <td class="voiceless-palatal-nasal" />
        <td class="voiced-palatal-nasal" />
        <td class="voiceless-velar-nasal" />
        <td class="voiced-velar-nasal" />
        <td class="voiceless-uvular-nasal" />
        <td class="voiced-uvular-nasal" />
        <td class="voiceless-epiglottal-nasal" style="border:1px solid; background:#ccc;" />
        <td class="voiced-epiglottal-nasal" style="border:1px solid; background:#ccc;" />
        <td class="voiceless-glottal-nasal" style="border:1px solid; background:#ccc;" />
        <td class="voiced-glottal-nasal" style="border:1px solid; background:#ccc;" />
    </tr>
    <tr>
        <td style="font-size:75%; text-align:left; border:2px solid; border-width:0px 2px 0px 1px">Stop</td>
        <td class="voiceless-bilabial-stop" />
        <td class="voiced-bilabial-stop" />
        <td class="voiceless-labiodental-stop" />
        <td class="voiced-labiodental-stop" />
        <td class="voiceless-linguolabial-stop" />
        <td class="voiced-linguolabial-stop" />
        <td class="voiceless-dental-stop" />
        <td class="voiced-dental-stop" />
        <td class="voiceless-alveolar-stop" />
        <td class="voiced-alveolar-stop" />
        <td class="voiceless-postalveolar-stop" />
        <td class="voiced-postalveolar-stop" />
        <td class="voiceless-retroflex-stop" />
        <td class="voiced-retroflex-stop" />
        <td class="voiceless-alveolopalatal-stop" />
        <td class="voiced-alveolopalatal-stop" />
        <td class="voiceless-palatal-stop" />
        <td class="voiced-palatal-stop" />
        <td class="voiceless-velar-stop" />
        <td class="voiced-velar-stop" />
        <td class="voiceless-uvular-stop" />
        <td class="voiced-uvular-stop" />
        <td class="voiceless-epiglottal-stop" />
        <td class="voiced-epiglottal-stop" />
        <td class="voiceless-glottal-stop" />
        <td class="voiced-glottal-stop" style="border:1px solid; border-left:none; background:#ccc" />
    </tr>
    <tr>
        <td style="font-size:75%; text-align:left; border:2px solid; border-width:0px 2px 0px 1px">Sibilant affricate</td>
        <td class="voiceless-bilabial-sibilant-affricate" style="border:1px solid; background:#ccc;" />
        <td class="voiced-bilabial-sibilant-affricate" style="border:1px solid; background:#ccc;" />
        <td class="voiceless-labiodental-sibilant-affricate" style="border:1px solid; background:#ccc;" />
        <td class="voiced-labiodental-sibilant-affricate" style="border:1px solid; background:#ccc;" />
        <td class="voiceless-linguolabial-sibilant-affricate" style="border:1px solid; background:#ccc;" />
        <td class="voiced-linguolabial-sibilant-affricate" style="border:1px solid; background:#ccc;" />
        <td class="voiceless-dental-sibilant-affricate" />
        <td class="voiced-dental-sibilant-affricate" />
        <td class="voiceless-alveolar-sibilant-affricate" />
        <td class="voiced-alveolar-sibilant-affricate" />
        <td class="voiceless-postalveolar-sibilant-affricate" />
        <td class="voiced-postalveolar-sibilant-affricate" />
        <td class="voiceless-retroflex-sibilant-affricate" />
        <td class="voiced-retroflex-sibilant-affricate" />
        <td class="voiceless-alveolopalatal-sibilant-affricate" />
        <td class="voiced-alveolopalatal-sibilant-affricate" />
        <td class="voiceless-palatal-sibilant-affricate" style="border:1px solid; background:#ccc;" />
        <td class="voiced-palatal-sibilant-affricate" style="border:1px solid; background:#ccc;" />
        <td class="voiceless-velar-sibilant-affricate" style="border:1px solid; background:#ccc;" />
        <td class="voiced-velar-sibilant-affricate" style="border:1px solid; background:#ccc;" />
        <td class="voiceless-uvular-sibilant-affricate" style="border:1px solid; background:#ccc;" />
        <td class="voiced-uvular-sibilant-affricate" style="border:1px solid; background:#ccc;" />
        <td class="voiceless-epiglottal-sibilant-affricate" style="border:1px solid; background:#ccc;" />
        <td class="voiced-epiglottal-sibilant-affricate" style="border:1px solid; background:#ccc;" />
        <td class="voiceless-glottal-sibilant-affricate" style="border:1px solid; background:#ccc;" />
        <td class="voiced-glottal-sibilant-affricate" style="border:1px solid; border-left:none; background:#ccc" />
    </tr>
    <tr>
        <td style="font-size:75%; text-align:left; border:2px solid; border-width:0px 2px 0px 1px">Non-sibilant affricate</td>
        <td class="voiceless-bilabial-NONsibilant-NONlateral-affricate" />
        <td class="voiced-bilabial-NONsibilant-NONlateral-affricate" />
        <td class="voiceless-labiodental-NONsibilant-NONlateral-affricate" />
        <td class="voiced-labiodental-NONsibilant-NONlateral-affricate" />
        <td class="voiceless-linguolabial-NONsibilant-NONlateral-affricate" />
        <td class="voiced-linguolabial-NONsibilant-NONlateral-affricate" />
        <td class="voiceless-dental-NONsibilant-NONlateral-affricate" />
        <td class="voiced-dental-NONsibilant-NONlateral-affricate" />
        <td class="voiceless-alveolar-NONsibilant-NONlateral-affricate" />
        <td class="voiced-alveolar-NONsibilant-NONlateral-affricate" />
        <td class="voiceless-postalveolar-NONsibilant-NONlateral-affricate" />
        <td class="voiced-postalveolar-NONsibilant-NONlateral-affricate" />
        <td class="voiceless-retroflex-NONsibilant-NONlateral-affricate" />
        <td class="voiced-retroflex-NONsibilant-NONlateral-affricate" />
        <td class="voiceless-alveolopalatal-NONsibilant-NONlateral-affricate" />
        <td class="voiced-alveolopalatal-NONsibilant-NONlateral-affricate" />
        <td class="voiceless-palatal-NONsibilant-NONlateral-affricate" />
        <td class="voiced-palatal-NONsibilant-NONlateral-affricate" />
        <td class="voiceless-velar-NONsibilant-NONlateral-affricate" />
        <td class="voiced-velar-NONsibilant-NONlateral-affricate" />
        <td class="voiceless-uvular-NONsibilant-NONlateral-affricate" />
        <td class="voiced-uvular-NONsibilant-NONlateral-affricate" />
        <td class="voiceless-epiglottal-NONsibilant-NONlateral-affricate" />
        <td class="voiced-epiglottal-NONsibilant-NONlateral-affricate" />
        <td class="voiceless-glottal-NONsibilant-NONlateral-affricate" />
        <td class="voiced-glottal-NONsibilant-NONlateral-affricate" style="border:1px solid; border-left:none; background:#ccc" />
    </tr>
    <tr>
        <td style="font-size:75%; text-align:left; border:2px solid; border-width:0px 2px 0px 1px">Sibilant fricative</td>
        <td class="voiceless-bilabial-sibilant-fricative" style="border:1px solid; background:#ccc;" />
        <td class="voiced-bilabial-sibilant-fricative" style="border:1px solid; background:#ccc;" />
        <td class="voiceless-labiodental-sibilant-fricative" style="border:1px solid; background:#ccc;" />
        <td class="voiced-labiodental-sibilant-fricative" style="border:1px solid; background:#ccc;" />
        <td class="voiceless-linguolabial-sibilant-fricative" style="border:1px solid; background:#ccc;" />
        <td class="voiced-linguolabial-sibilant-fricative" style="border:1px solid; background:#ccc;" />
        <td class="voiceless-dental-sibilant-fricative" />
        <td class="voiced-dental-sibilant-fricative" />
        <td class="voiceless-alveolar-sibilant-fricative" />
        <td class="voiced-alveolar-sibilant-fricative" />
        <td class="voiceless-postalveolar-sibilant-fricative" />
        <td class="voiced-postalveolar-sibilant-fricative" />
        <td class="voiceless-retroflex-sibilant-fricative" />
        <td class="voiced-retroflex-sibilant-fricative" />
        <td class="voiceless-alveolopalatal-sibilant-fricative" />
        <td class="voiced-alveolopalatal-sibilant-fricative" />
        <td class="voiceless-palatal-sibilant-fricative" style="border:1px solid; background:#ccc;" />
        <td class="voiced-palatal-sibilant-fricative" style="border:1px solid; background:#ccc;" />
        <td class="voiceless-velar-sibilant-fricative" style="border:1px solid; background:#ccc;" />
        <td class="voiced-velar-sibilant-fricative" style="border:1px solid; background:#ccc;" />
        <td class="voiceless-uvular-sibilant-fricative" style="border:1px solid; background:#ccc;" />
        <td class="voiced-uvular-sibilant-fricative" style="border:1px solid; background:#ccc;" />
        <td class="voiceless-epiglottal-sibilant-fricative" style="border:1px solid; background:#ccc;" />
        <td class="voiced-epiglottal-sibilant-fricative" style="border:1px solid; background:#ccc;" />
        <td class="voiceless-glottal-sibilant-fricative" style="border:1px solid; background:#ccc;" />
        <td class="voiced-glottal-sibilant-fricative" style="border:1px solid; border-left:none; background:#ccc" />
    </tr>
    <tr>
        <td style="font-size:75%; text-align:left; border:2px solid; border-width:0px 2px 0px 1px">Non-sibilant fricative</td>
        <td class="voiceless-bilabial-NONsibilant-NONlateral-fricative" />
        <td class="voiced-bilabial-NONsibilant-NONlateral-fricative" />
        <td class="voiceless-labiodental-NONsibilant-NONlateral-fricative" />
        <td class="voiced-labiodental-NONsibilant-NONlateral-fricative" />
        <td class="voiceless-linguolabial-NONsibilant-NONlateral-fricative" />
        <td class="voiced-linguolabial-NONsibilant-NONlateral-fricative" />
        <td class="voiceless-dental-NONsibilant-NONlateral-fricative" />
        <td class="voiced-dental-NONsibilant-NONlateral-fricative" />
        <td class="voiceless-alveolar-NONsibilant-NONlateral-fricative" />
        <td class="voiced-alveolar-NONsibilant-NONlateral-fricative" />
        <td class="voiceless-postalveolar-NONsibilant-NONlateral-fricative" />
        <td class="voiced-postalveolar-NONsibilant-NONlateral-fricative" />
        <td class="voiceless-retroflex-NONsibilant-NONlateral-fricative" />
        <td class="voiced-retroflex-NONsibilant-NONlateral-fricative" />
        <td class="voiceless-alveolopalatal-NONsibilant-NONlateral-fricative" />
        <td class="voiced-alveolopalatal-NONsibilant-NONlateral-fricative" />
        <td class="voiceless-palatal-NONsibilant-NONlateral-fricative" />
        <td class="voiced-palatal-NONsibilant-NONlateral-fricative" />
        <td class="voiceless-velar-NONsibilant-NONlateral-fricative" />
        <td class="voiced-velar-NONsibilant-NONlateral-fricative" />
        <td class="voiceless-uvular-NONsibilant-NONlateral-fricative" />
        <td class="voiced-uvular-NONsibilant-NONlateral-fricative" />
        <td class="voiceless-epiglottal-NONsibilant-NONlateral-fricative voiceless-pharyngeal-NONsibilant-NONlateral-fricative" />
        <td class="voiced-epiglottal-NONsibilant-NONlateral-fricative voiced-pharyngeal-NONsibilant-NONlateral-fricative" />
        <td class="voiceless-glottal-NONsibilant-NONlateral-fricative" />
        <td class="voiced-glottal-NONsibilant-NONlateral-fricative" />
    </tr>
    <tr>
        <td style="font-size:75%; text-align:left; border:2px solid; border-width:0px 2px 0px 1px"><a title="Approximant consonant">Approximant</a></td>
        <td class="voiceless-bilabial-approximant" />
        <td class="voiced-bilabial-approximant" />
        <td class="voiceless-labiodental-approximant" />
        <td class="voiced-labiodental-approximant" />
        <td class="voiceless-linguolabial-approximant" />
        <td class="voiced-linguolabial-approximant" />
        <td class="voiceless-dental-approximant" />
        <td class="voiced-dental-approximant" />
        <td class="voiceless-alveolar-approximant" />
        <td class="voiced-alveolar-approximant" />
        <td class="voiceless-postalveolar-approximant" />
        <td class="voiced-postalveolar-approximant" />
        <td class="voiceless-retroflex-approximant" />
        <td class="voiced-retroflex-approximant" />
        <td class="voiceless-alveolopalatal-approximant" />
        <td class="voiced-alveolopalatal-approximant" />
        <td class="voiceless-palatal-approximant" />
        <td class="voiced-palatal-approximant" />
        <td class="voiceless-velar-approximant" />
        <td class="voiced-velar-approximant" />
        <td class="voiceless-uvular-approximant" />
        <td class="voiced-uvular-approximant" />
        <td class="voiceless-epiglottal-approximant" />
        <td class="voiced-epiglottal-approximant" />
        <td class="voiceless-glottal-approximant" />
        <td class="voiced-glottal-approximant" />
    </tr>
    <tr>
        <td style="font-size:75%; text-align:left; border:2px solid; border-width:0px 2px 0px 1px"><a title="Flap consonant">Flap or tap</a></td>
        <td class="voiceless-bilabial-tap" />
        <td class="voiced-bilabial-tap" />
        <td class="voiceless-labiodental-tap" />
        <td class="voiced-labiodental-tap" />
        <td class="voiceless-linguolabial-tap" />
        <td class="voiced-linguolabial-tap" />
        <td class="voiceless-dental-tap" />
        <td class="voiced-dental-tap" />
        <td class="voiceless-alveolar-tap" />
        <td class="voiced-alveolar-tap" />
        <td class="voiceless-postalveolar-tap" />
        <td class="voiced-postalveolar-tap" />
        <td class="voiceless-retroflex-tap" />
        <td class="voiced-retroflex-tap" />
        <td class="voiceless-alveolopalatal-tap" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiced-alveolopalatal-tap" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiceless-palatal-tap" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiced-palatal-tap" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiceless-velar-tap" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiced-velar-tap" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiceless-uvular-tap" />
        <td class="voiced-uvular-tap" />
        <td class="voiceless-epiglottal-tap" />
        <td class="voiced-epiglottal-tap" />
        <td class="voiceless-glottal-tap" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiced-glottal-tap" style="border:1px solid; border-left:none; background:#ccc" />
    </tr>
    <tr>
        <td style="font-size:75%; text-align:left; border:2px solid; border-width:0px 2px 0px 1px"><a title="Trill consonant">Trill</a></td>
        <td class="voiceless-bilabial-trill" />
        <td class="voiced-bilabial-trill" />
        <td class="voiceless-labiodental-trill" />
        <td class="voiced-labiodental-trill" />
        <td class="voiceless-linguolabial-trill" />
        <td class="voiced-linguolabial-trill" />
        <td class="voiceless-dental-trill" />
        <td class="voiced-dental-trill" />
        <td class="voiceless-alveolar-trill" />
        <td class="voiced-alveolar-trill" />
        <td class="voiceless-postalveolar-trill" />
        <td class="voiced-postalveolar-trill" />
        <td class="voiceless-retroflex-trill" />
        <td class="voiced-retroflex-trill" />
        <td class="voiceless-alveolopalatal-trill" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiced-alveolopalatal-trill" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiceless-palatal-trill" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiced-palatal-trill" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiceless-velar-trill" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiced-velar-trill" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiceless-uvular-trill" />
        <td class="voiced-uvular-trill" />
        <td class="voiceless-epiglottal-trill" />
        <td class="voiced-epiglottal-trill" />
        <td class="voiceless-glottal-trill" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiced-glottal-trill" style="border:1px solid; border-left:none; background:#ccc" />
    </tr>
    <tr>
        <td style="font-size:75%; text-align:left; border:2px solid; border-width:0px 2px 0px 1px"><a title="Lateral consonant">Lateral</a>&#160;<a title="Affricate consonant">affricate</a></td>
        <td class="voiceless-bilabial-lateral-affricate" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiced-bilabial-lateral-affricate" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiceless-labiodental-lateral-affricate" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiced-labiodental-lateral-affricate" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiceless-linguolabial-lateral-affricate" />
        <td class="voiced-linguolabial-lateral-affricate" />
        <td class="voiceless-dental-lateral-affricate" />
        <td class="voiced-dental-lateral-affricate" />
        <td class="voiceless-alveolar-lateral-affricate" />
        <td class="voiced-alveolar-lateral-affricate" />
        <td class="voiceless-postalveolar-lateral-affricate" />
        <td class="voiced-postalveolar-lateral-affricate" />
        <td class="voiceless-retroflex-lateral-affricate" />
        <td class="voiced-retroflex-lateral-affricate" />
        <td class="voiceless-alveolopalatal-lateral-affricate" />
        <td class="voiced-alveolopalatal-lateral-affricate" />
        <td class="voiceless-palatal-lateral-affricate" />
        <td class="voiced-palatal-lateral-affricate" />
        <td class="voiceless-velar-lateral-affricate" />
        <td class="voiced-velar-lateral-affricate" />
        <td class="voiceless-uvular-lateral-affricate" />
        <td class="voiced-uvular-lateral-affricate" />
        <td class="voiceless-epiglottal-lateral-affricate" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiced-epiglottal-lateral-affricate" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiceless-glottal-lateral-affricate" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiced-glottal-lateral-affricate" style="border:1px solid; border-left:none; background:#ccc" />
    </tr>
    <tr>
        <td style="font-size:75%; text-align:left; border:2px solid; border-width:0px 2px 0px 1px"><a title="Lateral consonant">Lateral</a>&#160;<a title="Fricative consonant">fricative</a></td>
        <td class="voiceless-bilabial-lateral-fricative" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiced-bilabial-lateral-fricative" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiceless-labiodental-lateral-fricative" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiced-labiodental-lateral-fricative" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiceless-linguolabial-lateral-fricative" />
        <td class="voiced-linguolabial-lateral-fricative" />
        <td class="voiceless-dental-lateral-fricative" />
        <td class="voiced-dental-lateral-fricative" />
        <td class="voiceless-alveolar-lateral-fricative" />
        <td class="voiced-alveolar-lateral-fricative" />
        <td class="voiceless-postalveolar-lateral-fricative" />
        <td class="voiced-postalveolar-lateral-fricative" />
        <td class="voiceless-retroflex-lateral-fricative" />
        <td class="voiced-retroflex-lateral-fricative" />
        <td class="voiceless-alveolopalatal-lateral-fricative" />
        <td class="voiced-alveolopalatal-lateral-fricative" />
        <td class="voiceless-palatal-lateral-fricative" />
        <td class="voiced-palatal-lateral-fricative" />
        <td class="voiceless-velar-lateral-fricative" />
        <td class="voiced-velar-lateral-fricative" />
        <td class="voiceless-uvular-lateral-fricative" />
        <td class="voiced-uvular-lateral-fricative" />
        <td class="voiceless-epiglottal-lateral-fricative" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiced-epiglottal-lateral-fricative" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiceless-glottal-lateral-fricative" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiced-glottal-lateral-fricative" style="border:1px solid; border-left:none; background:#ccc" />
    </tr>
    <tr>
        <td style="font-size:75%; text-align:left; border:2px solid; border-width:0px 2px 0px 1px"><a title="Lateral consonant">Lateral</a>&#160;<a title="Approximant consonant">approximant</a></td>
        <td class="voiceless-bilabial-lateral-approximant" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiced-bilabial-lateral-approximant" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiceless-labiodental-lateral-approximant" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiced-labiodental-lateral-approximant" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiceless-linguolabial-lateral-approximant" />
        <td class="voiced-linguolabial-lateral-approximant" />
        <td class="voiceless-dental-lateral-approximant" />
        <td class="voiced-dental-lateral-approximant" />
        <td class="voiceless-alveolar-lateral-approximant" />
        <td class="voiced-alveolar-lateral-approximant" />
        <td class="voiceless-postalveolar-lateral-approximant" />
        <td class="voiced-postalveolar-lateral-approximant" />
        <td class="voiceless-retroflex-lateral-approximant" />
        <td class="voiced-retroflex-lateral-approximant" />
        <td class="voiceless-alveolopalatal-lateral-approximant" />
        <td class="voiced-alveolopalatal-lateral-approximant" />
        <td class="voiceless-palatal-lateral-approximant" />
        <td class="voiced-palatal-lateral-approximant" />
        <td class="voiceless-velar-lateral-approximant" />
        <td class="voiced-velar-lateral-approximant" />
        <td class="voiceless-uvular-lateral-approximant" />
        <td class="voiced-uvular-lateral-approximant" />
        <td class="voiceless-epiglottal-lateral-approximant" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiced-epiglottal-lateral-approximant" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiceless-glottal-lateral-approximant" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiced-glottal-lateral-approximant" style="border:1px solid; border-left:none; background:#ccc" />
    </tr>
    <tr>
        <td style="font-size:75%; text-align:left; border:2px solid; border-width:0px 2px 1px 1px"><a title="Lateral flap">Lateral flap</a></td>
        <td class="voiceless-bilabial-lateral-tap" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiced-bilabial-lateral-tap" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiceless-labiodental-lateral-tap" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiced-labiodental-lateral-tap" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiceless-linguolabial-lateral-tap" />
        <td class="voiced-linguolabial-lateral-tap" />
        <td class="voiceless-dental-lateral-tap" />
        <td class="voiced-dental-lateral-tap" />
        <td class="voiceless-alveolar-lateral-tap" />
        <td class="voiced-alveolar-lateral-tap" />
        <td class="voiceless-postalveolar-lateral-tap" />
        <td class="voiced-postalveolar-lateral-tap" />
        <td class="voiceless-retroflex-lateral-tap" />
        <td class="voiced-retroflex-lateral-tap" />
        <td class="voiceless-alveolopalatal-lateral-tap" />
        <td class="voiced-alveolopalatal-lateral-tap" />
        <td class="voiceless-palatal-lateral-tap" />
        <td class="voiced-palatal-lateral-tap" />
        <td class="voiceless-velar-lateral-tap" />
        <td class="voiced-velar-lateral-tap" />
        <td class="voiceless-uvular-lateral-tap" />
        <td class="voiced-uvular-lateral-tap" />
        <td class="voiceless-epiglottal-lateral-tap" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiced-epiglottal-lateral-tap" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiceless-glottal-lateral-tap" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiced-glottal-lateral-tap" style="border:1px solid; border-left:none; background:#ccc" />
    </tr>
    <tr>
        <td style="font-size:75%; text-align:left; border:2px solid; border-width:0px 2px 1px 1px">Implosive</td>
        <td class="voiceless-bilabial-lateral-implosive" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiced-bilabial-lateral-implosive" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiceless-labiodental-lateral-implosive" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiced-labiodental-lateral-implosive" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiceless-linguolabial-lateral-implosive" />
        <td class="voiced-linguolabial-lateral-implosive" />
        <td class="voiceless-dental-lateral-implosive" />
        <td class="voiced-dental-lateral-implosive" />
        <td class="voiceless-alveolar-lateral-implosive" />
        <td class="voiced-alveolar-lateral-implosive" />
        <td class="voiceless-postalveolar-lateral-implosive" />
        <td class="voiced-postalveolar-lateral-implosive" />
        <td class="voiceless-retroflex-lateral-implosive" />
        <td class="voiced-retroflex-lateral-implosive" />
        <td class="voiceless-alveolopalatal-lateral-implosive" />
        <td class="voiced-alveolopalatal-lateral-implosive" />
        <td class="voiceless-palatal-lateral-implosive" />
        <td class="voiced-palatal-lateral-implosive" />
        <td class="voiceless-velar-lateral-implosive" />
        <td class="voiced-velar-lateral-implosive" />
        <td class="voiceless-uvular-lateral-implosive" />
        <td class="voiced-uvular-lateral-implosive" />
        <td class="voiceless-epiglottal-lateral-implosive" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiced-epiglottal-lateral-implosive" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiceless-glottal-lateral-implosive" style="border:1px solid; border-left:none; background:#ccc" />
        <td class="voiced-glottal-lateral-implosive" style="border:1px solid; border-left:none; background:#ccc" />
    </tr>
    </tbody>
</table></div>
<div><figure><svg xmlns="http://www.w3.org/2000/svg" id="vowel-trapezoid" version="1.1" x="0px" y="0px" viewBox="130 130 800 450" enable-background="new 130 130 800 450" preserveAspectRatio="xMinYMin meet" xml:space="preserve">

    <text x="295" y="170" text-anchor="middle" class="label">Front</text>
    <text x="440" y="170" text-anchor="middle" class="label">Near-front</text>
    <text x="585" y="170" text-anchor="middle" class="label">Central</text>
    <text x="730" y="170" text-anchor="middle" class="label">Near-back</text>
    <text x="875" y="170" text-anchor="middle" class="label">Back</text>

    <text x="150" y="205" alignment-baseline="baseline" class="label">Close</text>
    <text x="150" y="265" alignment-baseline="baseline" class="label">Near-close</text>
    <text x="150" y="325" alignment-baseline="baseline" class="label">Close-mid</text>
    <text x="150" y="385" alignment-baseline="baseline" class="label">Mid</text>
    <text x="150" y="445" alignment-baseline="baseline" class="label">Open-mid</text>
    <text x="150" y="505" alignment-baseline="baseline" class="label">Near-open</text>
    <text x="150" y="565" alignment-baseline="baseline" class="label">Open</text>

    <g id="Layer_3">
        <line fill="none" stroke="#dddddd" stroke-width="3.2" x2="295" y2="200" x1="585" y1="560" />
        <line fill="none" stroke="#dddddd" stroke-width="3.2" x1="585" y1="200" x2="730" y2="560" />
        <line fill="none" stroke="#dddddd" stroke-width="3.2" x1="875" y1="200" x2="875" y2="560" />

        <line fill="none" stroke="#dddddd" stroke-width="3.2" x1="295" y1="200" x2="875" y2="200" />
        <line fill="none" stroke="#dddddd" stroke-width="3.2" x1="390" y1="320" x2="876" y2="320" />
        <line fill="none" stroke="#dddddd" stroke-width="3.2" x1="485" y1="440" x2="876" y2="440" />
        <line fill="none" stroke="#dddddd" stroke-width="3.2" x1="585" y1="560" x2="876" y2="560" />
    </g>
    <circle fill="#dddddd" cx="295" cy="200" r="10" />
    <text x="295" y="205" text-anchor="middle" class="glyph" id="close-front"> </text>
    <circle fill="#dddddd" cx="585" cy="200" r="10" />
    <text x="585" y="205" text-anchor="middle" class="glyph" id="close-central"> </text>
    <circle fill="#dddddd" cx="875" cy="200" r="10" />
    <text x="875" y="205" text-anchor="middle" class="glyph" id="close-back"> <a href="http://example.org" class="abc">a<title>rounded close back vowel</title></a></text>

    <circle fill="#dddddd" cx="481" cy="260" r="10" />
    <text x="481" y="265" text-anchor="middle" class="glyph" id="nearclose-nearfront"> </text>
    <circle fill="#dddddd" cx="761" cy="260" r="10" />
    <text x="761" y="265" text-anchor="middle" class="glyph" id="nearclose-nearback"> </text>

    <circle fill="#dddddd" cx="390" cy="320" r="10" />
    <text x="390" y="325" text-anchor="middle" class="glyph" id="closemid-front"> </text>
    <circle fill="#dddddd" cx="633" cy="320" r="10" />
    <text x="633" y="325" text-anchor="middle" class="glyph" id="closemid-central"> </text>
    <circle fill="#dddddd" cx="875" cy="320" r="10" />
    <text x="876" y="325" text-anchor="middle" class="glyph" id="closemid-back"> </text>

    <circle fill="#dddddd" cx="658" cy="380" r="10" />
    <text x="658" y="385" text-anchor="middle" class="glyph" id="mid-central"> </text>

    <circle fill="#dddddd" cx="486" cy="440" r="10" />
    <text x="486" y="445" text-anchor="middle" class="glyph" id="openmid-front"> </text>
    <circle fill="#dddddd" cx="682" cy="440" r="10" />
    <text x="682" y="445" text-anchor="middle" class="glyph" id="openmid-central"> </text>
    <circle fill="#dddddd" cx="875" cy="440" r="10" />
    <text x="875" y="445" text-anchor="middle" class="glyph" id="openmid-back"> </text>

    <circle fill="#dddddd" cx="536" cy="500" r="10" />
    <text x="536" y="505" text-anchor="middle" class="glyph" id="nearopen-front"> </text>
    <circle fill="#dddddd" cx="706" cy="500" r="10" />
    <text x="706" y="505" text-anchor="middle" class="glyph" id="nearopen-central"> </text>

    <circle fill="#dddddd" cx="585" cy="560" r="10" />
    <text x="585" y="565" text-anchor="middle" class="glyph" id="open-front"> </text>
    <circle fill="#dddddd" cx="730" cy="560" r="10" />
    <text x="730" y="565" text-anchor="middle" class="glyph" id="open-central"> </text>
    <circle fill="#dddddd" cx="875" cy="560" r="10" />
    <text x="875" y="565" text-anchor="middle" class="glyph" id="open-back"> </text>
<style>@namespace svg url(http://www.w3.org/2000/svg);
svg|a:link, svg|a:visited {cursor: pointer;}
svg|a text, text svg|a {fill: black;}
svg|a {outline: solid 1px solid 1px white;}
svg|a:hover, svg|a:active {outline: dotted 1px blue;}
</style></svg><figcaption>Vowels</figcaption></figure></div>
</body>
</html>"""