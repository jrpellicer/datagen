import json
import random
import numpy as np
import string

# ***********************************************************************************
# Campo valor fijo ******************************************************************
# ***********************************************************************************
def genera_valor(valor,registros):
    lista = []
    for i in range(registros):
        lista.append(valor)
    return lista

# ***********************************************************************************
# Campo valor discreto***************************************************************
# ***********************************************************************************
def genera_discreto(propiedades,registros):

     # Inicializamos lista a devolver
    lista = []

    no_vacio= False
    valores = []
    pesos = []
    for subst in propiedades["values"]:
        if ("value" in subst) & ("percent" in subst):
            valores.append(subst["value"])
            pesos.append(subst["percent"])
            no_vacio = True

    if no_vacio:
        for i in range(registros):
            lista.append(random.choices(valores, weights=pesos, k=1)[0])
    
    return lista

# ***********************************************************************************
# Campo nombre **********************************************************************
# ***********************************************************************************
def procesar_csv(nombre_archivo):

    nombres = []
    pesos = []

    try:
        with open(nombre_archivo, 'r') as archivo:
            for linea in archivo:
                flds = linea.strip().split(',')
                if len(campos) >= 2:  # Asegurarse de que hay al menos dos campos
                    nombres.append(flds[0])
                    pesos.append(float(flds[1]))

        return nombres, pesos
    except FileNotFoundError:
        return [], []
    
def genera_name(propiedades,sexo,registros):

     # Inicializamos lista a devolver
    lista = []
    
    nombre_archivo = "nombres_m.csv"
    nombres_m, pesos_m = procesar_csv(nombre_archivo)
    nombre_archivo = "nombres_f.csv"
    nombres_f, pesos_f = procesar_csv(nombre_archivo)
    
    # Comprobamos si se ha especificado variable sexo correctamente
    if sexo:
        # se ha especificado el sexo        
        for i in range(registros):
            if sexo[i] == "M":
                lista.append(random.choices(nombres_m, weights=pesos_m, k=1)[0])
            else:
                lista.append(random.choices(nombres_f, weights=pesos_f, k=1)[0])
    else:
        # No se ha especificado el sexo
        nombres = nombres_m + nombres_f
        pesos = pesos_m + pesos_f
        if nombres:
            for i in range(registros):
                lista.append(random.choices(nombres, weights=pesos, k=1)[0])

    return lista

# ***********************************************************************************
# Campo dependiente *****************************************************************
# ***********************************************************************************
def genera_dependent(propiedades,variable,registros):
    # Obtenemos número de decimales a calcular
    if "decimals" in propiedades:
        decimales=propiedades["decimals"]
    else:
        decimales=0

    # Inicializamos lista a devolver
    lista = []
    
    if "r" in propiedades:
        r=propiedades["r"]

        if "sigma" in propiedades:
            sigma_y=propiedades["sigma"]
        else:
            sigma_y=1

        if "mu" in propiedades:
            mu_y=propiedades["mu"]
        else:
            mu=0

        # Recalculamos la sigma y la mu de la variable independiente
        mu_x=np.mean(variable)
        sigma_x=np.std(variable)

        if propiedades["distribution"] == "normal":
                if ("mu" in propiedades) & ("sigma" in propiedades):
                    
                    # Para introducir correlación entre X e Y, utilizamos una combinación lineal
                    # Y' = a * X + b * Z, donde Z es una variable aleatoria normal
                    # y 'a' y 'b' son factores que se calculan basándose en 'r' y las desviaciones estándar
                    z = np.random.normal(0, 1, registros)  # Variable aleatoria normal estándar

                    # Calcular los factores a y b
                    a = r * (sigma_y / sigma_x)
                    b = np.sqrt(1 - r**2) * sigma_y

                    # Generar la nueva variable Y con la correlación deseada
                    y = mu_y + a * (variable - mu_x) + b * z

                    if decimales==0:
                        lista=(np.round(y).astype(int)).tolist()
                    else:
                        lista=y.tolist()

        if propiedades["distribution"] == "expo":
                if "lambd" in propiedades:
                    if propiedades["lambd"] != 0:
                        beta=1/propiedades["lambd"]
                    else:
                        beta=0

                    # Generar una variable normal auxiliar (Z)
                    z = np.random.normal(0, 1, registros)

                    # Calcular los factores a y b
                    a = r
                    b = np.sqrt(1 - r**2)

                    # Generar la nueva variable W con la correlación deseada (a partir de Z)
                    w = a * (variable - mu_x) / sigma_x + b * z

                    # Transformar W para que tenga una distribución exponencial
                    # Aplicando la transformación inversa de la función de distribución acumulativa (CDF) de la exponencial
                    y = np.random.exponential(beta, registros)

                    # Ajustar Y para que tenga la correlación deseada con X
                    # y_new = y + k * (w - mean(w)), donde k es un ajuste para mantener la correlación
                    k = r * (beta / np.std(w))
                    y = y + k * (w - np.mean(w))

                    if decimales==0:
                        lista=(np.round(y).astype(int)).tolist()
                    else:
                        lista=y.tolist()
                
    return(lista)
                
# ***********************************************************************************
# Campo numérico ********************************************************************
# ***********************************************************************************
def genera_numero(propiedades,registros):
    # Obtenemos número de decimales a calcular
    if "decimals" in propiedades:
        decimales=propiedades["decimals"]
    else:
        decimales=0

    # Obtenemos si es una clave única
    if "unique" in propiedades:
        unico=propiedades["unique"]
    else:
        unico="no"

    # Inicializamos lista a devolver
    lista = []

    # Comprobamos si el valor es una distribución de probabilidad (Normal o Exponencial)
    if "distribution" in propiedades:
        for i in range(registros):
            if propiedades["distribution"] == "normal":
                if ("mu" in propiedades) & ("sigma" in propiedades):
                    if decimales==0:
                        lista.append(int(random.normalvariate(propiedades["mu"],propiedades["sigma"])))
                    else:
                        lista.append(round(random.normalvariate(propiedades["mu"],propiedades["sigma"]),decimales))
            if propiedades["distribution"] == "expo":
                if "lambd" in propiedades:
                    if decimales==0:
                        lista.append(int(random.expovariate(propiedades["lambd"])))
                    else:
                        lista.append(round(random.expovariate(propiedades["lambd"]),decimales))
    
    # El valor a generar es aleatorio uniforme
    else:
        if "max" in propiedades:
            max=propiedades["max"]
        else:
            max=65535

        if "min" in propiedades:
            min=propiedades["min"]
        else:
            min=0

        if ((max-min+1) >=  registros) or (unico != 'yes'):
            for i in range(registros):
                existe=True
                while existe:
                    if decimales==0:
                        valor=random.randint(min,max)
                    else:
                        valor=round(random.uniform(min,max),decimales)
                    if valor not in lista:
                        existe=False
                
                lista.append(valor)
    
    # Devolvemos lista generada
    return lista

# ***********************************************************************************
# Campo numérico secuencial**********************************************************
# ***********************************************************************************
def genera_seq(propiedades,registros):
    # Obtenemos número de decimales 
    if "decimals" in propiedades:
        decimales=propiedades["decimals"]   
    else:
        decimales=0
    
    incremento=1/(10**decimales)
    
    if "ini" in propiedades:
        contador=propiedades["ini"]
    else:
        contador=0
    # Inicializamos lista a devolver
    lista = []

    for i in range(registros):
        if decimales==0:
            lista.append(int(contador))
        else:
            lista.append(round(contador,decimales))

        contador=contador + incremento

    return lista

# ***********************************************************************************
# Campo alfabético ******************************************************************
# ***********************************************************************************
def genera_str(propiedades,registros):
    lista = []
    contador=0
    for i in range(registros):
        cadena=""
        for subst in propiedades["str"]:
            if ("len" in subst) & ("type" in subst):
                if subst["type"]=="int":
                    numeros_aleatorios = ''.join(random.choices(string.digits, k=subst["len"]))
                    cadena=cadena+numeros_aleatorios
                if subst["type"]=="char":
                    letras_alfabeticas = ''.join(random.choices(string.ascii_uppercase, k=subst["len"]))
                    cadena=cadena+letras_alfabeticas
                if subst["type"]=="seq":
                    if "ini" in subst:
                        valor_ini=subst["ini"]
                    else:
                        valor_ini=0

                    letras_alfabeticas = str(contador+valor_ini).zfill(subst["len"])
                    contador = contador +1
                    cadena=cadena+letras_alfabeticas
        lista.append(cadena)
    return lista

def rellena_campo(propiedades,registros):
    lista_valores = []
    
    # Comprobamos si hay que poner un valor fijo
    if "value" in propiedades:
        lista_valores=genera_valor(propiedades["value"],registros)

    elif "type" in propiedades:
        tipo=propiedades["type"]
        if tipo=="numeric":
            lista_valores=(genera_numero(propiedades,registros))

        elif tipo =="str":
            lista_valores=genera_str(propiedades,registros)

        elif tipo =="discrete":
            lista_valores=genera_discreto(propiedades,registros)

        elif tipo =="seq":
            lista_valores=genera_seq(propiedades,registros)
        
        elif tipo =="name":
            sexo=[]
            if "genere" in propiedades:
                if propiedades["genere"] in campos:
                    sexo=campos[propiedades["genere"]]
            lista_valores=genera_name(propiedades,sexo,registros)

        elif tipo =="dependent":
            if "variable" in propiedades:
                if propiedades["variable"] in campos:
                    lista_valores=genera_dependent(propiedades,campos[propiedades["variable"]],registros)


    return lista_valores


with open("prueba.json", encoding='utf-8') as archivo:
    datos=json.load(archivo)

# Recorremos cada una de los definiciones de ficheros en el archivo de definición
for fichero in datos:  
    if "file" in fichero:
        # Obtenemos nombre del fichero (tabla)
        nombre_archivo=fichero["file"]+".csv"
        # Obtenemos número de registros a generar en la tabla
        if "records" in fichero:
            registros=fichero["records"]
        registros=5

        # Creamos un diccionario vacío
        campos = {}
        if "fields" in fichero:
            for fld in fichero["fields"]:
                campos[fld] = rellena_campo(fichero["fields"][fld],registros)

        print(campos)


# Comprobar unique en alfanumérico


        # Generamos registros
        # Abrimos fichero para escritura
        #f = open(nombre_archivo, "w")

        #for i in range(registros):
            #f.write("HolaMundo!\n")

        # Cerramos fichero
        #f.close
