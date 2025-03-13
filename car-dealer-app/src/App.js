import React, { useState, useEffect } from "react";
import './App.css';
import axios from "axios";

function App() {
    const [cars, setCars] = useState([]);
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [isModalOpen, setIsModalOpen] = useState(false);

    const openModal = () => setIsModalOpen(true);
    const closeModal = () => setIsModalOpen(false);

    // Проверка авторизации при загрузке страницы
    useEffect(() => {
        const checkAuth = async () => {
            try {
                const response = await axios.get("http://127.0.0.1:8000/auth/status", { withCredentials: true });
                setIsAuthenticated(response.data.isAuthenticated);
            } catch (error) {
                console.error("Ошибка при проверке авторизации:", error);
                setIsAuthenticated(false);
            }
        };
        checkAuth();

        // Получение списка машин
        axios.get("http://127.0.0.1:8000/cars_for_sale")
            .then(res => setCars(res.data))
            .catch(console.error);
    }, []);

    // Логин
    const handleLogin = async (e) => {
        e.preventDefault();
        const formData = new URLSearchParams();
        formData.append("username", e.target.username.value);
        formData.append("password", e.target.password.value);

        try {
            const response = await axios.post("http://127.0.0.1:8000/auth/login", formData, {
                withCredentials: true,
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                },
            });

            if (response.data.message === "Login successful") {
                setIsAuthenticated(true);
                closeModal();
            } else {
                alert("Ошибка: " + (response.data.message || "Неверные данные."));
            }
        } catch (error) {
            alert("Ошибка при соединении с сервером.");
            console.error(error);
        }
    };

    // Логаут
    const handleLogout = async () => {
        try {
            const response = await axios.post("http://127.0.0.1:8000/auth/logout", {}, { withCredentials: true });

            if (response.data.message === "Successfully logged out") {
                setIsAuthenticated(false);
                alert("Подтвердите выход.");
            } else {
                alert("Ошибка при выходе: " + response.data.message);
            }
        } catch (error) {
            alert("Ошибка при соединении с сервером.");
            console.error(error);
        }
    };

    return (
        <div className="app">
            <h1>Cars for Sale</h1>
            <div className="buttons">
                {!isAuthenticated ? (
                    <>
                        <button onClick={openModal}>Sign In</button>
                        <button>Sign Up</button>
                    </>
                ) : (
                    <button onClick={handleLogout}>Logout</button>
                )}
            </div>

            {/* Модальное окно логина */}
            {isModalOpen && (
                <div className="modal">
                    <div className="modal-content">
                        <span className="close" onClick={closeModal}>&times;</span>
                        <h2>Login</h2>
                        <form onSubmit={handleLogin}>
                            <div>
                                <label htmlFor="username">Username</label>
                                <input type="text" id="username" name="username" required />
                            </div>
                            <div>
                                <label htmlFor="password">Password</label>
                                <input type="password" id="password" name="password" required />
                            </div>
                            <button type="submit">Login</button>
                        </form>
                    </div>
                </div>
            )}

            {/* Список машин */}
            <div className="car-list">
                {cars.map(car => (
                    <div className="car-card" key={car.id}>
                        <h2>{car["manufacturer name"]} {car.model}</h2>
                        <p><strong>Year:</strong> {car.year_produced}</p>
                        <p><strong>Odometer:</strong> {car.odometer_value} km</p>
                        <p><strong>Previous Owners:</strong> {car.previous_owners}</p>
                        <p><strong>Color:</strong> {car.color}</p>
                        <p><strong>Transmission:</strong> {car.transmission}</p>
                        <p><strong>Engine Type:</strong> {car.engine_type}</p>
                        <p><strong>Body Type:</strong> {car.body_type}</p>
                        <p><strong>Price:</strong> ${car.price_usd}</p>
                    </div>
                ))}
            </div>
        </div>
    );
}

export default App;
