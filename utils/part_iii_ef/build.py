import copy
import html
import json
import re
import uuid
import zipfile
import sys
from pathlib import Path
from urllib.parse import urlencode

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from part_iii_scaffolding import revise_content

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
    revise_content(stem, content)
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
    table_style = ''
    if stem in ('III_G_Q2_Exclusive_Set_Items', 'III_J_Q1_Add_Counters'):
        table_style = '.h5p-advanced-text table{width:100%;max-width:48rem;margin:1rem 0;border-collapse:collapse}.h5p-advanced-text table caption{caption-side:top;text-align:left;font-weight:700;color:#333;padding:0 0 .5rem}.h5p-advanced-text table th,.h5p-advanced-text table td{border:1px solid #c9c9c9;padding:.55rem .8rem;text-align:left;vertical-align:top;overflow-wrap:normal;word-break:normal}.h5p-advanced-text table thead th{background:#f4e9ec}.h5p-advanced-text table tbody tr:nth-child(even){background:#faf7f8}@media(max-width:520px){.h5p-advanced-text table th,.h5p-advanced-text table td{padding:.35rem .4rem}.h5p-interactive-book-status{flex-wrap:wrap!important;height:auto!important;overflow:visible!important}.h5p-interactive-book-status-chapter{order:10!important;flex:0 0 100%!important;width:100%!important;padding:.35rem .75rem!important}}'
    page = page.replace('</head>', '<meta charset="UTF-8"><style>a:focus,a:focus-visible,button:focus,button:focus-visible,[tabindex]:focus,[tabindex]:focus-visible{outline:3px solid #0055a4!important;outline-offset:3px!important}.h5p-advanced-text a:focus,.h5p-advanced-text a:focus-visible{background:#eaf2ff!important;box-shadow:0 0 0 4px #0055a4!important;border-radius:2px}.h5p-advanced-text{line-height:1.6}.h5p-alternative-inner p{font-weight:400!important;font-size:1rem!important}code{overflow-wrap:anywhere}' + table_style + '</style></head>')
    from urllib.parse import quote
    live = 'https://uga-ling2200.github.io/applets/part_III/' + stem + '.html'
    page = re.sub(r'(&amp;source-url=)[^"\s]*', lambda match: match[1] + quote(live, safe=''), page)
    page = re.sub(r'[ \t]+(?=\n)', '', page)
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
G = [
chapter('1. Describe the target',
 text('Start with examples', '<p>III.G Q2 · Sets</p><h3>Notebook task</h3><ul><li>Write <code>xor(first, second)</code>.</li><li>Accept two sets and return a set of the items that are in one set or the other, but not both.</li></ul><h3>Learning goals</h3><ul><li><strong>Classify</strong> items by membership in two sets.</li><li><strong>Compare</strong> familiar set operations with the target result.</li><li><strong>Test</strong> a rule on varied input pairs before coding.</li></ul>' + PARTNER + '<p>On paper, start with <code>first = {"a", "b", "c"}</code> and <code>second = {"b", "d"}</code>. List the candidate items, then predict the returned set. Focus on which items are present, not on the order in which Python might display them.</p>'),
 q('Check the predicted members', '<p>Start with the two sets from your paper prediction: <code>first = {"a", "b", "c"}</code> and <code>second = {"b", "d"}</code>. Which set contains exactly the items that <code>xor(first, second)</code> should return?</p>',
   ('<code>{"a", "c", "d"}</code>', 'Yes. Each of these items occurs in exactly one input; b occurs in both.'),
   ('<code>{"a", "b", "c", "d"}</code>', 'This includes b, which occurs in both inputs. Recheck the last part of the task rule.'),
   ('<code>{"b"}</code>', 'This keeps only the shared item. The task asks for items in one input but not both.')),
 q('Decide what a set answer means', '<p>After predicting the result members, decide how to check that prediction. If Python displays the same result set in a different order, which statement is correct?</p>',
   ('The result can still be correct if it has the same members.', 'Correct. Set equality depends on membership, not display order.'),
   ('The result is wrong unless its display order matches the first input.', 'A set does not preserve the first input as an answer order. Compare members instead.'),
   ('The result must always be sorted alphabetically.', 'Sets do not promise an alphabetical display order.'))),
chapter('2. Mark membership',
 text('Use one row per candidate', '<p>Keep the same two sets from page 1. Copy this table and fill the two membership columns before deciding whether each candidate belongs in the returned set. Include <code>"e"</code> to test a value that occurs in neither input.</p><table><caption>Candidate membership to predict</caption><thead><tr><th scope="col">Item</th><th scope="col">In first?</th><th scope="col">In second?</th><th scope="col">In result?</th></tr></thead><tbody><tr><th scope="row">a</th><td>?</td><td>?</td><td>?</td></tr><tr><th scope="row">b</th><td>?</td><td>?</td><td>?</td></tr><tr><th scope="row">c</th><td>?</td><td>?</td><td>?</td></tr><tr><th scope="row">d</th><td>?</td><td>?</td><td>?</td></tr><tr><th scope="row">e</th><td>?</td><td>?</td><td>?</td></tr></tbody></table><p>Compare your rows with your partner. Explain each result decision using both membership columns.</p>'),
 q('A member of both inputs', '<p>You predicted the whole result; now check one row of the membership table. For <code>first = {"a", "b", "c"}</code> and <code>second = {"b", "d"}</code>, what should happen to <code>"b"</code> in the returned set?</p>',
   ('Leave it out because it occurs in both inputs.', 'Yes. The word “both” in the task excludes this item.'),
   ('Include it because it occurs in at least one input.', 'That rule describes union. Check whether b occurs in both.'),
   ('Include it twice, once for each input.', 'A set cannot contain two copies of the same item. The task excludes shared items.')),
 q('A member of neither input', '<p>After checking an item found in both inputs, test the other boundary of the rule. The string <code>"e"</code> appears in neither input set. What should happen to it in the returned set?</p>',
   ('Leave it out because it occurs in neither input.', 'Correct. An output member must come from one of the input sets.'),
   ('Include it because it does not occur in both inputs.', '“Not both” alone is not enough: the item must occur in one input.'),
   ('Include it as an empty placeholder.', 'Sets contain actual items. There is no placeholder item for a value that never appeared.'))),
chapter('3. Order the set operations',
 text('Fill in a flowchart', '<p>Return to <code>first = {"a", "b", "c"}</code> and <code>second = {"b", "d"}</code>. Copy this flowchart onto paper. Fill each operation blank with <em>union</em>, <em>intersection</em>, or <em>difference</em>. Both branches begin with the original input sets.</p><table><caption>Two branches followed by one final step</caption><thead><tr><th scope="col">Branch A: all candidate items</th><th scope="col">Branch B: shared items</th></tr></thead><tbody><tr><td><code>first</code> and <code>second</code><br>↓<br>Operation: ____<br>↓<br>Call the result <code>A</code></td><td><code>first</code> and <code>second</code><br>↓<br>Operation: ____<br>↓<br>Call the result <code>B</code></td></tr><tr><td colspan="2">↓ Use the two branch results in this order: ____ then ____<br>Final operation: ____<br>Remove the shared items from the broader collection.</td></tr></tbody></table><p>Predict the members of <code>A</code>, <code>B</code>, and the final result before using Check. The final step must happen after both branches, so the inputs to that step are the two intermediate sets.</p>'),
 q('Choose the operation for all candidates', '<p>The membership table covered every candidate item; branch <code>A</code> needs to collect them before any are excluded. For <code>first = {"a", "b", "c"}</code> and <code>second = {"b", "d"}</code>, which operation puts <code>{"a", "b", "c", "d"}</code> in branch <code>A</code>, including the item shared by both inputs?</p>',
   ('Union', 'Union collects every item found in either input. Now decide which operation isolates the shared items.'),
   ('Intersection', 'Intersection keeps only items found in both inputs. Branch A needs all candidates.'),
   ('Difference', 'Difference removes items from one set. Branch A must still include every candidate.')),
 q('Choose the operation for shared items', '<p>Branch <code>A</code> gathers candidates; branch <code>B</code> must identify what to remove. For <code>first = {"a", "b", "c"}</code> and <code>second = {"b", "d"}</code>, which operation puts only the shared item <code>{"b"}</code> in branch <code>B</code>?</p>',
   ('Intersection', 'Intersection keeps the item shared by both inputs. Compare this smaller set with branch A.'),
   ('Union', 'Union includes every item from either input, not just the shared item.'),
   ('Difference', 'Difference removes members of one set from another; it does not isolate the shared item here.')),
 q('Order the final step', '<p>Now combine the two branches you just examined. Let <code>A</code> contain all candidates and <code>B</code> contain the shared items. Which expression removes the shared items while retaining items unique to either input?</p>',
   ('<code>A.difference(B)</code>', 'Yes. Start with all candidates in A, then remove the shared members in B.'),
   ('<code>B.difference(A)</code>', 'Every shared item in B is also in A, so this removes everything. Check which collection should be larger.'),
   ('<code>first.difference(second)</code>', 'This finds items unique to first, but misses items unique to second. The flowchart begins with both inputs.'))),
chapter('4. Test other relationships',
 text('Look for cases your first example missed', '<p>Now predict three pairs before checking: identical sets, disjoint sets, and a pair where one set is empty. Use the original rule for each item rather than assuming the first example covers every case.</p><p>If no items qualify, write the Python value for an empty <em>set</em>. Compare that value with an empty dictionary or list.</p>'),
 q('Compare identical inputs', '<p>Now test the flowchart when every input item is shared. What set should <code>xor({1, 2}, {1, 2})</code> return?</p>',
   ('<code>set()</code>', 'Every item occurs in both inputs, so no item qualifies.'),
   ('<code>{1, 2}</code>', 'Each item is shared. The task excludes items in both.'),
   ('<code>[1, 1, 2, 2]</code>', 'This is a list with repeated values, not a set. Shared items do not qualify.')),
 q('Compare an empty input', '<p>After testing identical sets, change the relationship: one input has no items at all. What set should <code>xor({1, 2}, set())</code> return?</p>',
   ('<code>{1, 2}</code>', 'Each item occurs in the first set and not the empty second set.'),
   ('<code>set()</code>', 'The second set is empty, but the first has items that occur in exactly one input.'),
   ('<code>{}</code>', 'That expression creates an empty dictionary, not the required result set.')),
 q('Compare disjoint inputs', '<p>The empty-input case still had items in only one set. Now both inputs have items, but none are shared. What set should <code>xor({1, 2}, {3, 4})</code> return?</p>',
   ('<code>{1, 2, 3, 4}</code>', 'Every item occurs in exactly one input. Here the result happens to match the union.'),
   ('<code>set()</code>', 'There are no shared items to exclude; each input still contributes its members.'),
   ('<code>{}</code>', 'This is an empty dictionary, not the required result set.'))),
chapter('5. Explain, implement, test',
 text('Return to III.G Q2', '<p>Explain your rule to your partner before writing code. For any candidate item, what facts about the two input sets do you need? How will you prevent a shared item from entering the result? Then write your own <code>xor(first, second)</code> function in the course notebook.</p><h3>Make a test table</h3><ul><li>Overlapping inputs: <code>{1, 2}</code> and <code>{2, 3}</code>.</li><li>Identical inputs: <code>{1, 2}</code> and <code>{1, 2}</code>.</li><li>Disjoint inputs: <code>{1}</code> and <code>{2}</code>.</li><li>One or both inputs empty: use <code>set()</code>.</li></ul><p>Predict each returned set before running the function. Explain any mismatch by referring to membership, not display order. Check that your function returns a set.</p>'),
 q('Diagnose a test result', '<p>You have predicted outputs for several input relationships; use one overlap case to diagnose a possible coding mistake. For inputs <code>{1, 2}</code> and <code>{2, 3}</code>, which returned set would show that a function kept every item from either input, including the shared item?</p>',
   ('<code>{1, 2, 3}</code>', 'This is the union; the shared item 2 has not been excluded.'),
   ('<code>{1, 3}</code>', 'This contains only items in exactly one input, so it does not show that mistake.'),
   ('<code>{2}</code>', 'This keeps only the shared item, which is a different mistake.')),
 q('Check a set result', '<p>After diagnosing a possible mistake, choose a check for the intended result. For <code>first = {1, 2}</code> and <code>second = {2, 3}</code>, the expected result contains <code>1</code> and <code>3</code>, but not the shared item <code>2</code>. Which Python check verifies exactly those <em>set members</em> without relying on display order?</p>',
   ('<code>result == {1, 3}</code>', 'Set equality compares members without requiring a display order.'),
   ('<code>list(result) == [1, 3]</code>', 'Converting to a list introduces an order that the set does not promise.'),
   ('<code>result[0] == 1</code>', 'Sets do not support indexing by position.')))
]

J = [
chapter('1. Predict a combined count',
 text('Begin with the notebook task', '<p>III.J Q1 · Dictionaries</p><h3>Notebook task</h3><ul><li>Write <code>add_counters(counter1, counter2)</code> for two dictionaries whose values are counts.</li><li>Return a <strong>new dictionary</strong> containing every key found in either input.</li><li>For each key, the returned count is the sum of its counts in the two inputs.</li></ul><h3>Learning goals</h3><ul><li><strong>Predict</strong> combined counts for shared and unshared keys.</li><li><strong>Explain</strong> how a missing key contributes to a sum.</li><li><strong>Plan and test</strong> a loop that builds a new dictionary.</li></ul>' + PARTNER + '<p>On paper, compare <code>counter1 = {"a": 2, "b": 1, "c": 3}</code> and <code>counter2 = {"a": 1, "b": 2, "d": 3}</code>. First predict the count for <code>"a"</code>, then list the keys that the result needs. Keep the two input dictionaries separate on your page.</p>'),
 q('Predict one value', '<p>For the two dictionaries above, what value should the returned dictionary store under <code>"a"</code>?</p>',
   ('<code>3</code>', 'Yes. The two inputs contribute 2 and 1 for the same key.'),
   ('<code>2</code>', 'That reads only the first dictionary. The result combines both counts.'),
   ('<code>1</code>', 'That reads only the second dictionary. Check the first input too.')),
 q('List the result keys', '<p>Now look beyond the shared key. Which keys must appear in the new dictionary?</p>',
   ('<code>"a", "b", "c", "d"</code>', 'Each key found in either input appears once in the result.'),
   ('<code>"a", "b"</code>', 'Those are only the shared keys. The task also keeps keys found in just one input.'),
   ('<code>"c", "d"</code>', 'Those are only the unshared keys. Shared keys also need summed counts.'))),
chapter('2. Account for missing keys',
 text('Make one row per key', '<p>Use the same dictionaries from page 1. Copy the table and fill each question mark before choosing an answer. Write <em>missing</em> when a key has no entry in that input; do not assume the missing entry is stored as a zero.</p><table><caption>Counts to combine from the two inputs</caption><thead><tr><th scope="col">Key</th><th scope="col"><code>counter1</code></th><th scope="col"><code>counter2</code></th><th scope="col">Result</th></tr></thead><tbody><tr><th scope="row"><code>"a"</code></th><td>2</td><td>1</td><td>?</td></tr><tr><th scope="row"><code>"b"</code></th><td>1</td><td>2</td><td>?</td></tr><tr><th scope="row"><code>"c"</code></th><td>3</td><td>missing</td><td>?</td></tr><tr><th scope="row"><code>"d"</code></th><td>missing</td><td>3</td><td>?</td></tr></tbody></table><p>Discuss how a missing count should affect addition while keeping the key in the result.</p>'),
 q('Combine a key found once', '<p><code>"c"</code> occurs only in <code>counter1</code>, with count 3. What count belongs under <code>"c"</code> in the result?</p>',
   ('<code>3</code>', 'Correct. The missing contribution from the other dictionary adds nothing.'),
   ('No <code>"c"</code> entry', 'The result needs every key from either input, including c.'),
   ('An error because <code>"c"</code> is missing from <code>counter2</code>', 'The function must handle a key that occurs in only one input. Plan a safe lookup for that case.')),
 q('Separate missing from stored zero', '<p>Suppose <code>counter1 = {"x": 0}</code> and <code>counter2 = {}</code>. Which statement describes the inputs accurately?</p>',
   ('<code>"x"</code> is present in the first dictionary with value 0.', 'Yes. A stored zero and an absent key are different states, even though each contributes zero to the sum.'),
   ('<code>"x"</code> is missing from both dictionaries.', 'The first dictionary explicitly stores x with value 0.'),
   ('<code>"x"</code> should be left out because its count is zero.', 'The task includes every key found in either input, even when its stored count is zero.'))),
chapter('3. Read a count safely',
 text('Try a default for a missing key', '<p>A direct lookup such as <code>counter2["c"]</code> fails when <code>"c"</code> is absent. A dictionary also has <code>get(key, default)</code>: it returns the stored value when the key exists, and the supplied default when it does not. For this activity, consider <code>missing_count = 0</code>. Predict each expression below before checking. This is one possible lookup tool, not a required complete solution.</p>'),
 q('Read an absent key', '<p>With <code>counter2 = {"a": 1, "b": 2, "d": 3}</code> and <code>missing_count = 0</code>, what does <code>counter2.get("c", missing_count)</code> return?</p>',
   ('<code>0</code>', 'Yes. c is absent, so get returns the value supplied by missing_count.'),
   ('<code>3</code>', 'That is the value of d. get looks for the specific key c.'),
   ('A <code>KeyError</code>', 'A direct square-bracket lookup would fail here; get uses its default for an absent key.')),
 q('Read a stored value', '<p>With the same dictionary, what does <code>counter2.get("a", missing_count)</code> return?</p>',
   ('<code>1</code>', 'Yes. An existing key returns its stored count; the default is not used.'),
   ('<code>0</code>', 'The default applies only when the requested key is absent.'),
   ('<code>None</code>', 'A value is stored under a, so get returns that value.')),
 q('Check for a side effect', '<p>After evaluating <code>counter2.get("c", missing_count)</code>, what happens to <code>counter2</code>?</p>',
   ('It stays unchanged.', 'Correct. get reads a value or returns the default; it does not insert c.'),
   ('It gains <code>"c": 0</code>.', 'get does not add the missing key to the dictionary.'),
   ('It loses one of its existing keys.', 'A lookup does not remove entries.'))),
chapter('4. Plan the new dictionary',
 text('Choose keys, then fill values', '<p>Make a short plan on paper. First choose which keys the loop must visit so no input key is missed. Then decide where each combined count will be stored. You may use <code>get</code> or another safe lookup plan. Keep the inputs unchanged and build a separate result dictionary.</p><p>Use this unfinished outline to mark the two decisions, without filling them in yet:</p><pre><code>result = {}\nmissing_count = 0\nfor key in ______:\n    result[key] = ______</code></pre><p>Trace your plan with <code>counter1 = {"a": 2, "c": 3}</code> and <code>counter2 = {"a": 1, "d": 3}</code>. Show the result after visiting each key. Your plan should not depend on a particular dictionary display order.</p>'),
 q('Choose a complete set of keys', '<p>Which loop plan can visit every key needed by the result, including <code>"d"</code> in the second input?</p>',
   ('Visit the keys found in either input.', 'Yes. You can form that collection or process both inputs without skipping repeated keys.'),
   ('Visit only the keys in <code>counter1</code>.', 'That misses d, which occurs only in counter2.'),
   ('Visit only keys that both inputs share.', 'That misses c and d, which must also be in the result.')),
 q('Place the combined count', '<p>When your loop reaches a key, which action matches the requirement to return a new dictionary?</p>',
   ('Store the combined count for that key in a separate result dictionary.', 'Correct. The result holds one combined value per key; the inputs remain as they were.'),
   ('Replace the count in <code>counter1</code>.', 'That changes an input rather than building the required new dictionary.'),
   ('Print the combined count without storing it.', 'Printing does not construct or return the requested dictionary.')),
 q('Trace an unshared key', '<p>In the page 4 trace, <code>"d"</code> appears only in <code>counter2</code> with count 3. What should your plan place in the result under <code>"d"</code>?</p>',
   ('<code>3</code>', 'Yes. The absent first count contributes zero; d is still a result key.'),
   ('<code>0</code>', 'Zero is the missing contribution from counter1, not the entire combined count.'),
   ('No entry for <code>"d"</code>', 'The loop must include keys found in either dictionary.'))),
chapter('5. Implement and test',
 text('Return to III.J Q1', '<p>Explain your key plan and safe count lookup to your partner. Then write your own <code>add_counters(counter1, counter2)</code> function in the course notebook. Return the new dictionary; printing it alone does not meet the task.</p><h3>Make a test table</h3><ul><li>The notebook example: <code>{"a": 2, "b": 1, "c": 3}</code> and <code>{"a": 1, "b": 2, "d": 3}</code>.</li><li>Shared keys with different counts: <code>{"x": 2}</code> and <code>{"x": 5}</code>.</li><li>A stored zero: <code>{"x": 0}</code> and <code>{}</code>.</li><li>One empty input and then two empty inputs.</li></ul><p>Predict each dictionary before running your function. Afterwards, compare the returned value with the prediction and check that neither input changed. For a nonempty input, check that the returned dictionary is a separate object.</p><h3>Discuss</h3><ol><li>Why can looping over only one input miss a result key?</li><li>How do you distinguish a missing key from a key with a stored zero?</li><li>What evidence shows that your function returned a new dictionary?</li></ol>'),
 q('Check empty inputs', '<p>What should <code>add_counters({}, {})</code> return?</p>',
   ('<code>{}</code>', 'Yes. There are no keys in either input, so the new result dictionary is empty.'),
   ('<code>0</code>', 'The function returns a dictionary, even when it contains no keys.'),
   ('<code>None</code>', 'The task requires a returned dictionary rather than no return value.')),
 q('Check the complete contract', '<p>Suppose <code>counter1 = {"x": 2}</code> and <code>counter2 = {"x": 5}</code>. Which observation best supports that your function met the task?</p>',
   ('It returns a separate <code>{"x": 7}</code> dictionary and leaves both inputs unchanged.', 'That checks the sum, the returned dictionary, and the new-object requirement.'),
   ('It changes <code>counter1</code> to <code>{"x": 7}</code> and returns it.', 'The count is right, but the first input was changed instead of producing a new dictionary.'),
   ('It prints <code>{"x": 7}</code> and returns <code>None</code>.', 'Printing shows a value on screen but does not return the required dictionary.')))
]

only = sys.argv[sys.argv.index('--only') + 1] if '--only' in sys.argv else None
for stem,title,chapters,file,week in [('III_E_Q1_Reversing_Sequences','III.E Slicing, Q1 — Reversing Sequences',E,'III.E_Slicing.ipynb','week08'),('III_F_Q4_Removing_Parentheticals','III.F Strings, Q4 — Removing Parentheticals',F,'III.F_Strings_III.ipynb','week08'),('III_G_Q2_Exclusive_Set_Items','III.G Sets, Q2 — Items in Exactly One Set',G,'III.G_Sets.ipynb','week08'),('III_J_Q1_Add_Counters','III.J Dictionaries, Q1 — Add Counters',J,'III.J_Data_types_III.ipynb','week10')]:
    if only and stem != only:
        continue
    source='https://github.com/uga-ling2200/prep/blob/master/classnotes/'+week+'/'+file
    if stem not in ('III_G_Q2_Exclusive_Set_Items', 'III_J_Q1_Add_Counters'):
        chapters[-1]['params']['content'][0]['content']['params']['text']+='<p><a href="'+source+'" target="_blank" rel="noopener noreferrer">Open the original course notebook (new tab)</a></p>'
    print(stem,build(stem,title,chapters,source))

for stem,mode in [('III_E_Q1_Reversing_Sequences','slice'),('III_F_Q4_Removing_Parentheticals','edit')]:
    if only and stem != only:
        continue
    options='<option value="word">String: plant</option><option value="tuple">Tuple of numbers</option><option value="list">List of colors</option><option value="empty">Empty list</option><option value="single">One-item tuple</option>' if mode=='slice' else ''.join('<option value="'+str(i)+'">'+html.escape(s)+'</option>' for i,s in enumerate(['A (x) B (y) C','We (quietly) left','(maybe) We can go','We left (quietly)','(aside)']))
    fields='<div class="lab-fields">'+''.join('<div><label for="lab-'+k+'">'+k.capitalize()+'</label><input id="lab-'+k+'" inputmode="numeric" value="'+v+'" aria-describedby="lab-help"></div>' for k,v in [('start','1'),('stop','4'),('step','1')])+'</div>' if mode=='slice' else '<label><input id="lab-clean" type="checkbox">Clean only the join: trim its edges and separate nonempty pieces with one space</label>'
    helper='Leave a slice field blank to omit it. Blank step means 1. Write your predicted Python value, or write empty or error.' if mode=='slice' else 'Preview one pair at a time. Compare a direct join with a cleaned join. This lab shows separate matched pairs; it does not run your function.'
    lab='<section class="sequence-lab" data-sequence-lab="'+mode+'" aria-labelledby="lab-title"><h2 id="lab-title">Practice lab: predict, then check</h2><p id="lab-help">'+helper+'</p><label for="lab-example">Practice example</label><select id="lab-example">'+options+'</select><p>Current sequence:</p><p id="lab-original"></p><ol id="lab-positions" aria-label="Items and their indices"></ol><form id="lab-form">'+fields+'<label for="lab-prediction">Your predicted result</label><input id="lab-prediction" maxlength="200" autocomplete="off" aria-describedby="lab-help"><div class="lab-actions"><button type="submit" class="btn-uga">Check prediction</button>'+('<button type="button" class="btn-uga" id="lab-apply" disabled>Apply this edit</button>' if mode=='edit' else '')+'<button type="button" class="btn-uga" id="lab-reset">Reset lab</button></div></form><p id="lab-status" role="status" aria-live="polite"></p><p id="lab-result"></p><p><a href="index.html">All Part III activities</a></p></section>'
    p=OUT/(stem+'.html');s=p.read_text().replace('</main>',lab+'</main>',1);s='<link rel="stylesheet" href="sequence-lab.css"></head>'.join(s.rsplit('</head>',1));s='<script src="sequence-lab.js" defer></script></body>'.join(s.rsplit('</body>',1));p.write_text('\n'.join(line.rstrip() for line in s.splitlines()) + '\n')
