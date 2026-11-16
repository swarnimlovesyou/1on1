"""Execute only trusted, repository-authored references on every fixture. Never a student runner."""
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
content = json.loads((ROOT / 'backend/src/main/resources/content.json').read_text(encoding='utf-8'))
results = []
cache = (ROOT / '.cache').resolve()
if not cache.is_relative_to(ROOT):
    raise RuntimeError('The temporary reference directory must stay inside the workspace.')
cache.mkdir(exist_ok=True)
compiler = shutil.which('g++')
compiler_env = os.environ.copy()
if compiler and os.name == 'nt':
    compiler_root = Path(compiler).parents[2]
    directories = [Path(compiler).parent, compiler_root / 'usr' / 'bin']
    compiler_env['PATH'] = os.pathsep.join(str(path) for path in directories if path.is_dir()) + os.pathsep + compiler_env.get('PATH', '')
if compiler:
    checked = subprocess.run([compiler, '--version'], capture_output=True, text=True, timeout=10, env=compiler_env)
    if checked.returncode:
        print(f'Optional local C++ compiler is unusable (exit {checked.returncode}); C++ remains unverified until Judge0 works.')
        compiler = None

def normalize(value):
    return re.sub(r'[ \t]+(?=\n|$)', '', value.replace('\r\n', '\n')).rstrip()

with tempfile.TemporaryDirectory(prefix='reference-check-', dir=cache) as directory:
    for problem in content['problems']:
        for language in ['python', 'cpp']:
            if language not in problem.get('references', {}):
                results.append(dict(problem=problem['id'], language=language, status='missing'))
                continue
            if language == 'cpp' and not compiler:
                results.append(dict(problem=problem['id'], language=language, status='not_verified', reason='No local C++ compiler; verify through Judge0.'))
                continue
            if language == 'python':
                command = [sys.executable, '-c', problem['references']['python']]
            else:
                source = Path(directory) / 'reference.cpp'
                executable = Path(directory) / ('reference.exe' if os.name == 'nt' else 'reference')
                source.write_text(problem['references']['cpp'], encoding='utf-8')
                compiled = subprocess.run([compiler, '-std=c++17', '-O2', str(source), '-o', str(executable)], capture_output=True, text=True, timeout=40, env=compiler_env)
                if compiled.returncode:
                    raise AssertionError(f'{problem["id"]}: C++ reference did not compile: {compiled.stderr[:1000]}')
                command = [str(executable)]
            for number, fixture in enumerate(problem['tests'], 1):
                ran = subprocess.run(command, input=fixture['input'], capture_output=True, text=True, timeout=5, env=compiler_env)
                if ran.returncode or normalize(ran.stdout) != normalize(fixture['output']):
                    raise AssertionError(f'{problem["id"]}/{language} fixture {number} failed: {ran.stderr[:500]}')
            results.append(dict(problem=problem['id'], language=language, status='passed', fixtures=len(problem['tests'])))
            print(f'{problem["id"]} / {language}: passed {len(problem["tests"])} fixtures')
(ROOT / '.cache/reference-verification.json').write_text(json.dumps(results, indent=2)+'\n', encoding='utf-8')
for language in ['python', 'cpp']:
    statuses = [r['status'] for r in results if r['language'] == language]
    print(f'{language}: ' + ', '.join(f'{statuses.count(s)} {s}' for s in sorted(set(statuses))))
print('Trusted reference checks complete. This does not verify Judge0 or student-code isolation.')
