"""Exercise real HTTP sessions, CSRF, persistence, permissions, and planner outputs."""
import urllib.request, urllib.error, http.cookiejar, json, uuid
import sys
from pathlib import Path
base='http://127.0.0.1:8080/api/v1'
jar=http.cookiejar.CookieJar(); client=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
def req(path,data=None,status=200,token=None):
    headers={'Content-Type':'application/json'}
    if token:headers['X-CSRF-TOKEN']=token
    request=urllib.request.Request(base+path, data=None if data is None else json.dumps(data).encode(),headers=headers)
    try:
        with client.open(request,timeout=45) as response:
            assert response.status==status,(path,response.status,status)
            return json.load(response)
    except urllib.error.HTTPError as e:
        body=e.read().decode();assert e.code==status,(path,e.code,status,body)
        return json.loads(body)
lessons=req('/lessons');problems=req('/problems');assert len(lessons)==33 and len(problems)==60
curriculum=req('/curriculum');assert curriculum['version']==1 and len(curriculum['concepts'])==24 and len(curriculum['questions'])==47
assert all('tests' not in p and 'reference' not in p for p in problems)
req('/progress',status=401)
token=req('/auth/session')['csrf']
req('/experiments',{'algorithm':'sliding-window','input':'2,1,5,1,3,2','target':3},status=403)
trace=req('/experiments',{'algorithm':'sliding-window','input':'2,1,5,1,3,2','target':3},token=token)
assert trace['result']['variables']['best']==9
req('/auth/register',{'name':'API Verification','email':'verification-'+uuid.uuid4().hex[:8]+'@example.test','password':'test-password-1on1'},token=token)
session=req('/auth/session');assert session['user']['name']=='API Verification';token=session['csrf']
req('/progress',{'completed':['lesson-sliding-window'],'resumeLesson':'lesson-sliding-window','resumeStep':2},token=token)
note=req('/notes',{'title':'Invariant','text':'The running sum equals the current window.','lesson':'lesson-sliding-window'},token=token)
progress=req('/progress');assert 'lesson-sliding-window' in progress['completed'];assert any(x['id']==note['id'] for x in progress['notes'])
plan=req('/plans',{'topics':['Arrays','Dynamic programming'],'perDay':2},token=token);assert not plan['uncovered'] and plan['selected']
req('/admin/content',status=403)
if not req('/system')['execution']:
    req('/submissions',{'problem':problems[0]['id'],'language':'java','code':'invalid','official':True},status=503,token=token)
assert not req('/progress')['solved']
for method in ['trie','set-cover','quickselect']:
    result=req('/evidence',{'method':method},token=token);assert len(result['rows'])==3
    if '--export' in sys.argv:
        output=Path(__file__).resolve().parents[1]/'docs/benchmarks';output.mkdir(parents=True,exist_ok=True)
        (output/(method+'.json')).write_text(json.dumps(result,indent=2),encoding='utf-8')
req('/auth/logout',{},token=token);req('/progress',status=401)
print('PASS: HTTP content, CSRF, registration, sessions, progress, notes, planning, permissions, unavailable-runner handling, three benchmarks, logout.')
