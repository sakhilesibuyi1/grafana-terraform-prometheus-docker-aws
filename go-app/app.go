package main

import (
	"database/sql"
	"fmt"
	"html/template"
	"log"
	"net/http"
	"time"

	_ "github.com/lib/pq"
	"golang.org/x/crypto/bcrypt"
)

var db *sql.DB

const (
	host     = "my_app"
	port     = 5432
	user     = "admin"
	password = "admin1223"
	dbname   = "flask_db"
)

func main() {
	var err error
	dbinfo := fmt.Sprintf("host=%s port=%d user=%s "+
		"password=%s dbname=%s sslmode=disable",
		host, port, user, password, dbname)

	db, err = sql.Open("postgres", dbinfo)
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	err = db.Ping()
	if err != nil {
		log.Fatal(err)
	}

	http.HandleFunc("/", homeHandler)
	http.HandleFunc("/login", loginHandler)
	http.HandleFunc("/logout", logoutHandler)
	http.HandleFunc("/dashboard", dashboardHandler)

	fmt.Println("Server running on port 5001")

	if err := http.ListenAndServe(":5001", nil); err != nil {
		fmt.Printf("Error starting server: %s\n", err)
	}
}

func homeHandler(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintln(w, "Welcome to the Go Example!")
}

func loginHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		renderTemplate(w, "login.html", nil)
		return
	}

	username := r.FormValue("username")
	password := r.FormValue("password")

	var hashedPassword string
	err := db.QueryRow("SELECT password FROM users WHERE username = $1", username).Scan(&hashedPassword)
	if err != nil {
		log.Printf("Error retrieving user data: %v\n", err)
		renderTemplate(w, "login.html", map[string]interface{}{"Error": "Invalid username or password"})
		return
	}

	err = bcrypt.CompareHashAndPassword([]byte(hashedPassword), []byte(password))
	if err != nil {
		log.Printf("Invalid password for user %s: %v\n", username, err)
		renderTemplate(w, "login.html", map[string]interface{}{"Error": "Invalid username or password"})
		return
	}

	// Authentication successful, set session
	http.Redirect(w, r, "/dashboard", http.StatusFound)
}

func logoutHandler(w http.ResponseWriter, r *http.Request) {
	// Clear session
	http.Redirect(w, r, "/login", http.StatusFound)
}

func dashboardHandler(w http.ResponseWriter, r *http.Request) {
	// Display dashboard
	renderTemplate(w, "dashboard.html", nil)
}

func renderTemplate(w http.ResponseWriter, tmpl string, data interface{}) {
	tmpl = fmt.Sprintf("templates/%s", tmpl)
	t, err := template.ParseFiles(tmpl)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	err = t.Execute(w, data)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
	}
}
