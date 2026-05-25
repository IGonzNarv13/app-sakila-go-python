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

	_ "github.com/go-sql-driver/mysql"
	"github.com/joho/godotenv"
)

var db *sql.DB
var connectedUsers = make(map[string]User)
var messages []Message
var mutex sync.Mutex

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

type Message struct {
	Username string `json:"username"`
	Text     string `json:"text"`
	SentAt   string `json:"sent_at"`
}

type ConnectRequest struct {
	Username string `json:"username"`
}

type MessageRequest struct {
	Username string `json:"username"`
	Text     string `json:"text"`
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
		LIMIT 30
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

func getActorsHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method == http.MethodOptions {
		enableCORS(w)
		return
	}

	if r.Method != http.MethodGet {
		sendError(w, http.StatusMethodNotAllowed, "Método no permitido")
		return
	}

	rows, err := db.Query(`
		SELECT actor_id, first_name, last_name
		FROM actor
		ORDER BY actor_id
		LIMIT 50
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

	mutex.Lock()

	connectedUsers[request.Username] = User{
		Username:    request.Username,
		ConnectedAt: time.Now().Format("2006-01-02 15:04:05"),
	}

	messages = append(messages, Message{
		Username: "Sistema",
		Text:     request.Username + " se ha conectado al servidor",
		SentAt:   time.Now().Format("2006-01-02 15:04:05"),
	})

	mutex.Unlock()

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

	mutex.Lock()

	delete(connectedUsers, request.Username)

	messages = append(messages, Message{
		Username: "Sistema",
		Text:     request.Username + " se ha desconectado del servidor",
		SentAt:   time.Now().Format("2006-01-02 15:04:05"),
	})

	mutex.Unlock()
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

	request.Username = strings.TrimSpace(request.Username)
	request.Text = strings.TrimSpace(request.Text)

	if request.Username == "" || request.Text == "" {
		sendError(w, http.StatusBadRequest, "El usuario y el mensaje son obligatorios")
		return
	}

	newMessage := Message{
		Username: request.Username,
		Text:     request.Text,
		SentAt:   time.Now().Format("2006-01-02 15:04:05"),
	}

	mutex.Lock()
	messages = append(messages, newMessage)
	mutex.Unlock()

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

	mutex.Lock()
	copiedMessages := make([]Message, len(messages))
	copy(copiedMessages, messages)
	mutex.Unlock()

	sendJSON(w, http.StatusOK, copiedMessages)
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
	http.HandleFunc("/api/actors", getActorsHandler)
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

	fmt.Println("Servidor corriendo en http://localhost:8080")

	err = http.ListenAndServe(":"+apiPort, nil)
	if err != nil {
		log.Fatal("Error al iniciar servidor:", err)
	}
}