# demo to convert m to M in svg path

s='151.52288,577.5905 72.73098,-54.54824 68.69037,113.13709 -90.91373,72.73098 -111.116773,-20.20305 -12.121831,-80.81221 54.548234,8.08122 4.04061,-66.67006';
a=s.split(' ');
b=[it.split(',') for it in a];
c=[[float(it[0]),float(it[1])] for it in b];
d=[];
t=[0.,0.];
for it in c:
  t[0]=t[0]+it[0];
  t[1]=t[1]+it[1];
  d.append(t.copy());
e=[','.join([str(it[0]),str(it[1])]) for it in d];
f=' '.join(e);
print(f);
