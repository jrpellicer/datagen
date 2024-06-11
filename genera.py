import json
import random
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

        elif tipo =="seq":
            lista_valores=genera_seq(propiedades,registros)

    return lista_valores


with open("prueba.json", encoding='utf-8') as archivo:
    datos=json.load(archivo)

# Recorremos cada una de los definiciones de ficheros en el archivo de configuración
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
            for flds in fichero["fields"]:
                campos[flds] = rellena_campo(fichero["fields"][flds],registros)

        print(campos)


# Comprobar unique en alfanumérico
# Generar secuencial en alfanumérico





        # Generamos registros
        # Abrimos fichero para escritura
        #f = open(nombre_archivo, "w")

        #for i in range(registros):
            #f.write("HolaMundo!\n")

        # Cerramos fichero
        #f.close
