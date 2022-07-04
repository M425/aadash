
import json
import re

def parse(jobstdout):
    count = 0
    
    state = 'HEADER'
    last_output = ''
    
    parsed = []
    current_task = {
        'row': 0,
        'role': '',
        'name': 'init',
        'hosts': {},
        'sect': 'init',
        'new_sect': True,
    }
    parsed.append(current_task)
    playrecap = {}
    host = ''
    for line in jobstdout.split('\n'):
        count += 1
        line = line.strip()
        # print(f'{count} -> state "{state}" -- line: "{line}" -- lastout "{last_output}" -- lenparsed {len(parsed)}')
    
        if line == '':
            last_output = 'skip.blank'
            continue
    
        rgx = r'^(TASK|RUNNING HANDLER).*'
        if re.search(rgx, line):
            # READING NEW TASK
            state = 'TASK'
            all_skipping = True
            if 'hosts' in current_task:
                for h in current_task['hosts']:
                    all_skipping = all_skipping and current_task['hosts'][h]['status'] == 'skipping'
            current_task['all_skipping'] = all_skipping
            old_task = current_task
            current_task = {
                'row': count,
                'role': '',
                'name': '',
                'hosts': {},
                'sect': '',
                'new_sect': False
            }
            parsed.append(current_task)
            rgx_role = re.search(r'^TASK \[([a-zA-Z_]+\.[a-zA-Z_]+\.[a-zA-Z_]+)\s:\s(.*)\].*', line)
            rgx_sect = re.search(r'^TASK \[\(([a-zA-Z0-9_\-\s]+)\)\].*', line)
            rgx_task = re.search(r'^TASK \[(.*)\].*', line)
            if rgx_role:
                current_task['role'] = rgx_role.group(1)
                current_task['name'] = rgx_role.group(2)
                current_task['sect'] = old_task['sect']
                last_output = 'task.role'
            elif rgx_sect:
                current_task['role'] = ''
                current_task['sect'] = rgx_sect.group(1)
                current_task['name'] = ''
                current_task['new_sect'] = current_task['sect'] != old_task['sect']
                if current_task['new_sect']:
                    current_task = {
                        'role': '',
                        'name': current_task['name'],
                        'hosts': {},
                        'sect': current_task['sect'],
                        'new_sect': False
                    }
                    parsed.append(current_task)
                last_output = 'task.sect'
            elif rgx_task:
                current_task['role'] = ''
                current_task['sect'] = old_task['sect']
                current_task['name'] = rgx_task.group(1)
                last_output = 'task.std'
            continue
    
        rgx = r'^(ok:|changed:|skipping:|fatal:) \[([a-zA-Z0-9]+)(\]| -> ).*'
        if re.search(rgx, line):
            result = re.search(rgx, line).group(1)
            # READING NEW RES
            state = 'RES'
            host = re.search(rgx, line).group(2)
            map_status = {  # skipping < ok < changed < failed
                'skipping': 1,
                'ok': 2,
                'changed': 3,
                'failed': 4
            }
            if host not in current_task['hosts']:
                current_task['hosts'][host] = {'res': [], 'status': 'skipping'}
            current_res = {
                'status': result[:-1],
                'out': ''
            }
            current_task['hosts'][host]['res'].append(current_res)
            if map_status[current_task['hosts'][host]['status']] < map_status[current_res['status']]:
                current_task['hosts'][host]['status'] = current_res['status']
            current_res['out'] += line
            last_output = 'task.result'
            continue
    
        rgx = r'^included:.*'
        if re.search(rgx, line):
            state = 'BODY'
            current_task['included'] = line[:-1]
            last_output = 'task.included'
            continue
    
        rgx = r'^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday).*'
        if re.search(rgx, line):
            last_output = 'skip.date'
            continue
    
        rgx = r'^(NO\sMORE\sHOSTS\sLEFT).*'
        if re.search(rgx, line):
            continue
    
        rgx = r'^(PLAY RECAP).*'
        if re.search(rgx, line):
            state = 'PLAYRECAP'
            continue
    
        rgx = r'^(PLAY).*'
        if re.search(rgx, line):
            state = 'PLAY'
            continue

        rgx = r'^(\[WARNING\]).*'
        if re.search(rgx, line):
            continue
    
        if state == 'HEADER':
            continue
    
        if state == 'RES':
            current_task['hosts'][host]['res'][-1]['out'] += line
            continue
    
        if state == 'PLAYRECAP':
            rgx = r'^=+.*'
            if re.search(rgx, line):
                state = 'FINISH'
                continue
    
            rgx = r'^([a-zA-Z0-9]+) *: ok=([0-9]+) *changed=([0-9]+) *unreachable=([0-9]+) *failed=([0-9]+) *skipped=([0-9]+) *rescued=([0-9]+) *ignored=([0-9]+)'
    
            host = re.search(rgx, line).group(1)
            playrecap[host] = {}
            playrecap[host]['ok'] = re.search(rgx, line).group(2)
            playrecap[host]['changed'] = re.search(rgx, line).group(3)
            playrecap[host]['unreachable'] = re.search(rgx, line).group(4)
            playrecap[host]['failed'] = re.search(rgx, line).group(5)
            playrecap[host]['skipped'] = re.search(rgx, line).group(6)
            playrecap[host]['rescued'] = re.search(rgx, line).group(7)
            playrecap[host]['ignored'] = re.search(rgx, line).group(8)
            continue
    
        if state == 'FINISH':
            continue
        print(line)
        raise Exception(line)
    
    allhosts = set()
    for p in parsed:
        allhosts = allhosts.union(set(p['hosts'].keys()))
    head_sect = None
    sections = []
    for p in parsed:
        if p['new_sect']:
            head_sect = p
            head_sect['hosts'] = {x: {'all_changed': False} for x in allhosts}
            sections.append(head_sect['sect'])
        else:
            for host in p['hosts']:
                if head_sect:
                    head_sect['hosts'][host]['all_changed'] = head_sect['hosts'][host]['all_changed'] or p['hosts'][host]['status'] == 'changed'
    
    result = {
        'parsed': parsed,
        'allhosts': list(allhosts),
        'playrecap': playrecap,
        'sections': sections
    }
    return result
    