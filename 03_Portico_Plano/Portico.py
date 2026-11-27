import numpy as np

with open("Input.txt", "r", encoding="utf-8") as arq:
    lin = arq.readline()#===== DADOS GERAIS ==
    lin = arq.readline()#	nnos	nelems	 
    lin = arq.readline()#=====================
    
    lin = arq.readline().split()
    nnos = int(lin[0])
    nelems = int(lin[1])	
    print("nnos, nelems:", nnos, nelems)
    
    lin = arq.readline()#=====================
    lin = arq.readline()#

    lin = arq.readline()#===== MATERIAIS ==========
    lin = arq.readline()#	nmats
    lin = arq.readline()#==========================
    
    lin = arq.readline().split()
    nmats = int(lin[0])
    
    lin = arq.readline()#==========================
    lin = arq.readline()#	mat		const
    lin = arq.readline()#==========================
    
    young = np.zeros(nmats, dtype = float)
    for i_mat in range(0,nmats):
        lin = arq.readline().split()
        young[int(lin[0])-1] = float(lin[1])
        
    lin = arq.readline()#==========================
    lin = arq.readline()#
    
    arq.readline()#== SECOES TRANSVERSAIS ===
    arq.readline()#	nsect
    arq.readline()#==========================
    
    lin = arq.readline().split()
    nsect = int(lin[0])
    
    arq.readline()#==========================
    arq.readline()#	secao		area    inercia
    arq.readline()#==========================
    
    area = np.zeros((nsect), dtype = float)
    inercia = np.zeros((nsect), dtype = float)
    for i_sec in range(0,nsect):
        lin = arq.readline().split()
        sec= int(lin[0]) - 1
        area[sec] = float(lin[1])
        inercia[sec] = float(lin[2])
    print("area: ", area)
    
    arq.readline()#==========================
    arq.readline()#    
    print("inercia: ", inercia)

    arq.readline()#==== COORDENADAS =============================
    arq.readline()#	no	coord_x		coord_y
    arq.readline()#==============================================
    
    coord = np.zeros((nnos,2), dtype = float)
    for ino in range(0,nnos):
        lin = arq.readline().split()
        no = int(lin[0])
        coord[no-1,0] = float(lin[1])
        coord[no-1,1] = float(lin[2])
        
    arq.readline()#==============================================
    arq.readline()
    print("coord: ", coord)


    lin = arq.readline()#==== ELEMENTOS ===============================
    lin = arq.readline()#	elem	no1		no2		material    secao
    lin = arq.readline()#==============================================
    
    inc = np.zeros((nelems,2), dtype = int)
    material = np.zeros(nelems, dtype = int)
    secao = np.zeros(nelems, dtype = int)
    for i_elems in range(0,nelems):
        lin = arq.readline().split()
        inc[int(lin[0])-1,0] = int(lin[1])
        inc[int(lin[0])-1,1] = int(lin[2])
        material[int(lin[0])-1] = int(lin[3])
        secao[int(lin[0])-1] = int(lin[4])
    print("inc: ", inc)
    print("material: ", material)
    print("secao: ", secao)
    
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
    
    car = np.zeros(3*nnos, dtype = float)
    for i_car in range(0,ncar):
        lin = arq.readline().split()
        no = int(lin[0])
        dir = int(lin[1])
        gl = (3*(no-1)+dir) - 1
        car[gl] = float(lin[2])
    #print("car: ", car)
    
    lin = arq.readline()#==================================
    lin = arq.readline()#
    
    lin = arq.readline()#=== CONDIÇÕES DE CONTORNO ========
    lin = arq.readline()#	n_cond_cont
    lin = arq.readline()#==================================
    
    lin = arq.readline().split()#	2
    n_cond_cont = int(lin[0])
    
    lin = arq.readline()#==================================
    lin = arq.readline()#	no		dir		tipo    valor
    lin = arq.readline()#==================================
    
    tipo_cc = np.zeros((3*nnos), dtype = int)
    valor_cc = np.zeros((3*nnos), dtype = float)
    for i_cond_cont in range(0,n_cond_cont):
        lin = arq.readline().split()
        no = int(lin[0])
        dir = int(lin[1])
        gl = (3*(no-1)+dir) - 1
        tipo_cc[gl] = int(lin[2])
        valor_cc[gl] = float(lin[3])
    print("tipo_cc: ", tipo_cc)
    print("valor_cc: ", valor_cc)
    
    lin = arq.readline()#==================================
	
 

def conectividade(nelems, inc):
    # Calcula a matriz de conectividade
    # var:
    #       conec
    # tamanho:
    #       [n_elems,n_gl_elem]
    
    conec = np.zeros((nelems,6), dtype = int)
    for i_elem in range(0,nelems):
        for i_no in range(0,2):
            for i_dir in range(0,3):
                conec[i_elem,3*i_no+i_dir] = 3 * (inc[i_elem,i_no] - 1) + (i_dir + 1)
    
    return conec
conec = conectividade(nelems, inc)
print("conec: ", conec)

def comprimento_das_barras(nelems,coord):
    # calcula o comprimento das barras
    # var:
    #   comp
    # tamanho:
    #   [n_elems]
    comp = np.zeros((nelems), dtype = float)
    for i_elem in range(0,nelems):
        no_i = inc[i_elem,0] - 1
        no_f = inc[i_elem,1] - 1
        comp[i_elem] = np.sqrt(
                                np.power(coord[no_f,0]-coord[no_i,0],2)+
                                np.power(coord[no_f,1]-coord[no_i,1],2)
                               ) 
    
    return comp
comp = comprimento_das_barras(nelems,coord)
print("comp: ", comp)


def matriz_rotacao(coord,i_elem,inc):
    rot = np.zeros((6,6), dtype = float)
    no_i = inc[i_elem,0] - 1
    no_f = inc[i_elem,1] - 1
    c = (coord[no_f,0] - coord[no_i,0]) / np.sqrt(
                                                 np.power(coord[no_f,0]-coord[no_i,0],2)+
                                                 np.power(coord[no_f,1]-coord[no_i,1],2)
                                                ) 
    s = (coord[no_f,1] - coord[no_i,1]) / np.sqrt(
                                                 np.power(coord[no_f,0]-coord[no_i,0],2)+
                                                 np.power(coord[no_f,1]-coord[no_i,1],2)
                                                )     
    rot[0,0] = c; rot[0,1] = s
    rot[1,0] = -s; rot[1,1] = c
    rot[3,3] = c; rot[3,4] = s
    rot[4,3] = -s; rot[4,4] = c
    rot[2,2] = 1.0; rot[5,5] = 1
    return rot
rot = matriz_rotacao(coord,4,inc)#o elemento começa do 0
print("rot: ", rot)
 
def matriz_rigidez_local(young, area, inercia, comp):
    # calcula a matriz de rigidez do elemento no sistema local
    # var:
    #      k_elem_local
    # tamanho:
    #       [graus de liberdade, graus de liberdade]
    k_elem_local = np.zeros((6,6), dtype = float)
    k_elem_local[0,0] = young * area / comp
    k_elem_local[0,3] = -young * area / comp
    k_elem_local[3,0] = k_elem_local[0,3]
    k_elem_local[3,3] = k_elem_local[0,0]
    
    k_elem_local[1,1] = 12.0 * young * inercia / np.power(comp,3)
    k_elem_local[1,2] = 6.0 * young * inercia / np.power(comp,2)
    k_elem_local[1,4] = -12.0 * young * inercia / np.power(comp,3)
    k_elem_local[1,5] = 6.0 * young * inercia / np.power(comp,2)
    
    k_elem_local[2,1] = k_elem_local[1,2]
    k_elem_local[2,2] = 4.0 * young * inercia / comp
    k_elem_local[2,4] = -6.0 * young * inercia / np.power(comp,2)
    k_elem_local[2,5] = 2.0 * young * inercia / comp
    
    k_elem_local[4,1] = k_elem_local[1,4]
    k_elem_local[4,2] = k_elem_local[2,4]
    k_elem_local[4,4] = 12.0 * young * inercia / np.power(comp,3)
    k_elem_local[4,5] = -6.0 * young * inercia / np.power(comp,2)
    
    k_elem_local[5,1] = k_elem_local[1,5] 
    k_elem_local[5,2] = k_elem_local[2,5] 
    k_elem_local[5,4] = k_elem_local[4,5]   
    k_elem_local[5,5] = -4.0 * young * inercia / comp
        
    return k_elem_local
k_elem_local = matriz_rigidez_local(young[0], area[2], inercia[2], comp[0])
print("k_elem_local: ", k_elem_local)

def matriz_rigidez_estrutura(nnos, nelems,material,secao,area,comp,conec):
    #============================================================
    #   Montagem da matriz de rigidez
    #============================================================
    ngl = 3 * nnos
    k_estr = np.zeros((ngl,ngl), dtype = float)
    gl_elem = 3*2
    for i_elem in range(0,nelems):
        
        i_mat = material[i_elem] - 1
        i_sec = secao[i_elem] - 1
        
        #Matriz de rigidez do elemento no sistema local
        k_elem_local = matriz_rigidez_local(young[i_mat],area[i_sec],inercia[i_sec],comp[i_elem])
        
        #Matriz de rotação do elemento
        rot = matriz_rotacao(coord,i_elem,inc)
        
        #Matriz de rigidez do elemento no sistema global
        k_elem_global = np.dot(np.transpose(rot),np.dot(k_elem_local,rot))    
        
        #Montagem da matriz de rigidez da estrutura
        for i_gl in range(0,gl_elem):
            for j_gl in range(0,gl_elem):
                k_estr[conec[i_elem,i_gl]-1,conec[i_elem,j_gl]-1] += k_elem_global[i_gl,j_gl]
                
    return k_estr
k_estr = matriz_rigidez_estrutura(nnos,nelems,material,secao,area,comp,conec)
print("kestr: ", k_estr)        

def vetor_forca_estrutura(nnos,car):
    # Cacula o vetor de forças da estrutura
    ngl = 3*nnos
    f_estr = np.zeros((ngl), dtype = float)
    f_estr = car.copy()

    return f_estr
f_estr = vetor_forca_estrutura(nnos,car)
print("f_estr: ", f_estr)

def condicoes_contorno(nnos, k_estr, f_estr, tipo_cc, valor_cc):
    #============================================================
    #   Aplicação das condições de contorno
    #============================================================
    ngl = 3 * nnos
    k_estr_cc = k_estr.copy()
    f_estr_cc = f_estr.copy()
    for ilin in range(0,ngl):
        if (tipo_cc[ilin] == 1):
            for icol in range(0,ngl):
                f_estr_cc[icol] =  f_estr[icol] - k_estr[icol,ilin]*valor_cc[ilin]
            for icol in range(0,ngl): 
                k_estr_cc[ilin,icol] = 0.0
                k_estr_cc[icol,ilin] = 0.0
            k_estr_cc[ilin,ilin] = 1.0
    print(k_estr_cc)
    #============================================================   
    
    return k_estr_cc, f_estr_cc
k_estr_cc, f_estr_cc = condicoes_contorno(nnos, k_estr, f_estr, tipo_cc, valor_cc)
print("k_estr_cc: ", k_estr_cc)
print("f_estr_cc: ", f_estr_cc)
    
#Calculo dos deslocamentos
desl = np.linalg.solve(k_estr_cc,f_estr_cc)
print("desl: ",desl) 

#Calculo das reações
reacoes = np.zeros((2*nnos), dtype = float)
reacoes = np.dot(k_estr,desl) - f_estr
print("reacoes: ", reacoes)   


def forca_interna(nelems,coord,inc,desl,young,area,comp,car):
    
    f_int_elem = np.zeros((6), dtype = float)
    u_local = np.zeros((6), dtype = float)
    U_elem = np.zeros((6), dtype = float)
    for i_elem in range(0,nelems):
        
        i_mat = material[i_elem] - 1
        i_sec = secao[i_elem] - 1
        
        # Deslocamentos de cada elemento no sistema global
        for i_no in range(0,2):
            for i_dir in range(0,3):
                U_elem[3*i_no+i_dir] = desl[(3*(inc[i_elem,i_no]-1)+i_dir)]
        
        # Matriz de rotação
        rot = matriz_rotacao(coord, i_elem, inc)
        
        # Vetor de desocamentos no sistema local
        u_local = np.dot(rot,U_elem)
        
        # Matriz de rigidez do elemento no sistema local
        k_elem_local = matriz_rigidez_local(young[i_mat],area[i_sec],inercia[i_sec],comp[i_elem])
        
        # Força interna no elemento
        f_int_elem = np.dot(k_elem_local,u_local) 
        print("f_int_elem: ", i_elem, f_int_elem)
    
    return f_int_elem
f_int_elem = forca_interna(nelems,coord,inc,desl,young,area,comp,car)
####print("forca_norma: ", forca_norma)





    








