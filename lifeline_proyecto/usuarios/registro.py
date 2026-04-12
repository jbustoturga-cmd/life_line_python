# usuarios/registro.py
# LEIDY - Lectura y escritura de usuarios en archivo .txt
# Segun la guia de clase del profesor (actividad ADSO)

import os
from datetime import datetime

# Ruta del archivo donde se guardan los usuarios
ARCHIVO_USUARIOS = "usuarios.txt"


def registrar_usuario(nombre, email):
    """
    Guarda un nuevo usuario en el archivo usuarios.txt
    Formato de cada linea: nombre,email,fecha_registro
    """
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(ARCHIVO_USUARIOS, "a", encoding="utf-8") as archivo:
        archivo.write(f"{nombre},{email},{fecha}\n")


def listar_usuarios():
    """
    Lee todos los usuarios guardados en usuarios.txt
    Retorna una lista de diccionarios con nombre, email y fecha
    """
    usuarios = []
    try:
        with open(ARCHIVO_USUARIOS, "r", encoding="utf-8") as archivo:
            for linea in archivo:
                linea = linea.strip()
                if linea:  # Ignorar lineas vacias
                    partes = linea.split(",")
                    if len(partes) >= 2:
                        usuario = {
                            "nombre": partes[0],
                            "email": partes[1],
                            "fecha_registro": partes[2] if len(partes) > 2 else "Sin fecha"
                        }
                        usuarios.append(usuario)
    except FileNotFoundError:
        # Si el archivo no existe, retornamos lista vacia (sin error)
        pass
    return usuarios


def buscar_usuario_por_nombre(nombre_buscar):
    """
    Busca usuarios cuyo nombre contenga el texto buscado.
    Retorna lista de usuarios que coincidan.
    (Extension opcional de la guia de clase)
    """
    todos = listar_usuarios()
    resultado = [
        u for u in todos
        if nombre_buscar.lower() in u["nombre"].lower()
    ]
    return resultado


def email_ya_existe(email):
    """
    Verifica si un email ya esta registrado en el archivo.
    Retorna True si ya existe, False si no.
    (Validacion de duplicados - extension opcional de la guia)
    """
    usuarios = listar_usuarios()
    for u in usuarios:
        if u["email"].lower() == email.lower():
            return True
    return False