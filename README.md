# Sistema de Gestión de Blogs con Neo4j

## Descripción del proyecto

Este proyecto consiste en una aplicación de escritorio con interfaz gráfica que permite gestionar un sistema de blogs mediante una base de datos no relacional orientada a grafos, utilizando **Neo4j**.

El sistema permite administrar usuarios, artículos, comentarios, categorías y etiquetas, implementando operaciones CRUD (Crear, Leer, Actualizar y Eliminar) para gestionar la información.

## Estructura de la base de datos

La base de datos está compuesta por cinco tipos de nodos:

- **Users:** Almacena la información de los usuarios registrados.
- **Articles:** Contiene los artículos publicados por los usuarios.
- **Comments:** Almacena los comentarios realizados sobre los artículos.
- **Categories:** Clasifica los artículos por categorías.
- **Tags:** Permite asociar etiquetas a los artículos.

Estos nodos se relacionan entre sí para representar la estructura de un sistema de blogs.

## Restricciones de la base de datos

Para garantizar la integridad de la información, se establecieron las siguientes restricciones:

1. No pueden existir usuarios con el mismo correo electrónico.
2. No pueden existir artículos con el mismo título.
3. No se permiten etiquetas duplicadas.
4. No se permiten categorías duplicadas.

## Funcionalidades principales

La aplicación cuenta con seis módulos principales:

| Módulo | Descripción |
|---|---|
| **Ver artículos** | Muestra todos los artículos publicados, incluyendo autor, categoría, etiquetas y comentarios. Permite buscar artículos por nombre o palabras clave. |
| **Registrar usuario** | Permite registrar nuevos usuarios mediante su nombre y correo electrónico, validando que el correo sea único. |
| **Usuarios** | Muestra todos los usuarios registrados e incluye un buscador por nombre o correo electrónico. |
| **Publicar artículo** | Permite a un usuario registrado publicar artículos indicando título, contenido, categoría y etiquetas. |
| **Comentar** | Permite agregar comentarios a artículos existentes, identificando al usuario mediante su correo electrónico. |
| **Eliminar artículo** | Permite eliminar un artículo utilizando su título exacto. |

## Validaciones del sistema

El programa incorpora diferentes validaciones para evitar inconsistencias en la base de datos:

- Verifica que los correos electrónicos de los usuarios sean únicos.
- Comprueba que el usuario exista antes de permitir la publicación de un artículo.
- Evita la publicación de artículos con títulos duplicados.
- Verifica que tanto el usuario como el artículo existan antes de registrar un comentario.
- Solicita el título exacto del artículo para realizar su eliminación.
- Muestra mensajes de confirmación y advertencia cuando se ejecutan las operaciones.

## Tecnologías utilizadas

- **Neo4j:** Base de datos no relacional orientada a grafos.
- **Interfaz gráfica:** Aplicación para interactuar con la base de datos.
- **Operaciones CRUD:** Gestión de usuarios, artículos y comentarios.

## Objetivo del proyecto

Desarrollar una aplicación gráfica que permita interactuar de manera sencilla con una base de datos orientada a grafos, demostrando el uso de Neo4j para modelar relaciones entre diferentes entidades y realizar operaciones de administración de información
