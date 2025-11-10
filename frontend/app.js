const express = require('express');
const bodyParser = require('body-parser');
const axios = require('axios');
const path = require('path');

const app = express();
const PORT = 3000;

// Backend Flask API URL
const API_BASE = 'http://localhost:5000';

app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json()); // hỗ trợ JSON
app.use(express.static(path.join(__dirname, 'public')));

// ----- Routes -----
app.get('/', (req, res) => {
    res.redirect('/login');
});

// ---- Register page ----
app.get('/register', (req, res) => {
    res.render('register', { message: null });
});

app.post('/register', async (req, res) => {
    try {
        const { email, username, password } = req.body;
        const response = await axios.post(`${API_BASE}/register`, {
            email, username, password
        }, { headers: { 'Content-Type': 'application/json' } });

        if (response.data.success) {
            res.render('login', { message: response.data.message });
        } else {
            res.render('register', { message: response.data.message });
        }
    } catch (err) {
        let msg = "Lỗi server hoặc tên người dùng đã tồn tại.";
        if (err.response && err.response.data && err.response.data.message) {
            msg = err.response.data.message;
        }
        res.render('register', { message: msg });
    }
});

// ---- Login page ----
app.get('/login', (req, res) => {
    res.render('login', { message: null });
});

app.post('/login', async (req, res) => {
    try {
        const { username, password } = req.body;
        const response = await axios.post(`${API_BASE}/login`, {
            username, password
        }, { headers: { 'Content-Type': 'application/json' } });

        if (response.data.success) {
            res.redirect(`/welcome?username=${username}`);
        } else {
            res.render('login', { message: response.data.message });
        }
    } catch (err) {
        let msg = "Sai tên đăng nhập hoặc mật khẩu!";
        if (err.response && err.response.data && err.response.data.message) {
            msg = err.response.data.message;
        }
        res.render('login', { message: msg });
    }
});

// ---- Welcome page ----
app.get('/welcome', (req, res) => {
    const username = req.query.username || "Khách";
    res.render('welcome', { username });
});

// ---- Start server ----
app.listen(PORT, () => {
    console.log(`Frontend Node.js running at http://localhost:${PORT}`);
});
