// 1. RESTRICCIONES DE UNICIDAD (CONSTRAINTS)
CREATE CONSTRAINT user_email IF NOT EXISTS FOR (u:User) REQUIRE u.email IS UNIQUE;
CREATE CONSTRAINT article_title IF NOT EXISTS FOR (a:Article) REQUIRE a.title IS UNIQUE;
CREATE CONSTRAINT tag_name IF NOT EXISTS FOR (t:Tag) REQUIRE t.name IS UNIQUE;
CREATE CONSTRAINT category_name IF NOT EXISTS FOR (c:Category) REQUIRE c.name IS UNIQUE;

// 2. CREACIÓN DE NODOS INICIALES
CREATE (u1:User {name: "Ana Torres", email: "ana.torres@email.com"})
CREATE (u2:User {name: "Carlos Ruiz", email: "carlos.ruiz@email.com"})

CREATE (c1:Category {name: "Bases de Datos", url: "/categorias/bases-de-datos"})
CREATE (c2:Category {name: "Programación", url: "/categorias/programacion"})

CREATE (t1:Tag {name: "Neo4j", url: "/tags/neo4j"})
CREATE (t2:Tag {name: "Python", url: "/tags/python"})
CREATE (t3:Tag {name: "Grafos", url: "/tags/grafos"})

CREATE (a1:Article {
    title: "Introducción a Neo4j y Cypher",
    date: "2026-11-20",
    text: "Las bases de datos orientadas a grafos permiten modelar relaciones complejas de forma natural..."
})

CREATE (com1:Comment {
    name: "Excelente artículo introductorio",
    url: "/articulos/intro-neo4j#comment-1"
})

// 3. CREACIÓN DE RELACIONES
CREATE (u1)-[:WROTE]->(a1)
CREATE (a1)-[:IN_CATEGORY]->(c1)
CREATE (a1)-[:IN_CATEGORY]->(c2)
CREATE (a1)-[:HAS_TAG]->(t1)
CREATE (a1)-[:HAS_TAG]->(t3)

CREATE (u2)-[:POSTED]->(com1)
CREATE (com1)-[:ON_ARTICLE]->(a1);