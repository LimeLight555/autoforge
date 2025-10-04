AB='#00822b'
AA='#d85600'
A9='#9ACD32'
A8='#00BFFF'
A7='#FFD700'
A6='#DC143C'
A5='#800080'
A4='#FF8C00'
A3='#4682B4'
A2='#228B22'
A1='NOT_LAST'
A0='THIRD_LAST'
z='SECOND_LAST'
y='LAST'
x='SHRINK'
w='UPSET'
v='BEND'
u='PUNCH'
t='DRAW'
s=print
r=tuple
h='last'
g='middle'
f='first'
e='#FF4500'
d='HARD_HIT'
c='MEDIUM_HIT'
b='LIGHT_HIT'
V='HIT'
U=sum
T=sorted
I=range
H=int
G=len
F=enumerate
D=False
B=True
A=None
from time import sleep as J
from ctypes import Structure as AC,WinDLL as W,create_string_buffer as AD,sizeof,byref,pointer
from ctypes.wintypes import DWORD as K,LONG as O,WORD as i,RECT
from numpy import frombuffer as AE,uint8 as M,all,any,where as N,max,min,ceil,zeros,array as P
from cv2 import inRange,findNonZero as AF,dilate,connectedComponentsWithStats as j,CC_STAT_LEFT as k,CC_STAT_TOP as l
from pulp import LpProblem as AG,LpMinimize as AH,LpVariable as AI,LpInteger as AJ,lpSum as X,PULP_CBC_CMD as AK
AL='Hardrock TerraFirmaCraft 3 - 1.6.2 - //1.18.2//'
AM,Y=.025,{b:-3,c:-6,d:-9,t:-15,u:2,v:7,w:13,x:16}
L={'NONE':0,y:1,z:2,'NOT_THIRD_LAST':3,A0:4,'NOT_SECOND_LAST':5,A1:6,'ANY':7}
Q=list(Y.keys())
Z=[A2,A3,A4,A5,A6,A7,A8,A9,e]
AN=[(34,139,34),(70,130,180),(255,140,0),(128,0,128),(220,20,60),(255,215,0),(0,191,255),(154,205,50),(255,69,0)]
AO=[AA,AB]
AP=P([(216,86,0),(0,130,43)])
AQ={AA:{f:(127,0,0),g:(255,72,0),h:(0,61,0)},AB:{f:(0,0,51),g:(0,107,0),h:(0,92,20)}}
m={A2:u,A3:v,A4:w,A5:x,A6:b,A7:c,A8:d,A9:t,e:V}
n={B:A for(A,B)in m.items()}
AR,AS,AT,AU=(165,42,42),(58,122,254),(30,144,255),(255,218,185)
AV=[(139,69,19),(64,224,208)]
AW,AX,AY,AZ=90,88,67,220
R,S,a=A,A,B
C=W('user32')
E=W('gdi32')
Aa=W('shcore')
Ab=P([(137,2,2),(51,115,54)])
Ac=P([[0,1,0],[1,1,1],[0,1,0]],dtype=M)
class o(AC):_fields_=[('biSize',K),('biWidth',O),('biHeight',O),('biPlanes',i),('biBitCount',i),('biCompression',K),('biSizeImage',K),('biXPelsPerMeter',O),('biYPelsPerMeter',O),('biClrUsed',K),('biClrImportant',K)]
def Ad():
	global a
	while a:
		if C.GetAsyncKeyState(AW)&32768:q(B);J(.1)
		elif C.GetAsyncKeyState(AX)&32768:Ak();J(.1)
		elif C.GetAsyncKeyState(AY)&32768:q(D);J(.1)
		elif C.GetAsyncKeyState(AZ)&32768:a=D
		J(.1)
def Ae(x,y):C.SetCursorPos(H(x),H(y));J(AM);C.mouse_event(2,0,0,0,0);C.mouse_event(4,0,0,0,0)
def Af():Aa.SetProcessDpiAwareness(2);O=C.FindWindowW(A,AL);B=RECT();C.GetWindowRect(O,pointer(B));K,L,F,D=B.left,B.top,B.right-B.left,B.bottom-B.top;H=C.GetDC(0);I=E.CreateCompatibleDC(H);J=E.CreateCompatibleBitmap(H,F,D);E.SelectObject(I,J);E.BitBlt(I,0,0,F,D,H,K,L,1087111200);G=o();G.biSize,G.biWidth,G.biHeight,G.biPlanes,G.biBitCount=sizeof(o),F,-D,1,32;N=AD(F*D*4);E.GetDIBits(I,J,0,D,N,byref(G),0);E.DeleteObject(J);E.DeleteDC(I);C.ReleaseDC(0,H);return AE(N,dtype=M).reshape((D,F,4))[:,:,[2,1,0]],K,L,F,D
def Ag(img):C=img;A,B=N(all(C==AR,axis=-1));D,E=max(B)-min(B)+1,max(A)-min(A)+1;C=C[::E,::D];A,B=N(all(C==AS,axis=-1));return C[min(A):max(A)+1,min(B):max(B)+1],min(B),min(A),D,E
def Ah(img,left,top,min_x,min_y,batch_width,batch_height):
	S=batch_height;R=batch_width;Q=min_y;O=min_x;B=img;J,U={},{};V=[P(A)for A in AN]
	for(b,(D,H))in F(zip(Z,V)):
		K=AF(inRange(B,H,H))
		if K is not A and G(K)>0 and(D!=e or G(J)<G(Z)-1):J[D]=K.reshape(-1,2).tolist()
	L=zeros(B.shape[:2],dtype=M)
	for c in Ab:L|=all(B==c,axis=-1)
	d=dilate(L,Ac)&~L
	for(D,f)in J.items():
		for(E,C)in f:
			if 0<=E<B.shape[1]and 0<=C<B.shape[0]and d[C,E]:U[D]=left+(E+O)*R,top+(C+Q)*S;break
	W=[]
	for(b,(D,H))in F(zip(Z,V)):
		X=all(B==H,axis=-1).astype(M)
		if not any(X):continue
		Y,Y,N,Y=j(X,connectivity=4)
		for a in I(1,G(N)):
			E,C=N[a,k],N[a,l]
			if C>0 and r(B[C-1,E])==(5,5,5):W.append(((left+(E+O)*R,top+(C+Q)*S),D))
	return U,[A for(B,A)in T(W,key=lambda i:i[0][0])]
def Ai(img,detected_hex_codes):
	W=detected_hex_codes;O=img;X=all(O==AT,axis=-1);Y=all(O==AU,axis=-1)
	if not any(X)or not any(Y):return A,A,[]
	C,Z=N(X);C,a=N(Y);p=min(a)-(max(Z)+1);q=O[:,max(Z)+1:min(a)];b=c=A
	for(R,s)in F(AV):
		P=all(q==s,axis=-1)
		if any(P):
			C,d=N(P)
			if G(d)>0:
				e=ceil(min(d)/p*150).astype(H)
				if R==0:b=e
				else:c=e
	E={}
	for(R,t)in F(AO):
		P=all(O==AP[R],axis=-1).astype(M)
		if not any(P):continue
		C,C,S,C=j(P);U=AQ[t]
		for i in I(1,G(S)):
			J,n=S[i,k],S[i,l]
			if J not in E:E[J]=[D,D,D]
			if n>0:
				V=r(O[n-1,J])
				if V==U[f]:E[J][0]=B
				elif V==U[g]:E[J][1]=B
				elif V==U[h]:E[J][2]=B
	K=[]
	for(o,(C,Q))in F(T(E.items())):
		if o>=G(W):continue
		u=W[o];L=m.get(u,'').upper()
		if not L:continue
		v=Q.count(B)
		if v==3:K.append((L,'ANY'))
		elif Q==[B,B,D]:K.append((L,A1))
		elif Q[0]:K.append((L,A0))
		elif Q[1]:K.append((L,z))
		elif Q[2]:K.append((L,y))
	return b,c,K
def Aj(constraints,target,start_point):
	K=constraints;M=AG('AnvilRecipeOptimization',AH);h={A:U(1 for(B,C)in K if B==A and B!=V)for A in Q};i=U(1 for(A,B)in K if A==V);N={A:AI(A,lowBound=h[A],cat=AJ)for A in Q};M+=X(Y[A]*N[A]for A in Q)+start_point==target,'PerfectForging';M+=X(N[A]for A in[b,c,d])>=i,'HitRuleHelper';M+=X(N.values()),'Total_Operations';M.solve(AK(msg=D));E={A:H(N[A].varValue)for A in Q};K.sort(key=lambda c:U(L[c[1]]>>A&1 for A in I(3)));G=[A,A,A]
	def Z(op):
		if op==V:op=next(A for A in T([f"{A}_HIT"for A in['LIGHT','MEDIUM','HARD']],key=lambda x:E[x])if E[A])
		E[op]-=1;return op
	for(C,O)in K:
		a=U(L[O]>>A&1 for A in I(3));P=D
		if a==1:
			for(g,e)in F([1,2,4]):
				if L[O]&e:G[g]=Z(C);P=B;break
		elif a==2:
			for(g,e)in F([1,2,4]):
				if L[O]&e:
					for J in I(2,-1,-1):
						if G[J]is A and L[O]^1<<J:G[J]=Z(C);P=B;break
					if P:break
		elif a==3:
			for J in I(2,-1,-1):
				if G[J]is A:G[J]=Z(C);P=B;break
	R=[]
	for C in T(E.keys(),reverse=B,key=lambda x:E[x]+1000*(Y[x]>0)):R.extend([C]*E[C])
	f=[]
	if R:
		S,W=R[0],1
		for C in R[1:]:
			if C!=S:f.extend([S]*W);S,W=C,1
			else:W+=1
		f.extend([S]*W)
	return f+[B for B in reversed(G)if B is not A]
def p(steps,buttons):
	B=buttons;D=n.get
	for E in steps:
		A=D(E)
		if A and A in B:C=B[A];Ae(H(C[0]),H(C[1]))
def Ak():
	if R and S:p(R,S)
def q(should_execute=B):
	global R,S
	try:
		I,J,K,L,L=Af();E,M,N,O,P=Ag(I);F,Q=Ah(E,J,K,M,N,O,P);G,H,T=Ai(E,Q)
		if G is A or H is A:return
		B=Aj(T,G,H);D={};U=n.get
		for V in set(B):
			C=U(V)
			if C and C in F:D[C]=F[C]
		if should_execute:p(B,D)
		else:s('\nCalculated steps:',B)
		R,S=B,D
	except:pass
if __name__=='__main__':s('Press Z to calculate and execute\nPress X to execute the last operation (without recomputing)\nPress C to calculate only (no execution)\nPress \\ to exit');Ad()