
import os

def parse_callsum(sumfile):
  summaries = {}
  lines = [l.strip('\n').split('\t') for l in open(sumfile,'rU')]
  #check if lines[0] exists
  if len(lines) > 0:
    header = lines[0]
    for l in lines[1:]:
      tmp = dict((h,l[header.index(h)]) for h in header[1:])
      if tmp['call'].startswith('Fixable'):
        p1,p2 = tmp['call'].split(':')[1].split(',')
        tmp['p1'] = p1
        tmp['p2'] = p2
        tmp['call'] = tmp['call'].split(':')[0]
      summaries[l[0]] = tmp
  return summaries

def load_calls(analysis):
  acalls = {}
  adir = os.path.join(analysis.attrib['location'],analysis.attrib['name'])
  for pool in analysis:
    pdir = os.path.join(adir, pool.attrib['name'])
    acalls[pool.attrib['name']] = {}
    for job in pool:
      jdir = os.path.join(pdir, job.attrib['name'])
      sumfile = os.path.join(jdir,"call_summary.txt")
      acalls[pool.attrib['name']][job.attrib['protocol']] = parse_callsum(sumfile)
  return acalls

def ff(v):
  return str(int(round(float(v))))

def fp(v):
  return str(round(float(v),1))
  

def call_display(d):
  call = d['call']
  if call == 'Pass': return {'call':'perfect','display':ff(d['mean_cov'])}
  elif call == 'Fixable': return {'call':'almost','display':ff(d['mean_cov']),'p1':d['p1'],'p2':d['p2']}
  elif call == 'Errors': return {'call':'errors','display':d['nvars']}
  elif call == 'Dips': return {'call':'dips','display':d['ndips']}
  elif call == 'Incomplete': return {'call':'incomplete','display':d['pct_cov']}
  elif call == 'Low coverage': return {'call':'lowcov','display':ff(d['mean_cov'])}
  else: return {'call':'?','display':ff(d['mean_cov'])}

def merge_calls(analysis, reflens, poollist, use_protocol="bwa_dir"):
  calltable = {} # dict((r[0],dict()) for r in reflens)
  acalls = load_calls(analysis)
  for ref,rlen in reflens:
    calltable[ref] = {}
    for pname in poollist:
      if use_protocol in acalls[pname]:
        calltable[ref][pname] = call_display(acalls[pname][use_protocol][ref])
      else: # use_protocol was not found
        if "bwa_dir" in acalls[pname]:
          calltable[ref][pname] = call_display(acalls[pname]["bwa_dir"][ref])

  return calltable

def best_calls(calltable):
  ret = []
  for ref,calls in calltable.iteritems():
    best = [(p,d['display']) for p,d in calls.iteritems() if d['call']=='perfect']
    if best:
      ret.append( (ref,sorted(best,key=lambda x:int(x[1]),reverse=True)[0][0]) )
    else:
      almost = [(p,d['display']) for p,d in calls.iteritems() if d['call']=='almost']
      if almost:
        ret.append( (ref,sorted(almost,key=lambda x:int(x[1]),reverse=True)[0][0]) )
      else:
        ret.append( (ref,None) )
  return dict(ret)
   
#for ref,rlen in refs:
#  tableline = '%s\t%s' % (ref, '\t'.join(calltable[ref][pname]['call'] for pname in poollist))
#  print tableline
  
