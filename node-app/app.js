const express = require('express');
const session = require('express-session');
const bodyParser = require('body-parser');
const path = require('path');
const { Pool } = require('pg');

const app = express();
const PORT = process.env.PORT || 5001;

// Middleware
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());
app.use(session({ secret: 'your_secret_key', resave: true, saveUninitialized: true }));

// Serve static files from the 'public' directory
app.use(express.static(path.join(__dirname, 'public')));


// Create a PostgreSQL connection pool
const pool = new Pool({
  user: 'your_db_user',
  host: 'your_db_host',
  database: 'your_db_name',
  password: 'your_db_password',
  port: 5432, // Default PostgreSQL port
});
// Define routes
app.get('/', (req, res) => {
    res.send('Welcome to the Node.js Example App!');
});

app.get('/login', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'login.html'));
});

app.post('/login', async (req, res) => {
    const { username, password } = req.body;
    try {
      // Query the database to get the user's password hash
      const query = 'SELECT password FROM users WHERE username = $1';
      const { rows } = await pool.query(query, [username]);
      if (rows.length === 0) {
        // User not found, return login error
        return res.render('login', { error: 'Invalid username or password.' });
      }
      const storedPasswordHash = rows[0].password;
  
      // Compare the stored password hash with the password provided by the user
      if (password === storedPasswordHash) {
        // Passwords match, perform login logic (e.g., set session)
        // Redirect user to dashboard or show login success message
        return res.redirect('/dashboard');
      } else {
        // Passwords don't match, return login error
        return res.render('login', { error: 'Invalid username or password.' });
      }
    } catch (error) {
      console.error('Error authenticating user:', error);
      return res.status(500).send('Internal server error');
    }
  });

app.get('/dashboard', (req, res) => {
    if (req.session.username) {
        res.sendFile(path.join(__dirname, 'public', 'dashboard.html'));
    } else {
        res.redirect('/login');
    }
});

app.get('/logout', (req, res) => {
    req.session.destroy();
    res.redirect('/login');
});

// Start the server
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});
