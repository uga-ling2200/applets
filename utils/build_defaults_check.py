from pathlib import Path
import re,json,copy,uuid,zipfile
root=Path(__file__).resolve().parents[1]
# Reuse the existing course H5P runtime and question behaviour, preserving licensed assets.
template=(root/'docs/part_III/III_G_Q2_Exclusive_Set_Items.html').read_text();a=template.index('H5PIntegration = ')+len('H5PIntegration = '); integ,n=json.JSONDecoder().raw_decode(template[a:]);entry=next(iter(integ['contents'].values()));book=json.loads(entry['jsonContent']);mc=book['chapters'][0]['params']['content'][1];col=book['chapters'][0]
questions=[
 ('Predict a second call','<p>Start with a newly defined function A from the comparison above. Run <code>remember("cat")</code>, then <code>remember("dog")</code>, omitting the set both times. What is in the set returned by the second call?</p>', [('Both cat and dog',True,'Both calls use the same default set; add changes that object.'),('Only dog',False,'That would require a fresh set. A’s default is created at definition time.'),('An empty set',False,'Both calls execute add on the shared set.')]),
 ('Identify the safe initialization','<p>In version B, why does the second omitted call start with an empty set?</p>', [('The is None branch creates a new set during each omitted call.',True,'Correct. None is the sentinel; set() runs inside each such call.'),('Python copies every default argument for each call.',False,'Python does not copy default arguments automatically.'),('None prevents the function from changing any set.',False,'The function still calls add. It changes a fresh set, or the set supplied by the caller.')]),
 ('Distinguish a set from a dictionary','<p>What would replacing <code>set()</code> with <code>{}</code> in version A’s signature do when the first call reaches <code>words_to_include.add(word)</code>?</p>', [('Raise AttributeError: a dictionary has no add method.',True,'{} creates a dict, not a set. An empty set is written set().'),('Fix the shared-default problem.',False,'{} is still a mutable default, and its type is dict.'),('Create a fresh empty set for every call.',False,'{} creates one dictionary at definition time.')]),
 ('Separate reading from mutation','<p>The IV.A Q2 reference filter only tests membership in <code>words_to_include</code>; it never changes that set. Does using a set default alone prove that repeated filter calls will accumulate words?</p>', [('No. The shared object must actually be changed for this mutation bug to appear.',True,'Correct. remember demonstrates mutation explicitly. Use None as the robust initialization pattern in the exercise.'),('Yes. Calling any function automatically adds its input words to the default set.',False,'Calling a function does not change a set unless the executed operations mutate it.')])]
code_a = '<p><code>def remember(word, words_to_include=set()):<br>&nbsp;&nbsp;&nbsp;&nbsp;words_to_include.add(word)<br>&nbsp;&nbsp;&nbsp;&nbsp;return words_to_include</code></p>'
code_b = '<p><code>def remember(word, words_to_include=None):<br>&nbsp;&nbsp;&nbsp;&nbsp;if words_to_include is None:<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;words_to_include = set()<br>&nbsp;&nbsp;&nbsp;&nbsp;words_to_include.add(word)<br>&nbsp;&nbsp;&nbsp;&nbsp;return words_to_include</code></p>'
chapters=[]
for title,question,answers in questions:
 chapter=copy.deepcopy(col);q=copy.deepcopy(mc);v=q['content'];v['subContentId']=str(uuid.uuid5(uuid.NAMESPACE_URL, 'ling2200/defaults/' + title));v['metadata']['title']=v['metadata']['extraTitle']=title;v['params']['question']=f'<h2>{title}</h2>'+question;v['params']['answers']=[{'text':'<p>'+t+'</p>','correct':ok,'tipsAndFeedback':{'tip':'','chosenFeedback':fb,'notChosenFeedback':''}} for t,ok,fb in answers];intro = (code_a if len(chapters) == 0 or len(chapters) == 2 else code_b if len(chapters) == 1 else '<p>Apply your explanation to the notebook. The reference membership test reads the set without modifying it.</p>')
 intro_item={'content': {'library':'H5P.AdvancedText 1.1','params':{'text':intro},'subContentId':str(uuid.uuid5(uuid.NAMESPACE_URL,'ling2200/defaults/intro/'+title)),'metadata':{'title':'Example to inspect','license':'U','authors':[],'changes':[]}},'useSeparator':'disabled'}
 chapter['params']['content']=[intro_item,q];chapter['subContentId']=str(uuid.uuid5(uuid.NAMESPACE_URL, 'ling2200/defaults/chapter/' + title));chapter['metadata']['title']=chapter['metadata']['extraTitle']=title;chapters.append(chapter)
book['chapters']=chapters;book['behaviour']['defaultTableOfContents']=False;book['bookCover']={'coverDescription':'<p>Mutable defaults: check your reasoning</p>'};entry['metadata']['title']='Mutable defaults: check your reasoning';entry['jsonContent']=json.dumps(book);entry['displayOptions']['frame']=False
new=template[:a]+json.dumps(integ)+template[a+n:];body=list(re.finditer(r'<body(?:\s[^>]*)?>',new))[-1]
assert body, 'actual body not found'
new=new[:body.start()]+'<body><main aria-label="Mutable defaults practice"><div class="h5p-content" data-content-id="4096308226"></div></main></body></html>'
new=new[:new.rfind('</head>')]+'<style>html.h5p-iframe,html.h5p-iframe body{min-height:0!important;height:auto!important;margin:0!important;padding:0!important}</style>'+new[new.rfind('</head>'):]
new=re.sub(r'<title>.*?</title>','<title>Mutable defaults: practice checks</title>',new,count=1)
(root/'docs/part_IV/defaults_check.html').write_text(new)

# Preserve all installed libraries, including editor dependencies, for Lumi authoring.
source=root/'docs/part_III/III_G_Q2_Exclusive_Set_Items.h5p'
with zipfile.ZipFile(source) as src, zipfile.ZipFile(root/'docs/part_IV/IV_A_Q2_Keyword_Arguments.h5p','w',zipfile.ZIP_DEFLATED) as dest:
 manifest=json.loads(src.read('h5p.json'))
 manifest['title']=manifest['extraTitle']='IV.A Functions IV, Q2: Mutable Defaults'
 for info in src.infolist():
  if info.filename=='h5p.json' or info.filename.startswith('content/'): continue
  dest.writestr(info,src.read(info.filename))
 dest.writestr('h5p.json',json.dumps(manifest))
 dest.writestr('content/content.json',json.dumps(book))
(root/'utils/defaults_content.json').write_text(json.dumps(book,indent=2))
