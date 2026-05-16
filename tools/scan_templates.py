import os,re
issues=[]
for dirpath,dirnames,filenames in os.walk('templates'):
    for f in filenames:
        if not f.endswith('.html'): continue
        path=os.path.join(dirpath,f)
        with open(path,encoding='utf-8') as fh:
            s=fh.read()
        def cnt(p): return len(re.findall(re.escape(p),s))
        for_tags=cnt('{% for')
        endfor=cnt('{% endfor')
        if for_tags!=endfor:
            issues.append(f'UNMATCHED for/endfor in {path}: {for_tags} vs {endfor}')
        if_cnt=cnt('{% if')
        endif=cnt('{% endif')
        if if_cnt!=endif:
            issues.append(f'UNMATCHED if/endif in {path}: {if_cnt} vs {endif}')
        block=cnt('{% block')
        endblock=cnt('{% endblock')
        if block!=endblock:
            issues.append(f'UNMATCHED block/endblock in {path}: {block} vs {endblock}')
        raw_csrf=len(re.findall(r"csrf_token",s))
        has_csrf=cnt('{% csrf_token %}')
        if raw_csrf>0 and has_csrf==0:
            issues.append(f'stray csrf_token text in {path}')
        lbrace=s.count('{{')
        rbrace=s.count('}}')
        if lbrace!=rbrace:
            issues.append(f'unmatched braces in {path}: {{ count {lbrace} vs }} count {rbrace}')
        if re.search(r"\{%[^%]*$", s, re.M):
            issues.append(f'Possible unterminated {{% .. %}} in {path}')
        for i,line in enumerate(s.splitlines(),1):
            if 'csrf_token' in line and '{% csrf_token %}' not in line:
                issues.append(f'Line {i} in {path} contains "csrf_token" but not proper tag')

print('SCAN COMPLETE')
if issues:
    for it in issues:
        print(it)
else:
    print('No obvious template tag mismatches found.')
