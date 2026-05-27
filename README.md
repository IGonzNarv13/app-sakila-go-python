# Sakila Wiki Desktop

Aplicación cliente-servidor desarrollada para la materia de Despliegue de Aplicaciones Empresariales. El sistema permite consultar información de la base de datos Sakila, administrar actores mediante operaciones CRUD y comunicar usuarios conectados mediante chat grupal y privado con actualización por eventos.

## Descripción general

Sakila Wiki Desktop está compuesto por un servidor desarrollado en Go y un cliente de escritorio desarrollado en Python con CustomTkinter.

El servidor expone una API REST que se conecta a MySQL y consume la base de datos Sakila. El cliente de escritorio se comunica con el servidor mediante peticiones HTTP en formato JSON. Además, el sistema implementa Server-Sent Events para actualizar automáticamente el chat y la lista de usuarios conectados cuando ocurre un evento en el servidor.

## Arquitectura del sistema

```text
MySQL Sakila
    ↓
Servidor Go API REST
    ↓
Cliente de escritorio Python CustomTkinter
```

## Tecnologías utilizadas

| Componente | Tecnología |
|---|---|
| Backend | Go |
| Frontend | Python |
| Interfaz gráfica | CustomTkinter |
| Base de datos | MySQL |
| Base de datos de prueba | Sakila |
| Comunicación | API REST |
| Formato de intercambio | JSON |
| Eventos en tiempo real | Server-Sent Events |
| Control de versiones | Git / GitHub |

## Funcionalidades principales

- Inicio de sesión mediante nombre de usuario.
- Conexión de múltiples clientes al mismo servidor.
- Registro de usuarios conectados.
- Avisos automáticos cuando un usuario se conecta o desconecta.
- Consulta de películas desde la base Sakila.
- Filtro de películas por título.
- Filtro de películas por categoría.
- Consulta del catálogo de categorías.
- CRUD completo de actores:
  - Crear actor.
  - Consultar actores.
  - Buscar actor por ID.
  - Actualizar actor.
  - Eliminar actor.
- Chat grupal entre usuarios conectados.
- Chat privado entre usuarios.
- Actualización automática del chat mediante eventos.
- Interfaz de escritorio modular.

## Estructura del proyecto

```text
api-sakila/
│
├── main.go
├── go.mod
├── go.sum
├── .env.example
├── README.md
│
├── desktop-client/
│   ├── main.py
│   ├── requirements.txt
│   │
│   ├── services/
│   │   └── api.py
│   │
│   ├── components/
│   │   └── sidebar.py
│   │
│   └── views/
│       ├── home_view.py
│       ├── films_view.py
│       ├── categories_view.py
│       ├── actors_admin_view.py
│       └── communication_view.py
│
└── frontend-python/
    └── versión previa en Streamlit
```

## Requisitos previos

Antes de ejecutar el proyecto es necesario tener instalado:

- Go.
- Python 3.
- MySQL Server.
- MySQL Workbench, opcional pero recomendado.
- Base de datos Sakila cargada en MySQL.

## Configuración de la base de datos

La base de datos utilizada es Sakila. Para verificar que está cargada correctamente en MySQL, se puede ejecutar:

```sql
SHOW DATABASES;

USE sakila;

SHOW TABLES;
```

Algunas tablas esperadas son:

```text
actor
category
film
film_actor
inventory
rental
customer
payment
```

## Variables de entorno

El backend utiliza un archivo `.env` para configurar la conexión con MySQL.

Crear un archivo `.env` en la raíz del proyecto con el siguiente contenido:

```env
DB_USER=root
DB_PASSWORD=tu_password
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=sakila
API_PORT=8080
```

También se incluye un archivo `.env.example` como referencia. El archivo `.env` no debe subirse al repositorio porque contiene información sensible.

## Instalación del backend

Desde la raíz del proyecto:

```bash
go mod tidy
```

Ejecutar el servidor:

```bash
go run main.go
```

Si todo está correcto, la consola mostrará algo similar a:

```text
Conexión exitosa a MySQL - Base de datos Sakila
Servidor corriendo en http://localhost:8080
```

## Instalación del cliente de escritorio

Entrar a la carpeta del cliente:

```bash
cd desktop-client
```

Instalar dependencias:

```bash
python -m pip install -r requirements.txt
```

Ejecutar el cliente:

```bash
python main.py
```

## Orden recomendado de ejecución

Primero se debe iniciar el servidor:

```bash
go run main.go
```

Después se puede abrir uno o varios clientes de escritorio:

```bash
python main.py
```

Todos los clientes abiertos se conectarán al mismo servidor en `localhost:8080`.

## Endpoints principales

### Estado del servidor

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/api/health` | Verifica que el servidor esté funcionando |

### Películas

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/api/films` | Lista películas |
| GET | `/api/films/search?title=academy` | Busca películas por título |
| GET | `/api/films/category?name=Action` | Busca películas por categoría |

### Categorías

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/api/categories` | Lista categorías |

### Actores

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/api/actors` | Lista actores |
| GET | `/api/actors/{id}` | Consulta un actor por ID |
| POST | `/api/actors` | Crea un actor |
| PUT | `/api/actors/{id}` | Actualiza un actor |
| DELETE | `/api/actors/{id}` | Elimina un actor |

Ejemplo para crear actor:

```json
{
  "first_name": "ISAAC",
  "last_name": "GONZALEZ"
}
```

### Usuarios conectados

| Método | Endpoint | Descripción |
|---|---|---|
| POST | `/api/connect` | Conecta un usuario al sistema |
| GET | `/api/users` | Lista usuarios conectados |
| POST | `/api/disconnect` | Desconecta un usuario |

Ejemplo de conexión:

```json
{
  "username": "Isaac"
}
```

### Mensajes

| Método | Endpoint | Descripción |
|---|---|---|
| POST | `/api/messages` | Envía un mensaje |
| GET | `/api/messages?type=group` | Obtiene mensajes grupales |
| GET | `/api/messages?type=private&user1=Isaac&user2=Juan` | Obtiene mensajes privados entre dos usuarios |

Ejemplo de mensaje grupal:

```json
{
  "from": "Isaac",
  "to": "general",
  "text": "Hola a todos",
  "type": "group"
}
```

Ejemplo de mensaje privado:

```json
{
  "from": "Isaac",
  "to": "Juan",
  "text": "Hola Juan",
  "type": "private"
}
```

### Eventos

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/api/events` | Mantiene una conexión de eventos para actualizaciones en tiempo real |

Eventos implementados:

```text
user_connected
user_disconnected
message_received
```

## Funcionamiento del chat

El sistema de comunicación permite:

- Ver usuarios conectados.
- Abrir chat grupal.
- Abrir chat privado con otro usuario.
- Recibir mensajes sin presionar manualmente un botón de actualizar.
- Ver avisos del sistema cuando un usuario entra o sale.
- Diferenciar visualmente mensajes propios, recibidos y notificaciones del sistema.

Los mensajes se almacenan temporalmente en memoria del servidor. Si el servidor se reinicia, los usuarios conectados y mensajes se pierden.

## Compilar el backend

Para generar un ejecutable del servidor en Windows:

```bash
go build -o api-sakila.exe main.go
```

Después se puede ejecutar:

```bash
api-sakila.exe
```

## Empaquetar el cliente de escritorio

Instalar PyInstaller:

```bash
python -m pip install pyinstaller
```

Desde la carpeta `desktop-client`, generar ejecutable:

```bash
pyinstaller --onefile --windowed main.py
```

El ejecutable se generará dentro de:

```text
desktop-client/dist/
```

## Consideración sobre el servidor y múltiples clientes

El servidor debe ejecutarse una sola vez. Después se pueden abrir varios clientes de escritorio al mismo tiempo.

Si cada cliente intentara iniciar su propio servidor, el segundo podría fallar porque el puerto `8080` ya estaría ocupado. Por eso, para esta versión, se recomienda iniciar el servidor manualmente y después abrir los clientes necesarios.

## Capturas sugeridas para documentación

Se recomienda agregar capturas dentro de una carpeta `docs/` o `docs/img/`.

Ejemplo:

```text
docs/
└── img/
    ├── login.png
    ├── peliculas.png
    ├── categorias.png
    ├── actores-crud.png
    ├── usuarios-conectados.png
    ├── chat-grupal.png
    └── chat-privado.png
```

En el README pueden insertarse así:

```markdown
## Capturas del sistema

### Login
![Login](docs/img/login.png)

### Vista de películas
![Películas](docs/img/peliculas.png)

### CRUD de actores
![CRUD Actores](docs/img/actores-crud.png)

### Chat grupal
![Chat grupal](docs/img/chat-grupal.png)

### Chat privado
![Chat privado](docs/img/chat-privado.png)
```

## Pruebas recomendadas

Para validar el sistema:

1. Iniciar el servidor Go.
2. Abrir un cliente de escritorio con el usuario `Isaac`.
3. Abrir otro cliente de escritorio con el usuario `Juan`.
4. Verificar que ambos aparezcan como usuarios conectados.
5. Enviar un mensaje grupal desde un cliente.
6. Confirmar que el otro cliente lo recibe automáticamente.
7. Enviar un mensaje privado entre ambos usuarios.
8. Crear un actor desde la vista de Actores.
9. Buscar el actor creado por ID.
10. Actualizar el actor.
11. Eliminar el actor.
12. Consultar películas por título y por categoría.

## Conclusión

El proyecto implementa una aplicación cliente-servidor funcional con backend en Go, cliente de escritorio en Python y base de datos MySQL Sakila. El sistema utiliza API REST y JSON para la comunicación entre cliente y servidor, además de Server-Sent Events para actualizaciones en tiempo real. También incluye operaciones CRUD y comunicación entre usuarios, cumpliendo con los elementos principales de una aplicación empresarial distribuida.
