import numpy as np

with open("Input.txt", "r", encoding="utf-8") as arq:
    lin = arq.readline()#===== DADOS GERAIS ==
    lin = arq.readline()#	nnos	nelems	 
    lin = arq.readline()#=====================
    lin = arq.readline().split()#	5		6
    nnos = int(lin[0])
    nelems = int(lin[1])	
    lin = arq.readline()#=====================
    lin = arq.readline()#

    lin = arq.readline()#===== MATERIAIS ==========
    lin = arq.readline()#	nmats
    lin = arq.readline()#==========================
    lin = arq.readline().split()#	5
    nmats = int(lin[0])
    lin = arq.readline()#==========================
    lin = arq.readline()#	mat		const
    lin = arq.readline()#==========================
    const_mat = np.zeros(nmats, dtype = float)
    for i_mat in range(0,nmats):
        lin = arq.readline().split()
        const_mat[int(lin[0])-1] = float(lin[1])
    lin = arq.readline()#==========================
    lin = arq.readline()#
    
    
    
    lin = arq.readline()#==== ELEMENTOS ===================
    lin = arq.readline()#	elem	no1		no2		mat
    lin = arq.readline()#==================================
    inc = np.zeros((nelems,2), dtype = int)
    material = np.zeros(nelems, dtype = int)
    for i_elems in range(0,nelems):
        lin = arq.readline().split()
        inc[int(lin[0])-1,0] = int(lin[1])
        inc[int(lin[0])-1,1] = int(lin[2])
        material[int(lin[0])-1] = int(lin[3])
    #print("inc: ", inc)
    #print("material: ", material)
    lin = arq.readline()#==================================
    lin = arq.readline()#
    
    lin = arq.readline()#==== CARREGAMENTOS ===============
    lin = arq.readline()#	ncar
    lin = arq.readline()#==================================
    lin = arq.readline().split()#	3
    ncar = int(lin[0])
    lin = arq.readline()#==================================
    lin = arq.readline()#	no		dir		val
    lin = arq.readline()#==================================
    car = np.zeros(nnos, dtype = float)
    for i_car in range(0,ncar):
        lin = arq.readline().split()
        car[int(lin[0])-1] = float(lin[2])
    #print("car: ", car)
    lin = arq.readline()#==================================
    lin = arq.readline()#
    
    lin = arq.readline()#=== CONDIÇÕES DE CONTORNO ========
    lin = arq.readline()#	n_cond_cont
    lin = arq.readline()#==================================
    lin = arq.readline().split()#	2
    n_cond_cont = int(lin[0])
    lin = arq.readline()#==================================
    lin = arq.readline()#	no		dir		tipo
    lin = arq.readline()#==================================
    cc = np.zeros((nnos), dtype = float)
    for i_cond_cont in range(0,n_cond_cont):
        lin = arq.readline().split()
        cc[int(lin[0])-1] = float(lin[2])
    #print("cc: ", cc)
    lin = arq.readline()#==================================
	

#============================================================
#   Montagem da matriz de rigidez
#============================================================
ngl = 1 * nnos
kestr = np.zeros((ngl,ngl), dtype = float)
kestr_cc = np.zeros((ngl,ngl), dtype = float)

#print(kestr)
for ielem in range(0,nelems):
    print("ielem: ", ielem)
    kelem = np.full((2,2), 1.0, dtype = float)
    kelem[0,1] = -1.0 
    kelem[1,0] = -1.0
    kelem = const_mat[material[ielem]-1] * kelem 
    print("kelem: ", kelem)
    for ilin in range(0,2):
        for icol in range(0,2):
            kestr[inc[ielem,ilin]-1,inc[ielem,icol]-1] += kelem[ilin,icol]
print("kestr: ", kestr)        


#============================================================
#   Aplicação das condições de contorno
#============================================================
kestr_cc = kestr.copy()
for ilin in range(0,ngl):
    if (cc[ilin] == 1):
        for icol in range(0,ngl): 
            kestr_cc[ilin,icol] = 0.0
            kestr_cc[icol,ilin] = 0.0
        kestr_cc[ilin,ilin] = 1.0
print(kestr_cc)
#============================================================


desl = np.zeros((ngl), dtype = float)
desl = np.dot(np.linalg.inv(kestr_cc),car)
print(desl)
desl = np.linalg.solve(kestr_cc,car)
print(desl)   
forc = np.zeros((ngl), dtype = float)
forc = np.dot(kestr,desl)
print(forc)   



	





    








