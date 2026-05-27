package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"strings"
	"sync"
	"time"
	"os"
	"strconv"

	_ "github.com/go-sql-driver/mysql"
	"github.com/joho/godotenv"
)

var db *sql.DB
var connectedUsers = make(map[string]User)
var messages []Message
var mutex sync.Mutex

type Event struct {
	Type string      `json:"type"`
	Data interface{} `json:"data"`
}

var eventClients = make(map[chan Event]bool)
var eventMutex sync.Mutex

// =======================
// MODELOS
// =======================

type Film struct {
	FilmID      int    `json:"film_id"`
	Title       string `json:"title"`
	Description string `json:"description"`
	ReleaseYear int   `json:"release_year"`
	Rating      string `json:"rating"`
	Length      int    `json:"length"`
}

type Actor struct {
	ActorID   int    `json:"actor_id"`
	FirstName string `json:"first_name"`
	LastName  string `json:"last_name"`
}

type ActorRequest struct {
	FirstName string `json:"first_name"`
	LastName  string `json:"last_name"`
}

type SuccessResponse struct {
	Message string `json:"message"`
}

type Category struct {
	CategoryID int    `json:"category_id"`
	Name       string `json:"name"`
}

type ErrorResponse struct {
	Error string `json:"error"`
}

type User struct {
	Username  string `json:"username"`
	ConnectedAt string `json:"connected_at"`
}

type MessageRequest struct {
	From string `json:"from"`
	To   string `json:"to"`
	Text string `json:"text"`
	Type string `json:"type"`
}

type Message struct {
	From   string `json:"from"`
	To     string `json:"to"`
	Text   string `json:"text"`
	Type   string `json:"type"`
	SentAt string `json:"sent_at"`
}

type ConnectRequest struct {
	Username string `json:"username"`
}


// =======================
// FUNCIONES AUXILIARES
// =======================

func enableCORS(w http.ResponseWriter) {
	w.Header().Set("Access-Control-Allow-Origin", "*")
	w.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
	w.Header().Set("Access-Control-Allow-Headers", "Content-Type")
}

func sendJSON(w http.ResponseWriter, statusCode int, data interface{}) {
	enableCORS(w)
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(statusCode)
	json.NewEncoder(w).Encode(data)
}

func sendError(w http.ResponseWriter, statusCode int, message string) {
	sendJSON(w, statusCode, ErrorResponse{Error: message})
}

// =======================
// HANDLERS
// =======================

func healthHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method == http.MethodOptions {
		enableCORS(w)
		return
	}

	if r.Method != http.MethodGet {
		sendError(w, http.StatusMethodNotAllowed, "Método no permitido")
		return
	}

	response := map[string]string{
		"status":  "ok",
		"message": "Servidor Go funcionando correctamente",
	}

	sendJSON(w, http.StatusOK, response)
}

func getFilmsHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method == http.MethodOptions {
		enableCORS(w)
		return
	}

	if r.Method != http.MethodGet {
		sendError(w, http.StatusMethodNotAllowed, "Método no permitido")
		return
	}

	rows, err := db.Query(`
		SELECT film_id, title, description, release_year, rating, length
		FROM film
		ORDER BY film_id
		LIMIT 200
	`)
	if err != nil {
		log.Println("Error al consultar películas:", err)
		sendError(w, http.StatusInternalServerError, "Error al consultar películas")
		return
	}
	defer rows.Close()

	var films []Film

	for rows.Next() {
		var film Film

		err := rows.Scan(
			&film.FilmID,
			&film.Title,
			&film.Description,
			&film.ReleaseYear,
			&film.Rating,
			&film.Length,
		)
		if err != nil {
			log.Println("Error al leer película:", err)
			sendError(w, http.StatusInternalServerError, "Error al leer datos de películas")
			return
		}

		films = append(films, film)
	}

	sendJSON(w, http.StatusOK, films)
}

func searchFilmsHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method == http.MethodOptions {
		enableCORS(w)
		return
	}

	if r.Method != http.MethodGet {
		sendError(w, http.StatusMethodNotAllowed, "Método no permitido")
		return
	}

	title := strings.TrimSpace(r.URL.Query().Get("title"))

	if title == "" {
		sendError(w, http.StatusBadRequest, "Debes enviar el parámetro title")
		return
	}

	rows, err := db.Query(`
		SELECT film_id, title, description, release_year, rating, length
		FROM film
		WHERE title LIKE ?
		ORDER BY title
		LIMIT 30
	`, "%"+title+"%")
	if err != nil {
		log.Println("Error al buscar películas:", err)
		sendError(w, http.StatusInternalServerError, "Error al buscar películas")
		return
	}
	defer rows.Close()

	var films []Film

	for rows.Next() {
		var film Film

		err := rows.Scan(
			&film.FilmID,
			&film.Title,
			&film.Description,
			&film.ReleaseYear,
			&film.Rating,
			&film.Length,
		)
		if err != nil {
			log.Println("Error al leer película:", err)
			sendError(w, http.StatusInternalServerError, "Error al leer datos de películas")
			return
		}

		films = append(films, film)
	}

	sendJSON(w, http.StatusOK, films)
}

func actorsHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method == http.MethodOptions {
		enableCORS(w)
		return
	}

	switch r.Method {
	case http.MethodGet:
		getActorsHandler(w, r)
	case http.MethodPost:
		createActorHandler(w, r)
	default:
		sendError(w, http.StatusMethodNotAllowed, "Método no permitido")
	}
}

func actorByIDHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method == http.MethodOptions {
		enableCORS(w)
		return
	}

	idText := strings.TrimPrefix(r.URL.Path, "/api/actors/")
	idText = strings.TrimSpace(idText)

	if idText == "" {
		sendError(w, http.StatusBadRequest, "Debes enviar el ID del actor")
		return
	}

	actorID, err := strconv.Atoi(idText)
	if err != nil || actorID <= 0 {
		sendError(w, http.StatusBadRequest, "ID de actor inválido")
		return
	}

	switch r.Method {
	case http.MethodGet:
		getActorByIDHandler(w, r, actorID)
	case http.MethodPut:
		updateActorHandler(w, r, actorID)
	case http.MethodDelete:
		deleteActorHandler(w, r, actorID)
	default:
		sendError(w, http.StatusMethodNotAllowed, "Método no permitido")
	}
}

func getActorsHandler(w http.ResponseWriter, r *http.Request) {
	rows, err := db.Query(`
		SELECT actor_id, first_name, last_name
		FROM actor
		ORDER BY actor_id DESC
		LIMIT 100
	`)
	if err != nil {
		log.Println("Error al consultar actores:", err)
		sendError(w, http.StatusInternalServerError, "Error al consultar actores")
		return
	}
	defer rows.Close()

	var actors []Actor

	for rows.Next() {
		var actor Actor

		err := rows.Scan(
			&actor.ActorID,
			&actor.FirstName,
			&actor.LastName,
		)
		if err != nil {
			log.Println("Error al leer actor:", err)
			sendError(w, http.StatusInternalServerError, "Error al leer datos de actores")
			return
		}

		actors = append(actors, actor)
	}

	sendJSON(w, http.StatusOK, actors)
}

func getActorByIDHandler(w http.ResponseWriter, r *http.Request, actorID int) {
	var actor Actor

	err := db.QueryRow(`
		SELECT actor_id, first_name, last_name
		FROM actor
		WHERE actor_id = ?
	`, actorID).Scan(
		&actor.ActorID,
		&actor.FirstName,
		&actor.LastName,
	)

	if err == sql.ErrNoRows {
		sendError(w, http.StatusNotFound, "Actor no encontrado")
		return
	}

	if err != nil {
		log.Println("Error al consultar actor por ID:", err)
		sendError(w, http.StatusInternalServerError, "Error al consultar actor")
		return
	}

	sendJSON(w, http.StatusOK, actor)
}

func createActorHandler(w http.ResponseWriter, r *http.Request) {
	var request ActorRequest

	err := json.NewDecoder(r.Body).Decode(&request)
	if err != nil {
		sendError(w, http.StatusBadRequest, "JSON inválido")
		return
	}

	request.FirstName = strings.ToUpper(strings.TrimSpace(request.FirstName))
	request.LastName = strings.ToUpper(strings.TrimSpace(request.LastName))

	if request.FirstName == "" || request.LastName == "" {
		sendError(w, http.StatusBadRequest, "El nombre y apellido son obligatorios")
		return
	}

	result, err := db.Exec(`
		INSERT INTO actor (first_name, last_name, last_update)
		VALUES (?, ?, NOW())
	`, request.FirstName, request.LastName)

	if err != nil {
		log.Println("Error al crear actor:", err)
		sendError(w, http.StatusInternalServerError, "Error al crear actor")
		return
	}

	newID, err := result.LastInsertId()
	if err != nil {
		log.Println("Error al obtener ID generado:", err)
		sendError(w, http.StatusInternalServerError, "Actor creado, pero no se pudo obtener el ID")
		return
	}

	response := map[string]interface{}{
		"message":  "Actor creado correctamente",
		"actor_id": newID,
		"actor": Actor{
			ActorID:   int(newID),
			FirstName: request.FirstName,
			LastName:  request.LastName,
		},
	}

	sendJSON(w, http.StatusCreated, response)
}

func updateActorHandler(w http.ResponseWriter, r *http.Request, actorID int) {
	var request ActorRequest

	err := json.NewDecoder(r.Body).Decode(&request)
	if err != nil {
		sendError(w, http.StatusBadRequest, "JSON inválido")
		return
	}

	request.FirstName = strings.ToUpper(strings.TrimSpace(request.FirstName))
	request.LastName = strings.ToUpper(strings.TrimSpace(request.LastName))

	if request.FirstName == "" || request.LastName == "" {
		sendError(w, http.StatusBadRequest, "El nombre y apellido son obligatorios")
		return
	}

	result, err := db.Exec(`
		UPDATE actor
		SET first_name = ?, last_name = ?, last_update = NOW()
		WHERE actor_id = ?
	`, request.FirstName, request.LastName, actorID)

	if err != nil {
		log.Println("Error al actualizar actor:", err)
		sendError(w, http.StatusInternalServerError, "Error al actualizar actor")
		return
	}

	rowsAffected, err := result.RowsAffected()
	if err != nil {
		log.Println("Error al verificar actualización:", err)
		sendError(w, http.StatusInternalServerError, "Error al verificar actualización")
		return
	}

	if rowsAffected == 0 {
		sendError(w, http.StatusNotFound, "Actor no encontrado")
		return
	}

	response := map[string]interface{}{
		"message": "Actor actualizado correctamente",
		"actor": Actor{
			ActorID:   actorID,
			FirstName: request.FirstName,
			LastName:  request.LastName,
		},
	}

	sendJSON(w, http.StatusOK, response)
}

func deleteActorHandler(w http.ResponseWriter, r *http.Request, actorID int) {
	tx, err := db.Begin()
	if err != nil {
		log.Println("Error al iniciar transacción:", err)
		sendError(w, http.StatusInternalServerError, "Error al iniciar eliminación")
		return
	}

	var exists int
	err = tx.QueryRow(`
		SELECT COUNT(*)
		FROM actor
		WHERE actor_id = ?
	`, actorID).Scan(&exists)

	if err != nil {
		tx.Rollback()
		log.Println("Error al verificar actor:", err)
		sendError(w, http.StatusInternalServerError, "Error al verificar actor")
		return
	}

	if exists == 0 {
		tx.Rollback()
		sendError(w, http.StatusNotFound, "Actor no encontrado")
		return
	}

	_, err = tx.Exec(`
		DELETE FROM film_actor
		WHERE actor_id = ?
	`, actorID)

	if err != nil {
		tx.Rollback()
		log.Println("Error al eliminar relaciones del actor:", err)
		sendError(w, http.StatusInternalServerError, "Error al eliminar relaciones del actor")
		return
	}

	_, err = tx.Exec(`
		DELETE FROM actor
		WHERE actor_id = ?
	`, actorID)

	if err != nil {
		tx.Rollback()
		log.Println("Error al eliminar actor:", err)
		sendError(w, http.StatusInternalServerError, "Error al eliminar actor")
		return
	}

	err = tx.Commit()
	if err != nil {
		log.Println("Error al confirmar eliminación:", err)
		sendError(w, http.StatusInternalServerError, "Error al confirmar eliminación")
		return
	}

	response := map[string]interface{}{
		"message":  "Actor eliminado correctamente",
		"actor_id": actorID,
	}

	sendJSON(w, http.StatusOK, response)
}

func getCategoriesHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method == http.MethodOptions {
		enableCORS(w)
		return
	}

	if r.Method != http.MethodGet {
		sendError(w, http.StatusMethodNotAllowed, "Método no permitido")
		return
	}

	rows, err := db.Query(`
		SELECT category_id, name
		FROM category
		ORDER BY name
	`)
	if err != nil {
		log.Println("Error al consultar categorías:", err)
		sendError(w, http.StatusInternalServerError, "Error al consultar categorías")
		return
	}
	defer rows.Close()

	var categories []Category

	for rows.Next() {
		var category Category

		err := rows.Scan(
			&category.CategoryID,
			&category.Name,
		)
		if err != nil {
			log.Println("Error al leer categoría:", err)
			sendError(w, http.StatusInternalServerError, "Error al leer datos de categorías")
			return
		}

		categories = append(categories, category)
	}

	sendJSON(w, http.StatusOK, categories)
}

func getFilmsByCategoryHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method == http.MethodOptions {
		enableCORS(w)
		return
	}

	if r.Method != http.MethodGet {
		sendError(w, http.StatusMethodNotAllowed, "Método no permitido")
		return
	}

	categoryName := strings.TrimSpace(r.URL.Query().Get("name"))

	if categoryName == "" {
		sendError(w, http.StatusBadRequest, "Debes enviar el parámetro name")
		return
	}

	rows, err := db.Query(`
		SELECT 
			f.film_id,
			f.title,
			f.description,
			f.release_year,
			f.rating,
			f.length
		FROM film f
		INNER JOIN film_category fc ON f.film_id = fc.film_id
		INNER JOIN category c ON fc.category_id = c.category_id
		WHERE c.name = ?
		ORDER BY f.title
		LIMIT 30
	`, categoryName)
	if err != nil {
		log.Println("Error al consultar películas por categoría:", err)
		sendError(w, http.StatusInternalServerError, "Error al consultar películas por categoría")
		return
	}
	defer rows.Close()

	var films []Film

	for rows.Next() {
		var film Film

		err := rows.Scan(
			&film.FilmID,
			&film.Title,
			&film.Description,
			&film.ReleaseYear,
			&film.Rating,
			&film.Length,
		)
		if err != nil {
			log.Println("Error al leer película por categoría:", err)
			sendError(w, http.StatusInternalServerError, "Error al leer datos de películas")
			return
		}

		films = append(films, film)
	}

	sendJSON(w, http.StatusOK, films)
}

// =======================
// MAIN
// =======================
func connectUserHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method == http.MethodOptions {
		enableCORS(w)
		return
	}

	if r.Method != http.MethodPost {
		sendError(w, http.StatusMethodNotAllowed, "Método no permitido")
		return
	}

	var request ConnectRequest

	err := json.NewDecoder(r.Body).Decode(&request)
	if err != nil {
		sendError(w, http.StatusBadRequest, "JSON inválido")
		return
	}

	request.Username = strings.TrimSpace(request.Username)

	if request.Username == "" {
		sendError(w, http.StatusBadRequest, "El nombre de usuario es obligatorio")
		return
	}

	now := time.Now().Format("2006-01-02 15:04:05")

	systemMessage := Message{
		From:   "Sistema",
		To:     "general",
		Text:   request.Username + " se ha conectado al servidor",
		Type:   "system",
		SentAt: now,
	}

	mutex.Lock()

	connectedUsers[request.Username] = User{
		Username:    request.Username,
		ConnectedAt: now,
	}

	messages = append(messages, systemMessage)

	mutex.Unlock()

	broadcastEvent("user_connected", map[string]string{
		"username": request.Username,
	})

	broadcastEvent("message_received", systemMessage)

	response := map[string]string{
		"message":  "Usuario conectado correctamente",
		"username": request.Username,
	}

	sendJSON(w, http.StatusOK, response)
}

func getUsersHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method == http.MethodOptions {
		enableCORS(w)
		return
	}

	if r.Method != http.MethodGet {
		sendError(w, http.StatusMethodNotAllowed, "Método no permitido")
		return
	}

	mutex.Lock()

	var users []User
	for _, user := range connectedUsers {
		users = append(users, user)
	}

	mutex.Unlock()

	sendJSON(w, http.StatusOK, users)
}

func disconnectUserHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method == http.MethodOptions {
		enableCORS(w)
		return
	}

	if r.Method != http.MethodPost {
		sendError(w, http.StatusMethodNotAllowed, "Método no permitido")
		return
	}

	var request ConnectRequest

	err := json.NewDecoder(r.Body).Decode(&request)
	if err != nil {
		sendError(w, http.StatusBadRequest, "JSON inválido")
		return
	}

	request.Username = strings.TrimSpace(request.Username)

	if request.Username == "" {
		sendError(w, http.StatusBadRequest, "El nombre de usuario es obligatorio")
		return
	}

	now := time.Now().Format("2006-01-02 15:04:05")

	systemMessage := Message{
		From:   "Sistema",
		To:     "general",
		Text:   request.Username + " se ha desconectado del servidor",
		Type:   "system",
		SentAt: now,
	}

	mutex.Lock()

	delete(connectedUsers, request.Username)
	messages = append(messages, systemMessage)

	mutex.Unlock()

	broadcastEvent("user_disconnected", map[string]string{
		"username": request.Username,
	})

	broadcastEvent("message_received", systemMessage)

	response := map[string]string{
		"message":  "Usuario desconectado correctamente",
		"username": request.Username,
	}

	sendJSON(w, http.StatusOK, response)
}

func createMessageHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method == http.MethodOptions {
		enableCORS(w)
		return
	}

	if r.Method != http.MethodPost {
		sendError(w, http.StatusMethodNotAllowed, "Método no permitido")
		return
	}

	var request MessageRequest

	err := json.NewDecoder(r.Body).Decode(&request)
	if err != nil {
		sendError(w, http.StatusBadRequest, "JSON inválido")
		return
	}

	request.From = strings.TrimSpace(request.From)
	request.To = strings.TrimSpace(request.To)
	request.Text = strings.TrimSpace(request.Text)
	request.Type = strings.TrimSpace(request.Type)

	if request.From == "" || request.Text == "" {
		sendError(w, http.StatusBadRequest, "El usuario y el mensaje son obligatorios")
		return
	}

	if request.Type == "" {
		request.Type = "group"
	}

	if request.Type != "group" && request.Type != "private" {
		sendError(w, http.StatusBadRequest, "Tipo de mensaje inválido")
		return
	}

	if request.Type == "group" {
		request.To = "general"
	}

	if request.Type == "private" && request.To == "" {
		sendError(w, http.StatusBadRequest, "Debes indicar el usuario destino")
		return
	}

	newMessage := Message{
		From:   request.From,
		To:     request.To,
		Text:   request.Text,
		Type:   request.Type,
		SentAt: time.Now().Format("2006-01-02 15:04:05"),
	}

	mutex.Lock()
	messages = append(messages, newMessage)
	mutex.Unlock()

	broadcastEvent("message_received", newMessage)

	response := map[string]interface{}{
		"message": "Mensaje enviado correctamente",
		"data":    newMessage,
	}

	sendJSON(w, http.StatusCreated, response)
}


func getMessagesHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method == http.MethodOptions {
		enableCORS(w)
		return
	}

	if r.Method != http.MethodGet {
		sendError(w, http.StatusMethodNotAllowed, "Método no permitido")
		return
	}

	messageType := strings.TrimSpace(r.URL.Query().Get("type"))
	user1 := strings.TrimSpace(r.URL.Query().Get("user1"))
	user2 := strings.TrimSpace(r.URL.Query().Get("user2"))

	mutex.Lock()
	defer mutex.Unlock()

	var filteredMessages []Message

	for _, msg := range messages {
		if messageType == "" {
			filteredMessages = append(filteredMessages, msg)
			continue
		}

		if messageType == "group" {
			if msg.Type == "group" || msg.Type == "system" {
				filteredMessages = append(filteredMessages, msg)
			}
			continue
		}

		if messageType == "private" {
			if user1 == "" || user2 == "" {
				continue
			}

			isConversation :=
				msg.Type == "private" &&
					((msg.From == user1 && msg.To == user2) ||
						(msg.From == user2 && msg.To == user1))

			if isConversation {
				filteredMessages = append(filteredMessages, msg)
			}
		}
	}

	sendJSON(w, http.StatusOK, filteredMessages)
}

func broadcastEvent(eventType string, data interface{}) {
	event := Event{
		Type: eventType,
		Data: data,
	}

	eventMutex.Lock()
	defer eventMutex.Unlock()

	for client := range eventClients {
		select {
		case client <- event:
		default:
			// Si el cliente no puede recibir, evitamos bloquear el servidor.
		}
	}
}

func eventsHandler(w http.ResponseWriter, r *http.Request) {
	enableCORS(w)

	if r.Method == http.MethodOptions {
		return
	}

	if r.Method != http.MethodGet {
		sendError(w, http.StatusMethodNotAllowed, "Método no permitido")
		return
	}

	w.Header().Set("Content-Type", "text/event-stream")
	w.Header().Set("Cache-Control", "no-cache")
	w.Header().Set("Connection", "keep-alive")
	w.Header().Set("Access-Control-Allow-Origin", "*")

	flusher, ok := w.(http.Flusher)
	if !ok {
		sendError(w, http.StatusInternalServerError, "El servidor no soporta streaming")
		return
	}

	clientChan := make(chan Event, 10)

	eventMutex.Lock()
	eventClients[clientChan] = true
	eventMutex.Unlock()

	defer func() {
		eventMutex.Lock()
		delete(eventClients, clientChan)
		eventMutex.Unlock()
		close(clientChan)
	}()

	fmt.Fprintf(w, "event: connected\n")
	fmt.Fprintf(w, "data: {\"message\":\"Conexión de eventos establecida\"}\n\n")
	flusher.Flush()

	notify := r.Context().Done()

	for {
		select {
		case <-notify:
			return

		case event := <-clientChan:
			data, err := json.Marshal(event.Data)
			if err != nil {
				continue
			}

			fmt.Fprintf(w, "event: %s\n", event.Type)
			fmt.Fprintf(w, "data: %s\n\n", data)
			flusher.Flush()
		}
	}
}

func main() {
	var err error

	err = godotenv.Load()
	if err != nil {
		log.Println("No se encontró archivo .env, usando variables del sistema")
	}

	dbUser := os.Getenv("DB_USER")
	dbPassword := os.Getenv("DB_PASSWORD")
	dbHost := os.Getenv("DB_HOST")
	dbPort := os.Getenv("DB_PORT")
	dbName := os.Getenv("DB_NAME")
	apiPort := os.Getenv("API_PORT")

	if apiPort == "" {
		apiPort = "8080"
	}

	dsn := fmt.Sprintf("%s:%s@tcp(%s:%s)/%s", dbUser, dbPassword, dbHost, dbPort, dbName)

	db, err = sql.Open("mysql", dsn)
	if err != nil {
		log.Fatal("Error al abrir conexión:", err)
	}

	err = db.Ping()
	if err != nil {
		log.Fatal("No se pudo conectar a MySQL:", err)
	}

	fmt.Println("Conexión exitosa a MySQL - Base de datos Sakila")

	http.HandleFunc("/", healthHandler)
	http.HandleFunc("/api/health", healthHandler)
	http.HandleFunc("/api/films", getFilmsHandler)
	http.HandleFunc("/api/films/search", searchFilmsHandler)
	http.HandleFunc("/api/actors", actorsHandler)
	http.HandleFunc("/api/actors/", actorByIDHandler)
	http.HandleFunc("/api/categories", getCategoriesHandler)
	http.HandleFunc("/api/films/category", getFilmsByCategoryHandler)
	http.HandleFunc("/api/connect", connectUserHandler)
	http.HandleFunc("/api/users", getUsersHandler)
	http.HandleFunc("/api/disconnect", disconnectUserHandler)
	http.HandleFunc("/api/messages", func(w http.ResponseWriter, r *http.Request) {
		if r.Method == http.MethodPost {
			createMessageHandler(w, r)
			return
		}

		if r.Method == http.MethodGet {
			getMessagesHandler(w, r)
			return
		}

		if r.Method == http.MethodOptions {
			enableCORS(w)
			return
		}

		sendError(w, http.StatusMethodNotAllowed, "Método no permitido")
	})
	http.HandleFunc("/api/events", eventsHandler)

	fmt.Println("Servidor corriendo en http://localhost:" + apiPort)

	err = http.ListenAndServe(":"+apiPort, nil)
	if err != nil {
		log.Fatal("Error al iniciar servidor:", err)
	}
	}