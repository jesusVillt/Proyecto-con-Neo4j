from datetime import date  #Obtiene la fecha actual para la publicación del articulo
import tkinter as tk  
from tkinter import messagebox, scrolledtext, ttk  #Modulos para construir la interfaz y botones

# nuestro driver para conectar a neo4j
from neo4j import GraphDatabase  
from neo4j.exceptions import ConstraintError

# configuramos Neo4j
URI = "neo4j://127.0.0.1:7687"
USUARIO = "neo4j"
PASSWORD = "contraseñaSegura123" # contraseña


class BlogDesktopApp:
    # Configura la ventana principal root
    def __init__(self, root):
        self.root = root
        self.root.title("Administrador de Blog - Neo4j")
        self.root.geometry("680x550")

        # Configuramos estilo para resaltar la pestaña de eliminar en rojo
        style = ttk.Style()
        style.configure("Eliminar.TButton", foreground="red")

        # Conexión a Neo4j
        try:
            self.driver = GraphDatabase.driver(URI, auth=(USUARIO, PASSWORD))
        except Exception as e:
            messagebox.showerror("Error de conexión", str(e))

        # Creamos el contenedor NoteBook para meter adentro las diferentes pestañas
        self.notebook = ttk.Notebook(root) 
        # nuestro contenedor ocupará toda la raiz fill=both para horizontal y vertical
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10) # le baje el padding porque se veia muy feo

        self.tab_ver = ttk.Frame(self.notebook)  #aqui es cuando ya cramos las pestañas, cuyo contendor padre será notebook
        self.tab_usuario = ttk.Frame(self.notebook)
        self.tab_usuarios_lista = ttk.Frame(self.notebook)
        self.tab_articulo = ttk.Frame(self.notebook)
        self.tab_comentar = ttk.Frame(self.notebook)
        self.tab_eliminar = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_ver, text="Ver Artículos")
        self.notebook.add(self.tab_usuario, text="Registrar Usuario")
        self.notebook.add(self.tab_usuarios_lista, text="Usuarios")
        self.notebook.add(self.tab_articulo, text="Publicar Artículo")
        self.notebook.add(self.tab_comentar, text="Comentar")
        self.notebook.add(self.tab_eliminar, text="Eliminar")

        # inicializamos los frames:
        self.crear_pestana_ver() 
        self.crear_pestana_usuario()
        self.crear_pestana_usuarios_lista()
        self.crear_pestana_articulo()
        self.crear_pestana_comentar()
        self.crear_pestana_eliminar()

    # nuestra función estrella para ejecutar las queries
    def ejecutar_query(self, query, params=None):

        with self.driver.session() as session:  #Abre una sesion temporal
            result = session.run(query, params or {})  #Ejecuta la consulta recibida en query
            # probando = [record.data() for record in result]
            # for elemento in probando:
            #     print(elemento)
            #     print("")
            return [record.data() for record in result]  #Convierte el registro obtenido en un diccionario de python

    #para la pestaña de ver articulos
    def crear_pestana_ver(self):

        # ya como atributo tenemos definido el tab, ahora lo que se hace es crear
        # un frame para este y se muestra sobre la pantalla
        frame_controles = ttk.Frame(self.tab_ver)
        frame_controles.pack(pady=10, fill="x", padx=10)

        # se coloca la etiqueta buscar articulo
        # se coloca el textbox que servira como buscardor
        # se agrega el listener que disparara el evento cargar_articulos
        ttk.Label(frame_controles, text="Buscar artículo:").pack(side=tk.LEFT, padx=(0, 5))
        self.ent_buscar_articulo = ttk.Entry(frame_controles, width=28)
        self.ent_buscar_articulo.pack(side=tk.LEFT, padx=(0, 5))
        self.ent_buscar_articulo.bind("<KeyRelease>", lambda event: self.cargar_articulos())

        # se coloca el boton refrescar este se encargará de ejecutar la función cargar_articulos        
        btn_refrescar = ttk.Button(
            frame_controles,
            text="Cargar / Actualizar Artículos",
            command=self.cargar_articulos,
        )
        btn_refrescar.pack(side=tk.RIGHT) 

        self.txt_articulos = scrolledtext.ScrolledText(
            self.tab_ver, width=75, height=22
        )
        self.txt_articulos.pack(padx=10, pady=5)

        # el estado incial de este frame ya será contar con los articulos cargados
        self.cargar_articulos() 

    def cargar_articulos(self):
        self.txt_articulos.delete("1.0", tk.END) # antes de volver a cargar, borramos todo de incio a fin
        filtro = self.ent_buscar_articulo.get().strip() if hasattr(self, "ent_buscar_articulo") else ""

        # query encargada de cargar los articulos
        # la parte del buscador se hace mediante el filtro establecido
        query = """
        MATCH (u:User)-[:WROTE]->(a:Article)
        WHERE $filtro = "" OR toLower(a.title) CONTAINS toLower($filtro)
        OPTIONAL MATCH (a)-[:IN_CATEGORY]->(c:Category)
        OPTIONAL MATCH (a)-[:HAS_TAG]->(t:Tag)
        OPTIONAL MATCH (com:Comment)-[:ON_ARTICLE]->(a)
        OPTIONAL MATCH (autor_com:User)-[:POSTED]->(com)
        RETURN a.title AS titulo, a.date AS fecha, a.text AS texto, u.name AS autor,
               collect(DISTINCT c.name) AS categorias,  
               collect(DISTINCT t.name) AS tags,
               collect(DISTINCT {usuario: autor_com.name, texto: com.name}) AS comentarios
        """ #recordemos que con collect podemos extraer los valores de campos de multiples nodos para ponerlos en una lista

        articulos = self.ejecutar_query(query, {"filtro": filtro}) # usamos la funcion definida para ejecutar las queries

       # si el diccionario esta vacio (recordemos que da un diccionario el resultado de la consulta)
        if not articulos: 
            self.txt_articulos.insert(
                tk.END, "No hay artículos que coincidan con la búsqueda.\n" if filtro else "No hay artículos en la base de datos.\n"
            )
            return

        # por cada articulo que exista en el diccionario que recogimos
        # vamos a imprimir
        for art in articulos:
            self.txt_articulos.insert(
                tk.END, f"TÍTULO: {art['titulo']} ({art['fecha']})\n"
            )
            self.txt_articulos.insert(tk.END, f"AUTOR: {art['autor']}\n")
            self.txt_articulos.insert(
                tk.END, f"CATEGORÍAS: {', '.join(art['categorias'])}\n" # categorias es una lista
            )
            self.txt_articulos.insert(
                tk.END, f"TAGS: {', '.join(art['tags'])}\n"   # lo mismo con etiquetas puede ser una lista de varios elemenots
            )
            # por ultimo insertamos el contenido del articulo
            self.txt_articulos.insert(tk.END, f"TEXTO:\n{art['texto']}\n")

            #### Esto es para la sección de los comentarios:

            comentarios_formateados = [
                f'(usuario {c["usuario"] or "desconocido"}): "{c["texto"]}"'
                for c in art["comentarios"]
                if c.get("texto")
            ]
            if comentarios_formateados:
                self.txt_articulos.insert(tk.END, "COMENTARIOS:\n")
                for com_texto in comentarios_formateados:
                    self.txt_articulos.insert(tk.END, f"  {com_texto}\n\n")
            else:
                self.txt_articulos.insert(tk.END, "COMENTARIOS: Sin comentarios\n")

            #colocamos la linea de separación
            self.txt_articulos.insert(tk.END, "-" * 60 + "\n\n")

    # Para la pestaña de usuarios
    # esta es la pestaña donde se pueden crear los usuarios
    def crear_pestana_usuario(self):
        ttk.Label(self.tab_usuario, text="Nombre del Usuario:").pack(
            pady=(20, 5)
        )
        self.ent_user_name = ttk.Entry(self.tab_usuario, width=40)
        self.ent_user_name.pack()

        ttk.Label(self.tab_usuario, text="Email del Usuario:").pack(
            pady=(10, 5)
        )
        self.ent_user_email = ttk.Entry(self.tab_usuario, width=40)
        self.ent_user_email.pack()

        ttk.Button(
            self.tab_usuario,
            text="Guardar Usuario",
            command=self.guardar_usuario,  # al momento de presionar el boton disparamos la funcion de guardar usuario
        ).pack(pady=20)


    def guardar_usuario(self):
        name = self.ent_user_name.get().strip()
        email = self.ent_user_email.get().strip()
        if not name or not email:
            messagebox.showwarning("Aviso", "Llena todos los campos.")
            return

        # Verificamos primero si el correo ya existe para dar un aviso claro
        existe = self.ejecutar_query(
            "MATCH (u:User {email: $email}) RETURN u.name AS nombre",
            {"email": email},
        )
        if existe:
            messagebox.showwarning(
                "Correo duplicado",
                f"El email '{email}' ya está registrado (usuario: {existe[0]['nombre']}).",
            )
            return

        # si ya existe ese correo no permitimos su creacion usamos el mismo nodo
        query = "MERGE (u:User {email: $email}) ON CREATE SET u.name = $name RETURN u"
        self.ejecutar_query(query, {"name": name, "email": email})
        messagebox.showinfo("Exito", f"Usuario '{name}' guardado.")
        self.ent_user_name.delete(0, tk.END)
        self.ent_user_email.delete(0, tk.END)
        self.cargar_usuarios()

    # para cargar la pestaña que muestra la lista de usuarios
    def crear_pestana_usuarios_lista(self):
        frame_busqueda = ttk.Frame(self.tab_usuarios_lista)
        frame_busqueda.pack(pady=10, fill="x", padx=10)

        ttk.Label(frame_busqueda, text="Buscar usuario:").pack(side=tk.LEFT, padx=(0, 5))  # la etiqueta que va al lado del enetry
        self.ent_buscar_usuario = ttk.Entry(frame_busqueda, width=28) # el entrye que nos servirá como buscador
        self.ent_buscar_usuario.pack(side=tk.LEFT, padx=(0, 5)) # posicionamos
        # ponemos el evento cargar_usuarios sobre el entry
        self.ent_buscar_usuario.bind("<KeyRelease>", lambda event: self.cargar_usuarios())

        ttk.Button(
            frame_busqueda,
            text="Actualizar Lista",
            command=self.cargar_usuarios,
        ).pack(side=tk.RIGHT)

        self.txt_usuarios = scrolledtext.ScrolledText(
            self.tab_usuarios_lista, width=75, height=22
        )
        self.txt_usuarios.pack(padx=10, pady=5)
        # igual que en la pestaña donde cargamos los articulos
        # los mostramos desde el incio
        self.cargar_usuarios() 


    def cargar_usuarios(self):
        self.txt_usuarios.delete("1.0", tk.END)
        filtro = self.ent_buscar_usuario.get().strip() if hasattr(self, "ent_buscar_usuario") else ""

        query = """
        MATCH (u:User)
        WHERE $filtro = "" OR toLower(u.name) CONTAINS toLower($filtro) OR toLower(u.email) CONTAINS toLower($filtro)
        RETURN u.name AS nombre, u.email AS email
        ORDER BY u.name ASC
        """

        usuarios = self.ejecutar_query(query, {"filtro": filtro})
        # si no tenemos usuarios lo hacemos saber
        if not usuarios:
            self.txt_usuarios.insert(
                tk.END, "No se encontraron usuarios.\n"
            )
            return

        # recorremos los usuarios obtenidos de la consulta para darles un formato y mostrarlos
        for usr in usuarios:
            self.txt_usuarios.insert(
                tk.END, f"NOMBRE: {usr['nombre']} | EMAIL: {usr['email']}\n"
            )
            self.txt_usuarios.insert(tk.END, "-" * 60 + "\n")

    # Cargar pestaña para publciar un articulo
    def crear_pestana_articulo(self):
        # colocamos todos los botones, etiquetas y los entries para
        # pedir los datos al usuario
        ttk.Label(
            self.tab_articulo, text="Email del Autor (ya registrado):"
        ).pack(pady=(10, 2))
        self.ent_art_email = ttk.Entry(self.tab_articulo, width=45)
        self.ent_art_email.pack()

        ttk.Label(self.tab_articulo, text="Título del Artículo:").pack(
            pady=(8, 2)
        )
        self.ent_art_title = ttk.Entry(self.tab_articulo, width=45)
        self.ent_art_title.pack()

        ttk.Label(
            self.tab_articulo, text="Categorías (separadas por coma):"
        ).pack(pady=(8, 2))
        self.ent_art_cats = ttk.Entry(self.tab_articulo, width=45)
        self.ent_art_cats.pack()

        ttk.Label(self.tab_articulo, text="Tags (separados por coma):").pack(
            pady=(8, 2)
        )
        self.ent_art_tags = ttk.Entry(self.tab_articulo, width=45)
        self.ent_art_tags.pack()

        ttk.Label(self.tab_articulo, text="Contenido del Artículo:").pack(
            pady=(8, 2)
        )
        self.txt_art_body = tk.Text(self.tab_articulo, width=50, height=6)
        self.txt_art_body.pack()

        ttk.Button(
            self.tab_articulo,
            text="Publicar Artículo",
            command=self.guardar_articulo, # la funcion que se ejecutará una vez se presione el boton
        ).pack(pady=15)

    def guardar_articulo(self):
        email = self.ent_art_email.get().strip()
        title = self.ent_art_title.get().strip()
        text = self.txt_art_body.get("1.0", tk.END).strip()

        # Se crea una lista con las categoria y las etiquetas
        cats = [
            c.strip() for c in self.ent_art_cats.get().split(",") if c.strip()
        ]
        tags = [
            t.strip() for t in self.ent_art_tags.get().split(",") if t.strip()
        ]

        # dentro de este query hacemos lo siguiente:
        # buscamos el usuario, este tiene que existir, de lo contrario no podemos publicar un articulo
        # creamos el articulo y se lo asociamos al usuario
        # desempaquetamos las categorias
        # y las unimos con el articulo, esto se hace con MARGE, muy imporatne
        query = """
        MATCH (u:User {email: $email})
        CREATE (a:Article {title: $title, date: $date, text: $text})
        CREATE (u)-[:WROTE]->(a)
        WITH a
        UNWIND $cats AS cat_name
        MERGE (c:Category {name: cat_name})
        ON CREATE SET c.url = '/categorias/' + toLower(replace(cat_name, ' ', '-'))
        CREATE (a)-[:IN_CATEGORY]->(c)
        WITH a
        UNWIND $tags AS tag_name
        MERGE (t:Tag {name: tag_name})
        ON CREATE SET t.url = '/tags/' + toLower(replace(tag_name, ' ', '-'))
        CREATE (a)-[:HAS_TAG]->(t)
        RETURN a.title AS title
        """  
        # mandamos a ejectar el query y le pasamos sus respectivos parametros
        try:
            res = self.ejecutar_query(
                query,
                {
                    "email": email,
                    "title": title,
                    "date": str(date.today()),
                    "text": text,
                    "cats": cats,
                    "tags": tags,
                },
            )
            if res:
                messagebox.showinfo("Exito", "Artículo publicado.")
                self.cargar_articulos()
            else:
                messagebox.showerror(
                    "Error", "Verifica que el email del autor exista."
                )
        except ConstraintError:
            # Captura la restricción que pusimos en la base de datos,
            # si es que el titulo ya existe
            messagebox.showwarning(
                "Título duplicado",
                f"Ya existe un artículo con el título '{title}'.",
            )

    # -- crear pestaña para realizar comentarios 
    def crear_pestana_comentar(self):
        # para la seccion de comentar
        ttk.Label(
            self.tab_comentar,
            text="--- AGREGAR COMENTARIO ---",
            font=("Arial", 10, "bold"),
        ).pack(pady=(15, 5))
        # para caputrar el email
        ttk.Label(self.tab_comentar, text="Email de quien comenta:").pack()
        self.ent_com_email = ttk.Entry(self.tab_comentar, width=40)
        self.ent_com_email.pack()

        # para capturar el titulo del articulo (necesitamos el nombre exacto para poder asociarlo)
        ttk.Label(self.tab_comentar, text="Título exacto del artículo:").pack(
            pady=(5, 0)
        )
        self.ent_com_title = ttk.Entry(self.tab_comentar, width=40)
        self.ent_com_title.pack()

        # la etiqueta "comentario" con su respectiva casilla entry:
        ttk.Label(self.tab_comentar, text="Comentario:").pack(pady=(5, 0))
        self.ent_com_text = ttk.Entry(self.tab_comentar, width=40)
        self.ent_com_text.pack()

        # por ultimo tenemos el boton
        ttk.Button(
            self.tab_comentar,
            text="Publicar Comentario",
            command=self.agregar_comentario, # la funcion que se llamará al presionar el boton
        ).pack(pady=15)

    # -- crear pestaña para eliminar
    def crear_pestana_eliminar(self):
        # para eliminar
        # en esta pestaña tenemos el titulo, el entry y el boton

        # para el titulo
        ttk.Label(
            self.tab_eliminar,
            text="--- ELIMINAR ARTÍCULO ---",
            font=("Arial", 10, "bold"),
            foreground="red",
        ).pack(pady=(20, 5))

        # para ingresar el titulo, tiene que ser exacto, del articulo a eliminar
        ttk.Label(
            self.tab_eliminar, text="Título exacto del artículo a borrar:"
        ).pack()
        self.ent_del_title = ttk.Entry(self.tab_eliminar, width=40)
        self.ent_del_title.pack()
        
        # boton que disparará la fucnion de eliminar articulo
        tk.Button(
            self.tab_eliminar,
            text="Eliminar Artículo",
            command=self.eliminar_articulo,
            bg="#d9534f",
            fg="white",
            activebackground="#c9302c",
            activeforeground="white",
        ).pack(pady=15)

    def agregar_comentario(self):
        email = self.ent_com_email.get().strip()
        title = self.ent_com_title.get().strip()
        texto = self.ent_com_text.get().strip()

        # el query a ejectar para realizar el comentario
        # obtenemos el nodo del usuario de la persona que comenta y el articulo
        #
        query = """
        MATCH (u:User {email: $email})
        MATCH (a:Article {title: $title})
        CREATE (com:Comment {
            name: $texto,
            url: '/articulos/' + toLower(replace(a.title, ' ', '-')) + '#comment'
        })
        CREATE (u)-[:POSTED]->(com)
        CREATE (com)-[:ON_ARTICLE]->(a)
        RETURN com
        """

        # llamamos a la funcion ejecutar query y pasamos los argumetnos necesarios
        # en este caso: email, title y textp
        res = self.ejecutar_query(
            query, {"email": email, "title": title, "texto": texto}
        )
        if res:
            messagebox.showinfo("Éxito", "Comentario agregado.")
            self.cargar_articulos() # actualizamos automaticamente
        else:
            messagebox.showerror("Error", "Usuario o artículo no encontrado.")

    def eliminar_articulo(self):
        title = self.ent_del_title.get().strip()

        # el query para eliminar consiste en obtener el nodo del articulo especificado
        # para eliminarlo y tambien eliminar todos los comentarios asociados a este (en caso de tenerlos)
        query = """
        MATCH (a:Article {title: $title})
        OPTIONAL MATCH (c:Comment)-[:ON_ARTICLE]->(a)
        DETACH DELETE c, a
        """
        self.ejecutar_query(query, {"title": title})
        messagebox.showinfo(
            "Eliminado", f"Si existía, '{title}' fue eliminado."
        )
        self.cargar_articulos()

    def cerrar(self):
        self.driver.close()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = BlogDesktopApp(root)
    root.protocol("WM_DELETE_WINDOW", app.cerrar)
    root.mainloop() 
