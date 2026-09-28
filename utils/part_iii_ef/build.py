import copy
import html
import json
import re
import uuid
import zipfile
from pathlib import Path
from urllib.parse import urlencode

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'docs/part_III'
BASE = OUT / 'III_A_Q7_Counting_Names'
with zipfile.ZipFile(Path(str(BASE) + '.h5p')) as z:
    manifest = json.loads(z.read('h5p.json'))
    book = json.loads(z.read('content/content.json'))
mc_template = copy.deepcopy(book['chapters'][0]['params']['content'][1]['content']['params'])
export_html = Path(str(BASE) + '.html').read_text()
prefix = 'H5PIntegration = '
start = export_html.index(prefix) + len(prefix)
integration, consumed = json.JSONDecoder().raw_decode(export_html[start:])

def item(library, params, title):
    return {'library': library, 'params': params, 'subContentId': str(uuid.uuid5(uuid.NAMESPACE_URL, 'ling2200/part_iii_ef/' + library + '/' + title)),
            'metadata': {'title': title, 'extraTitle': title, 'license': 'U', 'authors': [], 'changes': []}}

def text(title, body):
    return item('H5P.AdvancedText 1.1', {'text': f'<h2>{title}</h2>{body}'}, title)

def question(title, body, answers):
    p = copy.deepcopy(mc_template)
    p['question'] = f'<h3>{title}</h3>{body}'
    # Keep the correct answer from occupying a predictable position.
    p['behaviour']['randomAnswers'] = True
    p['answers'] = [{'text': '<p>' + label + '</p>', 'correct': correct,
                     'tipsAndFeedback': {'tip': '', 'chosenFeedback': feedback, 'notChosenFeedback': ''}}
                    for label, correct, feedback in answers]
    return item('H5P.MultiChoice 1.16', p, title)

def chapter(title, *parts):
    return item('H5P.Column 1.18', {'content': [{'content': p, 'useSeparator': 'disabled'} for p in parts]}, title)

PARTNER = '<p>Work with a partner. Before you choose an answer, write down what you think will happen. Tell your partner why. Your partner can try an example to check your idea. Switch roles on each page. Select Check to get feedback. If you need another try, select Retry. At the end, write your own function in the course notebook.</p>'

def build(stem, title, chapters, source):
    content = copy.deepcopy(book)
    content['chapters'] = copy.deepcopy(chapters)
    for c in content['chapters']:
        for unit in c['params']['content']:
            params = unit['content']['params']
            if 'text' in params:
                params['text'] = re.sub(r'<h3>Learning goals</h3><p>(.*?)</p>', lambda m: '<h3>Learning goals</h3><ul>' + ''.join('<li>' + goal.strip().capitalize() + '</li>' for goal in m[1].split(';')) + '</ul>', params['text'])
    content['bookCover']['coverDescription'] = f'<p>{title}</p>'
    m = copy.deepcopy(manifest)
    m['title'] = m['extraTitle'] = title
    # Keep installed library dependencies, including editor libraries, for Lumi import.
    with zipfile.ZipFile(Path(str(BASE) + '.h5p')) as src, zipfile.ZipFile(OUT / (stem + '.h5p'), 'w', zipfile.ZIP_DEFLATED) as dest:
        for info in src.infolist():
            if info.filename.startswith('content/') or info.filename == 'h5p.json':
                continue
            data = src.read(info.filename)
            if info.filename.endswith('.js') and 'H5P.InteractiveBook-' in info.filename:
                data = data.replace(b'l10n.exitFullScreen', b'l10n.exitFullscreen')
            dest.writestr(info, data)
        dest.writestr('h5p.json', json.dumps(m, ensure_ascii=False))
        dest.writestr('content/content.json', json.dumps(content, ensure_ascii=False))
    d = copy.deepcopy(integration)
    v = next(iter(d['contents'].values()))
    v['jsonContent'] = json.dumps(content, ensure_ascii=False)
    v['metadata']['title'] = title
    # Standalone drafts have no hosted public URL yet.
    v['url'] = ''
    v['exportUrl'] = ''
    page = export_html[:start] + json.dumps(d, ensure_ascii=False).replace('</', '<\\/') + export_html[start + consumed:]
    # Correct upstream InteractiveBook 1.11's exit-fullscreen aria-label typo.
    page = page.replace('l10n.exitFullScreen', 'l10n.exitFullscreen')
    # Reconstruct a raw standalone export, then apply the current teacher formatter.
    runtime_start = page.index('<script>H5PIntegration = ')
    core_start = page.index('<style>/*!@license styles/h5p.css', runtime_start)
    core_end = page.index('</style>', core_start) + len('</style>')
    raw = '<!doctype html>\n<html lang="en" class="h5p-iframe">\n<head>\n' + page[runtime_start:core_end] + '\n</head>\n<body>\n<div style="margin: 0px 0px;">\n<div style="" class="h5p-content lag" data-content-id="4096308226"></div>\n</div>\n</body>\n</html>'
    import importlib.util
    spec = importlib.util.spec_from_file_location('brand', ROOT / 'utils/h5p_brand.py')
    brand = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(brand)
    page = brand.transform(raw, title=title, part_dir='part_III')
    page = page.replace('<head>', '<head><meta charset="UTF-8"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Merriweather:wght@400;700;800&amp;family=Merriweather+Sans:wght@400;600;700&amp;display=swap">', 1)
    page = page.replace('<div class="text-center mb-4">', '<div class="text-center mb-4" role="banner">', 1)
    page = page.replace('<div class="applet-wrapper">', '<main class="applet-wrapper" aria-label="' + title + '">', 1)
    page = page.replace('        </div>       \n        </div>', '        </div>       \n        </main>', 1)
    page = page.replace('</head>', '<meta charset="UTF-8"><style>a:focus-visible,button:focus-visible,[tabindex]:focus-visible{outline:3px solid #0055a4;outline-offset:3px}.h5p-advanced-text{line-height:1.6}.h5p-alternative-inner p{font-weight:400!important;font-size:1rem!important}code{overflow-wrap:anywhere}</style></head>')
    from urllib.parse import quote
    live = 'https://uga-ling2200.github.io/applets/part_III/' + stem + '.html'
    page = re.sub(r'(&amp;source-url=)[^"\s]*', lambda match: match[1] + quote(live, safe=''), page)
    (OUT / (stem + '.html')).write_text(page)
    (Path(__file__).parent / (stem + '_content.json')).write_text(json.dumps(content, ensure_ascii=False, indent=2))
    return len(chapters), sum(p['content']['library'].startswith('H5P.MultiChoice') for c in chapters for p in c['params']['content'])


def q(title, body, correct, wrong1, wrong2):
    return question(title, body, [(correct[0],True,correct[1]),(wrong1[0],False,wrong1[1]),(wrong2[0],False,wrong2[1])])
def diagram(word):
    cells=''.join('<th scope="col">'+html.escape(c if c!=' ' else 'space')+'</th>' for c in word)
    row=lambda vals: ''.join('<td>'+str(v)+'</td>' for v in vals)
    return '<table><caption>Characters and their positions in '+html.escape(repr(word))+'</caption><thead><tr><th scope="col">Character</th>'+cells+'</tr></thead><tbody><tr><th scope="row">Positive index</th>'+row(range(len(word)))+'</tr><tr><th scope="row">Negative index</th>'+row(range(-len(word),0))+'</tr></tbody></table>'
E=[
chapter('1. Map the positions',
 text('Read positions before writing code','<p>III.E Q1 · Slicing</p><h3>Notebook task</h3><ul><li>Write <code>reverse(group)</code>.</li><li>Accept a string, tuple, or list and return its items in reverse order.</li><li>The returned sequence keeps the input type.</li></ul><h3>Learning goals</h3><ul><li><strong>Trace</strong> the positions visited by a slice.</li><li><strong>Explain</strong> how boundaries and step direction affect the result.</li><li><strong>Test</strong> a reversal on different sequence types.</li></ul>'+PARTNER+'<p>On paper, write <code>"plant"</code> in five boxes. Add positive and negative indices. Then write the order in which you would visit the boxes to read the word backward. A negative index names a position; it does not, by itself, choose a direction.</p>'+diagram('plant')),
 q('Locate the starting item','<p>Which pair of indices refers to the final character of <code>"plant"</code>?</p>',('4 and -1','Both name the t. Now trace a move one place to the left.'),('5 and -1','Count from zero at the left. Is there a position 5 in a five-character string?'),('4 and 0','Zero refers to the first character. Negative positions count from the right.')),
 q('Read a negative position','<p>What does <code>"plant"[-2]</code> select?</p>',('The character n','Yes. This is a single-item lookup; no direction of travel is specified.'),('The characters tn','That would require more than one item. An index selects one item.'),('The character l','That is index 1, or -4. Count backward starting at -1.'))),
chapter('2. Compare slice boundaries',
 text('Predict before checking','<p>A slice is written <code>sequence[start:stop:step]</code>. The starting position is included; the stopping position is excluded. First compare these forward slices on paper: <code>"plant"[1:4]</code> and <code>"plant"[1:3]</code>. Change only one boundary. Which character changes?</p>'+diagram('plant')),
 q('Follow the first slice','<p>Which result matches <code>"plant"[1:4]</code>?</p>',('"lan"','Positions 1, 2, and 3 are included. Position 4 is the excluded boundary.'),('"lant"','You included the character at stop. Stop is excluded.'),('"la"','Check position 3. It is still before stop=4.')),
 q('Slice or index?','<p>For <code>items = ("oak", "elm", "ash")</code>, what is the type of <code>items[1:2]</code>?</p>',('tuple','A slice of a tuple remains a tuple, even with one item. Compare this with items[1].'),('str','That is the type of the item selected by indexing. A slice retains the surrounding sequence type.'),('list','Slicing does not automatically change a tuple into a list.'))),
chapter('3. Change the direction',
 text('Trace the steps','<p>Compare <code>"plant"[4:1:1]</code> and <code>"plant"[4:1:-1]</code>. Write the starting index, then repeatedly add the step. Stop before the excluded boundary. Which direction can reach the requested part of the word?</p><p>The step plays a similar role in <code>range()</code>. Here, focus on positions within the sequence.</p>'),
 q('Move from right to left','<p>Which index sequence is visited by <code>"plant"[4:1:-1]</code>?</p>',('4, 3, 2','Adding -1 moves left. Stop=1 excludes index 1; the resulting text is "tna".'),('4, 3, 2, 1','The direction is right, but stop=1 is excluded.'),('1, 2, 3','That moves in the opposite direction and starts at the wrong boundary.')),
 q('A direction mismatch','<p>What does <code>"plant"[4:1:1]</code> produce?</p>',('An empty string','A positive step cannot move from position 4 toward the lower stop boundary.'),('"tna"','That requires movement to the left. Which sign would the step need?'),('An IndexError','The mismatch gives an empty slice rather than an indexing error.')),
 q('A step of zero','<p>What happens when a slice uses <code>step=0</code>?</p>',('Python raises a ValueError','A zero step is invalid. It does not describe movement through positions.'),('Python repeats the starting item','Slicing does not use zero to repeat an item.'),('Python returns an empty sequence','Direction mismatches can be empty; a zero step is an error.'))),
chapter('4. Reach the edges',
 text('Look for a missing character','<p>Using your diagram, predict <code>"plant"[4:0:-1]</code>. Does it include every character? Now consider what it means to leave the stop field blank. Compare an omitted stop with an explicit stop of <code>0</code> or <code>-1</code>. Predict each result before checking.</p><p>Try your own prediction in the practice lab below this book. Change one field at a time. Leave a field blank to omit it; typing zero is a different choice.</p>'),
 q('Find the omitted item','<p>Which character is missing from <code>"plant"[4:0:-1]</code>?</p>',('p','Index 0 is excluded. How could you let the slice reach that edge?'),('t','Index 4 is the starting position and is included.'),('No character is missing','Trace 4, 3, 2, 1. Would index 0 be visited?')),
 q('Blank is not minus one','<p>Compare <code>"plant"[4::-1]</code> with <code>"plant"[4:-1:-1]</code>. Which statement is correct?</p>',('The first reaches p; the second is empty','An explicit -1 refers to the final character. It is the same position as start=4 here. Omitted stop has a different meaning.'),('Both include every character','An explicit -1 is a real position in the string, not a boundary before its beginning.'),('The first is empty; the second reaches p','The omitted stop allows travel through index 0. An explicit -1 does not mean the same thing.'))),
chapter('5. Generalize and test',
 text('Return to III.E Q1','<p>Build your own slice for <code>reverse(group)</code>. It must work for different lengths without a fixed starting index. The original exercise suggests a negative step. Explain your choice of both boundaries before writing code in the notebook.</p><h3>Test your function</h3><ul><li>A string: <code>"hello"</code>.</li><li>A tuple: <code>(3, 8, 2)</code>.</li><li>A list: <code>["red", "blue"]</code>.</li><li>An empty sequence and a one-item sequence of each type.</li></ul><p>Predict the value and type before each test. Check that the original list has not changed. A printed result alone does not meet the requirement to return a sequence.</p><h3>Discuss</h3><ol><li>How does a negative index differ from a negative step?</li><li>Why might a backward slice miss the first item?</li><li>Which boundary choices adapt to a different length?</li></ol>'),
 q('Check the return type','<p>For input <code>[3, 8, 2]</code>, which result meets the task?</p>',('<code>[2, 8, 3]</code>, returned as a list','Both the order and sequence type are correct.'),('<code>(2, 8, 3)</code>, returned as a tuple','The order is correct, but the input type was list.'),('<code>"283"</code>, returned as a string','Changing the type loses the original list structure.')),
 q('Test the smallest input','<p>What should reversing an empty tuple return?</p>',('An empty tuple','The operation still returns a tuple; there are no items to reorder.'),('An empty string','The type must remain tuple.'),('An error','An empty sequence can be reversed without accessing a nonexistent item.')))
]
F=[
chapter('1. Identify what stays',
 text('Read the result before planning the edits','<p>III.F Q4 · Strings and slicing</p><h3>Notebook task</h3><ul><li>Write <code>remove_parentheticals(string)</code>.</li><li>Remove parentheses and the text inside them.</li><li>Retain a single space where the surviving text on both sides meets.</li><li>Extend the function to more than one parenthetical; the original task assumes at least one.</li></ul><h3>Learning goals</h3><ul><li><strong>Locate</strong> the boundaries of a parenthetical.</li><li><strong>Compare</strong> slices and the spaces they retain.</li><li><strong>Explain</strong> why positions change after an edit.</li></ul>'+PARTNER+'<p>A parenthetical is text enclosed in parentheses, like <code>(kind of)</code>. The original example changes <code>"That\'s (kind of) good"</code> into <code>"That\'s good"</code>. Practice here uses separate, matched pairs, as in the course examples. Nested or unmatched parentheses are not specified in the question.</p>'),
 q('Preserve the outside words','<p>For <code>"We (quietly) left"</code>, which result meets the task?</p>',('"We left"','The outside words remain, with one space where they meet.'),('"We quietly left"','This removes the parentheses but keeps their contents.'),('"Weleft"','This removes the space between the surviving words.')),
 q('Check repeated letters','<p>In <code>"go (go) go"</code>, which occurrences of <code>go</code> should survive?</p>',('The first and third','Position relative to the parentheses determines what stays.'),('Only the first','The final go is also outside parentheses.'),('None of them','Deleting every matching word would also remove text outside the parentheses.'))),
chapter('2. Locate the boundaries',
 text('Find positions, not matching words','<p>Write <code>"A (x) B"</code> in seven boxes, including the spaces. Locate the opening and closing parentheses. Think about where a left slice should stop and a right slice should start if neither parenthesis should remain.</p>'+diagram('A (x) B')+'<p><code>str.find()</code> returns the first matching position. If there is no match, it returns <code>-1</code>; that result means not found, rather than an instruction to select the last character.</p>'),
 q('Choose the left boundary','<p>In <code>"A (x) B"</code>, which stop value keeps the text before the opening parenthesis and excludes that parenthesis?</p>',('2','The opening parenthesis is at index 2. A slice stops before its stop position.'),('3','That would also retain the opening parenthesis at index 2.'),('1','That would exclude the space at index 1 too. First separate boundary selection from space cleanup.')),
 q('Choose the right boundary','<p>The closing parenthesis is at index 4. Where should the right slice begin to exclude it?</p>',('5','The next character is at index 5. The closing parenthesis is left behind.'),('4','A slice includes its starting position, so the closing parenthesis would remain.'),('6','That skips the space as well. First preserve the complete outside portion.'))),
chapter('3. Inspect the spaces',
 text('Explain the first attempt','<p>For <code>"We (quietly) left"</code>, the two outside pieces are <code>"We "</code> and <code>" left"</code>. Draw the spaces as separate boxes. Predict what joining these pieces directly would produce.</p><p>Now try a parenthetical at an edge: <code>"We left (quietly)"</code>. One outside piece has no remaining words. Should joining always insert an extra space? Use the editing lab below to compare results before and after cleaning the join.</p>'),
 q('Count spaces at the join','<p>How many spaces occur between the words after directly joining <code>"We "</code> and <code>" left"</code>?</p>',('2','Each piece contributes one space. Concatenation does not remove either one.'),('1','Python does not automatically combine two spaces into one.'),('0','Concatenation preserves the existing characters, including spaces.')),
 q('Avoid a space at the edge','<p>After removing <code>(quietly)</code> from <code>"We left (quietly)"</code>, which cleanup best fits the task?</p>',('Keep "We left" without adding a trailing space','There is no surviving text on the right that needs a separating space.'),('Always add one space after "We left"','A separator is useful between surviving pieces, not after an empty right piece.'),('Remove all spaces to make "Weleft"','Spaces inside the surviving phrase are not part of the parenthetical.'))),
chapter('4. Handle repeated parentheses',
 text('Recheck positions after an edit','<p>On paper, cross out just the first parenthetical in <code>"A (x) B (y) C"</code>. Write the new string and renumber its characters. Then locate the next pair. Are its indices the same as before?</p><p>Compare that plan with deleting everything from the first opening parenthesis through the last closing parenthesis. Explain which outside text that larger deletion would lose.</p>'),
 q('Do not delete too much','<p>In <code>"A (x) B (y) C"</code>, what outside text is wrongly removed if one deletion runs from the first opening parenthesis through the last closing parenthesis?</p>',('B','B is between two separate parentheticals and should remain.'),('A','A lies before the first opening parenthesis, outside that deletion.'),('C','C lies after the last closing parenthesis, outside that deletion.')),
 q('Which string supplies the next indices?','<p>After the first parenthetical is removed, where should you find the next pair’s positions?</p>',('In the updated string','Earlier edits change length and therefore later positions. Search the current text.'),('In the original string using the old positions','Those positions may no longer identify the same characters.'),('By reusing the first pair’s positions','The next pair can appear at a different place.')),
 q('Know when to stop','<p>A search for the next opening parenthesis returns <code>-1</code>. What does that tell you?</p>',('No opening parenthesis remains','There is no next pair to process under the matched-pair assumptions.'),('Remove the last character','Here -1 is a search result meaning not found, not a requested index.'),('Start again from the original string','That would bring back text already removed instead of finishing.'))),
chapter('5. Plan, implement, test',
 text('Return to III.F Q4','<p>Explain your plan for one pair, including the join. Then describe what must be repeated, what changes after each edit, and how you will know when to stop. Write your own function in the notebook.</p><h3>Make a test table</h3><ul><li>Original example: <code>"That\'s (kind of) good"</code>.</li><li>Repeated pairs: <code>"That\'s (kind of) good (I think)"</code>.</li><li>Repeated words: <code>"go (go) go"</code>.</li><li>A pair at the beginning: <code>"(maybe) We can go"</code>.</li><li>Only a parenthetical: <code>"(aside)"</code>.</li></ul><p>Predict the output before running each case. Use a representation that lets you check leading, trailing, and doubled spaces. Include a case with no text outside the parentheses, and explain what your function should return.</p><h3>Discuss</h3><ol><li>Why can removing a matching word delete too much?</li><li>Why can correct slice boundaries still leave an incorrect space?</li><li>What changes after each removal, and why must the next search use that new text?</li></ol>'),
 q('A repeated-pair check','<p>Which output fits <code>"A (x) B (y) C"</code>?</p>',('"A B C"','All three outside pieces remain, with single spaces at the joins.'),('"A C"','This loses B, which was outside both pairs.'),('"A B (y) C"','This stops after only the first removal.')),
 q('No outside words remain','<p>What should remain from <code>"(aside)"</code>?</p>',('An empty string','Every character belongs to the parenthetical, including the opening and closing parentheses.'),('A single space','There are no surviving pieces to separate.'),('"aside"','The contents must be removed along with the parentheses.')))
]
for stem,title,chapters,file in [('III_E_Q1_Reversing_Sequences','III.E Slicing, Q1 — Reversing Sequences',E,'III.E_Slicing.ipynb'),('III_F_Q4_Removing_Parentheticals','III.F Strings, Q4 — Removing Parentheticals',F,'III.F_Strings_III.ipynb')]:
    source='https://github.com/uga-ling2200/prep/blob/master/classnotes/week08/'+file
    chapters[-1]['params']['content'][0]['content']['params']['text']+='<p><a href="'+source+'" target="_blank" rel="noopener noreferrer">Open the original course notebook (new tab)</a></p>'
    print(stem,build(stem,title,chapters,source))

for stem,mode in [('III_E_Q1_Reversing_Sequences','slice'),('III_F_Q4_Removing_Parentheticals','edit')]:
    options='<option value="word">String: plant</option><option value="tuple">Tuple of numbers</option><option value="list">List of colors</option><option value="empty">Empty list</option><option value="single">One-item tuple</option>' if mode=='slice' else ''.join('<option value="'+str(i)+'">'+html.escape(s)+'</option>' for i,s in enumerate(['A (x) B (y) C','We (quietly) left','(maybe) We can go','We left (quietly)','(aside)']))
    fields='<div class="lab-fields">'+''.join('<div><label for="lab-'+k+'">'+k.capitalize()+'</label><input id="lab-'+k+'" inputmode="numeric" value="'+v+'" aria-describedby="lab-help"></div>' for k,v in [('start','1'),('stop','4'),('step','1')])+'</div>' if mode=='slice' else '<label><input id="lab-clean" type="checkbox">Clean only the join: trim its edges and separate nonempty pieces with one space</label>'
    helper='Leave a slice field blank to omit it. Blank step means 1. Write your predicted Python value, or write empty or error.' if mode=='slice' else 'Preview one pair at a time. Compare a direct join with a cleaned join. This lab shows separate matched pairs; it does not run your function.'
    lab='<section class="sequence-lab" data-sequence-lab="'+mode+'" aria-labelledby="lab-title"><h2 id="lab-title">Practice lab: predict, then check</h2><p id="lab-help">'+helper+'</p><label for="lab-example">Practice example</label><select id="lab-example">'+options+'</select><p>Current sequence:</p><p id="lab-original"></p><ol id="lab-positions" aria-label="Items and their indices"></ol><form id="lab-form">'+fields+'<label for="lab-prediction">Your predicted result</label><input id="lab-prediction" maxlength="200" autocomplete="off" aria-describedby="lab-help"><div class="lab-actions"><button type="submit" class="btn-uga">Check prediction</button>'+('<button type="button" class="btn-uga" id="lab-apply" disabled>Apply this edit</button>' if mode=='edit' else '')+'<button type="button" class="btn-uga" id="lab-reset">Reset lab</button></div></form><p id="lab-status" role="status" aria-live="polite"></p><p id="lab-result"></p><p><a href="index.html">All Part III activities</a></p></section>'
    p=OUT/(stem+'.html');s=p.read_text().replace('</main>',lab+'</main>',1);s='<link rel="stylesheet" href="sequence-lab.css"></head>'.join(s.rsplit('</head>',1));s='<script src="sequence-lab.js" defer></script></body>'.join(s.rsplit('</body>',1));p.write_text('\n'.join(line.rstrip() for line in s.splitlines()) + '\n')
