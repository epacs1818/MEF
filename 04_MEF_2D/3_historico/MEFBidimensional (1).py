import numpy as np

with open("Input.txt", "r", encoding="utf-8") as arq:
    
    lin = arq.readline()#============================================================
    lin = arq.readline()#				tipo de elemento
    lin = arq.readline()#=== Quadrilateral (1) == Triangular(2) =====================
    
    lin = arq.readline().split()
    tipo_elemento = int(lin[0])
    
    lin = arq.readline()#============================================================
    lin = arq.readline()
    
    lin = arq.readline()#==== Número de pontos de integração ========================
    lin = arq.readline()#tipo de elemento:  			csi				eta
    lin = arq.readline()#	Quadrilateral(Gauss):  n_pont_int_csi	n_pont_int_eta
    lin = arq.readline()#	Triangular(Hammer):	   n_pont_int	
    lin = arq.readline()#-----------------------------------------------------------
    lin = arq.readline()#	Quadrilateral
    lin = arq.readline()#==== n_pont_int_csi === n_pont_int_eta ====================
    
    if (tipo_elemento == 1): 
        lin = arq.readline().split()		
        n_pont_int_csi = int(lin[0])
        n_pont_int_eta= int(lin[1])
    
    lin = arq.readline()#===========================================================
    lin = arq.readline()#	Triangular
    lin = arq.readline()#==== n_pont_int ===========================================
    		
    if (tipo_elemento == 2): 
        lin = arq.readline().split()		
        n_pont_int = int(lin[0])

    		
    lin = arq.readline()#===========================================================
    lin = arq.readline() 
       
    lin = arq.readline()#===== DADOS GERAIS =========================================
    lin = arq.readline()#	nnos	nelems	n_nos_elem			tipo_EP 
    lin = arq.readline()#================================ (EPD = 0) == (EPT = 1)=====
    
    lin = arq.readline().split()
    nnos = int(lin[0])
    nelems = int(lin[1])
    n_nos_elem = int(lin[2])
    tipo_EP	= int(lin[3])
    print("nnos, nelems:", nnos, nelems)
    print("n_nos_elem, tipo_EP:", n_nos_elem, tipo_EP)
    
    lin = arq.readline()#=====================
    lin = arq.readline()#

    lin = arq.readline()#===== MATERIAIS ==========
    lin = arq.readline()#	nmats
    lin = arq.readline()#==========================
    
    lin = arq.readline().split()
    nmats = int(lin[0])
    
    lin = arq.readline()#==========================
    lin = arq.readline()#	mat		young       poisson
    lin = arq.readline()#==========================
    
    young = np.zeros(nmats, dtype = float)
    poisson = np.zeros(nmats, dtype = float)
    for i_mat in range(0,nmats):
        lin = arq.readline().split()
        young[int(lin[0])-1] = float(lin[1])
        poisson[int(lin[0])-1] = float(lin[2])
        
    lin = arq.readline()#==========================
    lin = arq.readline()#
    
    arq.readline()#== SECOES TRANSVERSAIS ===
    arq.readline()#	nsect
    arq.readline()#==========================
    
    lin = arq.readline().split()
    nsect = int(lin[0])
    
    arq.readline()#==========================
    arq.readline()#	secao		espessura
    arq.readline()#==========================
    
    esp = np.zeros((nsect), dtype = float)
    for i_sec in range(0,nsect):
        lin = arq.readline().split()
        sec= int(lin[0]) - 1
        esp[sec] = float(lin[1])
    print("esp: ", esp)
    
    arq.readline()#==========================
    arq.readline()#    
    

    arq.readline()#==== COORDENADAS =============================
    arq.readline()#	no	coord_x		coord_y
    arq.readline()#==============================================
    
    coord = np.zeros((nnos,2), dtype = float)
    for ino in range(0,nnos):
        lin = arq.readline().split()
        no = int(lin[0])
        coord[no-1,0] = float(lin[1])
        coord[no-1,1] = float(lin[2])
    print("coord: ", coord)
       
    arq.readline()#==============================================
    arq.readline()
    
    lin = arq.readline()#==== ELEMENTOS ===============================
    lin = arq.readline()#	elem	no1 .. n_nos_elem		material    secao
    lin = arq.readline()#==============================================
    
    inc = np.zeros((nelems,n_nos_elem), dtype = int)
    material = np.zeros(nelems, dtype = int)
    secao = np.zeros(nelems, dtype = int)
    for i_elems in range(0,nelems):
        lin = arq.readline().split()
        for i_n_nos_elem in range(0,n_nos_elem):
            inc[int(lin[0])-1,i_n_nos_elem] = int(lin[i_n_nos_elem+1])
        material[int(lin[0])-1] = int(lin[n_nos_elem+1])
        secao[int(lin[0])-1] = int(lin[n_nos_elem+2])
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
	
  
def matriz_constitutiva(tipo_EP, poisson, young):
    
    matriz_const = np.zeros((3,3), dtype = float)
    
    if (tipo_EP == 0): #Estado Plano de Deformação (EPD)
        nil = poisson / (1.0 - poisson)
        El = young / (1.0 - poisson*poisson)
    elif (tipo_EP == 1): #Estado Plano de Tensão (EPT)
        nil = poisson
        El = young
      
    matriz_const[0,0] = 1.0
    matriz_const[0,1] = nil
    matriz_const[1,0] = nil
    matriz_const[1,1] = 1.0 
    matriz_const[2,2] = (1.0 - nil) / 2.0
    
    matriz_const = matriz_const * (El / (1.0 - nil*nil))
    
    return matriz_const
matriz_const = matriz_constitutiva(tipo_EP, poisson[0], young[0])
print("matriz_const: ", matriz_const)


def funcoes_forma(tipo_elemento, n_nos_elem, csi, eta):
    
    if (tipo_elemento == 1): #quadrilateral
        if (n_nos_elem == 4): # aproximação linear
            fi = np.zeros((n_nos_elem), dtype = float)
            fi[0] = 1.0 / 4.0 * (csi - 1.0) * (eta - 1.0) 
            fi[1] = 1.0 / 4.0 * (csi + 1.0) * (eta - 1.0)
            fi[2] = 1.0 / 4.0 * (csi - 1.0) * (eta + 1.0)
            fi[3] = 1.0 / 4.0 * (csi + 1.0) * (eta + 1.0)
        elif (n_nos_elem == 8): # aproximação quadrática
            pass
        elif (n_nos_elem == 9): # aproximação quadrática
            pass
        
    elif (tipo_elemento == 2): #triangular
        if (n_nos_elem == 3): # aproximação linear
            fi = np.zeros((n_nos_elem), dtype = float)
            fi[0] = 1.0 - csi - eta
            fi[1] = csi
            fi[2] = eta
        elif (n_nos_elem == 6): # aproximação quadrática
            pass
        elif (n_nos_elem == 10): # aproximação cúbica
            pass
        
    return fi


def der_funcoes_forma(tipo_elemento, n_nos_elem, csi, eta):
    
    if (tipo_elemento == 1): # quadrilateral
        if (n_nos_elem == 4): # aproximação linear
            dfi = np.zeros((n_nos_elem,2), dtype = float)
            dfi[0,0] = -1.0 / 4.0 * (eta - 1.0); dfi[0,1] = -1.0 / 4.0 * (csi - 1.0)  
            dfi[1,0] =  1.0 / 4.0 * (eta - 1.0); dfi[1,1] = -1.0 / 4.0 * (csi + 1.0) 
            dfi[2,0] = -1.0 / 4.0 * (eta + 1.0); dfi[2,1] =  1.0 / 4.0 * (csi - 1.0) 
            dfi[3,0] =  1.0 / 4.0 * (eta + 1.0); dfi[3,1] =  1.0 / 4.0 * (csi + 1.0) 
            
        elif (n_nos_elem == 8): # aproximação quadrática
            pass
        elif (n_nos_elem == 9): # aproximação quadrática
            pass
        
    elif (tipo_elemento == 2): # triangular
        if (n_nos_elem == 3): # aproximação linear
            dfi = np.zeros((n_nos_elem,2), dtype = float)
            dfi[0,0] = -1.0; dfi[0,1] = -1.0
            dfi[1,0] =  1.0; dfi[1,1] =  0.0
            dfi[2,0] =  0.0; dfi[2,1] =  1.0
            
        elif (n_nos_elem == 6): # aproximação quadrática
            pass
        elif (n_nos_elem == 10): # aproximação cúbica
            pass
        
    return dfi
 
 
def pontos_integracao(tipo_elemento,n_pontos_int):
    
    if (tipo_elemento == 1): # Quadratura de Gauss (quadrilaterais)
        if (n_pontos_int == 1):
            coord_pont_int = np.zeros((1), dtype =float)
            w_coord_pont_int = np.zeros((1), dtype =float)
            coord_pont_int[0] = 0.0; w_coord_pont_int[0] = 2.0
            
        elif (n_pontos_int == 2):
            coord_pont_int = np.zeros((2), dtype =float)
            w_coord_pont_int = np.zeros((2), dtype =float)
            coord_pont_int[0] = -1.0 / np.sqrt(3.0); w_coord_pont_int[0] = 1.0
            coord_pont_int[1] =  1.0 / np.sqrt(3.0); w_coord_pont_int[1] = 1.0
            
        elif (n_pontos_int == 3):
            coord_pont_int = np.zeros((3), dtype =float)
            w_coord_pont_int = np.zeros((3), dtype =float)
            coord_pont_int[0] = -np.sqrt(3.0 / 2.0); w_coord_pont_int[0] = 5.0 / 9.0
            coord_pont_int[1] =  0.0;                w_coord_pont_int[1] = 8.0 / 9.0
            coord_pont_int[2] =  np.sqrt(3.0 / 2.0); w_coord_pont_int[2] = 5.0 / 9.0
            
        elif (n_pontos_int == 4):
            pass
        
    elif (tipo_elemento == 2): # Quadratura de Hammer (triangulares)
        pass
    
    return coord_pont_int, w_coord_pont_int
 

def conectividade(nelems, inc):
    # Calcula a matriz de conectividade
    # var:
    #       conec
    # tamanho:
    #       [n_elems,n_gl_elem]
    
    conec = np.zeros((nelems,6), dtype = int)
    for i_elem in range(0,nelems):
        for i_no in range(0,2):
            for i_dir in range(0,2):
                conec[i_elem,2*i_no+i_dir] = 2 * (inc[i_elem,i_no] - 1) + (i_dir + 1)
    
    return conec
conec = conectividade(nelems, inc)
print("conec: ", conec)


def matriz_rigidez_elemento(tipo_elemento, i_elem, poisson, young,
                            n_pont_int_csi, n_pont_int_eta):
        
    # matriz constitutiva do elemento
    mat_D = matriz_constitutiva(tipo_elemento, poisson, young)
    
    # coordenadas dos nós do elemento
    x = np.zeros((n_nos_elem), dtype = float)
    y = np.zeros((n_nos_elem), dtype = float)
    for i_no in range(0,n_nos_elem):    
        x[i_no] = coord[inc[i_elem,i_no] - 1,0]
        y[i_no] = coord[inc[i_elem,i_no] - 1,1]
    
    if (tipo_elemento == 1) # quadrilateral
    
        # coordenada e peso dos pontos de integração
        coord_pont_int_csi, w_coord_pont_int_csi = pontos_integracao(tipo_elemento,n_pont_int_csi)
        coord_pont_int_eta, w_coord_pont_int_eta = pontos_integracao(tipo_elemento,n_pont_int_eta)
        
        # matriz de rigidez do elemento
        kelem = np.zeros((2*n_nos_elem,2*n_nos_elem), dtype = float)
        for i_ponto_int in range(0,n_pont_int_csi):
            for j_ponto_int in range(0,n_pont_int_eta):
                
                # coordenadas do ponto de integração
                csi = coord_pont_int_csi[i_ponto_int]
                eta = coord_pont_int_eta[j_ponto_int]
                
                # pedos do ponto de integração
                w_i = w_coord_pont_int_csi[i_ponto_int]
                w_j = w_coord_pont_int_eta[j_ponto_int]
                
                # derivada das funções de forma
                dfi = der_funcoes_forma(tipo_elemento, n_nos_elem, csi, eta)
                dN_dcsi = dfi[:,0]
                dN_deta = dfi[:,1]
                
                # matriz jacobiana
                mat_J = np.zeros((2,2), dtype = float)
                for i_no in range(0,n_nos_elem):
                    mat_J[0,0] = dN_dcsi[i_no] * x[i_no]
                    mat_J[0,1] = dN_dcsi[i_no] * y[i_no]
                    mat_J[1,0] = dN_deta[i_no] * x[i_no]
                    mat_J[1,1] = dN_deta[i_no] * y[i_no]
                
                # determinante da matriz jacobiana
                det_J = np.linalg.det(mat_J)
                
                # inversa da matriz jacobiana
                inv_mat_J = np.zeros((2,2), dtype = float)
                inv_mat_J = np.linalg.inv(mat_J)
                
                # matriz de relações cinemáticas
                mat_B = np.zeros((3,2*n_nos_elem), dtype = float)
                for i_no in range(0,n_nos_elem):
                    mat_B[0,2*i_no - 1] = dN_dcsi[i_no]*inv_mat_J[0,0] + dN_deta[i_no]*inv_mat_J[1,0] 
                    mat_B[1,] = 
                    mat_B[2,] = 
                
                # matriz de rigidez do elemento
                kelem += np.dot(np.tranpose(mat_B),np.dot(mat_D,mat_B)) * det_J * w_i * w_j
    
    elif (tipo_elemento == 2) # triangular
        pass
    
    return






""""
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
"""




    








