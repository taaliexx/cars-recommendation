import React, { useState, useEffect } from "react";
import './App.css';
import axios from "axios";

function App() {
  const [cars, setCars] = useState([]);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [dealerInfo, setDealerInfo] = useState(null);  // Информация о дилере
  const [showMyAccount, setShowMyAccount] = useState(false);  // Раздел "My Account"
  const [soldCars, setSoldCars] = useState([]);  // Проданные машины
  const [recommendedCars, setRecommendedCars] = useState([]);  // Ранее рекомендованные машины
  const [isLoading, setIsLoading] = useState(false);  // Статус загрузки рекомендаций
  const [recommendations, setRecommendations] = useState([]);
  const [showRecommendations, setShowRecommendations] = useState(false);
  const [showSoldCars, setShowSoldCars] = useState(false); // Флаг для отображения проданных машин
  const [showPreviousRecommendations, setShowPreviousRecommendations] = useState(false); // Флаг для отображения предыдущих рекомендаций
  const [isAddCarFormOpen, setIsAddCarFormOpen] = useState(false);
  const [newCar, setNewCar] = useState({
    manufacturer_name: '',
    model_name: '',
    year_produced: '',
    odometer_value: '',
    price_usd: '',
    transmission: 'automatic',
    engine_type: 'gasoline',
    body_type: 'universal',
    color: 'silver',
    previous_owners: '1'
  });

  const [filteredCars, setFilteredCars] = useState([]);  // Массив для отфильтрованных машин
  const [showFilters, setShowFilters] = useState(true);
  const [filters, setFilters] = useState({
    manufacturer_name: '',
    model: '',
    year_produced: '',
    min_price: '',
    max_price: '',
    min_odometer: '',
    max_odometer: '',
    transmission: 'automatic',
    engine_type: 'gasoline',
    body_type: 'universal',
    color: 'silver'
  });

  const transmissionOptions = ['automatic', 'manual'];
  const engineTypeOptions = ['gasoline', 'diesel'];
  const bodyTypeOptions = [
    'universal', 'suv', 'sedan', 'hatchback', 'liftback', 'minivan',
    'minibus', 'van', 'pickup', 'coupe', 'cabriolet', 'limousine', 'other'
  ];
  const colorOptions = [
    'silver', 'blue', 'red', 'black', 'grey', 'brown', 'white', 'green',
    'violet', 'orange', 'yellow', 'other'
  ];
  const previousOwnersOptions = ['1', '2', '3', 'more than 3'];

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
      .then(res => { setCars(res.data); setFilteredCars(res.data); })
      .catch(console.error);
  }, []);

  // Функция для обработки изменения значений фильтров
  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters({
      ...filters,
      [name]: value
    });
  };

  // Фильтрация машин
  const filterCars = () => {
    let filtered = cars;

    // Фильтрация по каждому полю
    if (filters.manufacturer_name) {
      filtered = filtered.filter(car =>
        car.manufacturer_name && car.manufacturer_name.toLowerCase().includes(filters.manufacturer_name.toLowerCase())
      );
    }
    if (filters.model_name) {
      filtered = filtered.filter(car =>
        car.model && car.model.toLowerCase().includes(filters.model_name.toLowerCase())
      );
    }
    if (filters.year_produced) {
      filtered = filtered.filter(car => car.year_produced === parseInt(filters.year_produced));
    }
    if (filters.min_price) {
      filtered = filtered.filter(car => car.price_usd >= parseFloat(filters.min_price));
    }
    if (filters.max_price) {
      filtered = filtered.filter(car => car.price_usd <= parseFloat(filters.max_price));
    }
    if (filters.min_odometer) {
      filtered = filtered.filter(car => car.odometer_value >= parseFloat(filters.min_odometer));
    }
    if (filters.max_odometer) {
      filtered = filtered.filter(car => car.odometer_value <= parseFloat(filters.max_odometer));
    }
    if (filters.transmission) {
      filtered = filtered.filter(car => car.transmission === filters.transmission);
    }
    if (filters.engine_type) {
      filtered = filtered.filter(car => car.engine_type === filters.engine_type);
    }
    if (filters.body_type) {
      filtered = filtered.filter(car => car.body_type === filters.body_type);
    }
    if (filters.color) {
      filtered = filtered.filter(car => car.color === filters.color);
    }

    setFilteredCars(filtered);
  };
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
      alert("Ошибка");
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

  // Получение информации о дилере
  const fetchDealerInfo = async () => {
    try {
      const response = await axios.get("http://127.0.0.1:8000/dealer_info", { withCredentials: true });
      if (response.data && response.data.name) {
        setDealerInfo(response.data);
      } else {
        console.error("Данные о дилере не найдены");
        setDealerInfo(null);  // Устанавливаем пустое состояние, если данные не получены
      }
    } catch (error) {
      console.error("Ошибка при получении информации о дилере:", error);
      setDealerInfo(null);  // Устанавливаем пустое состояние в случае ошибки
    }
  };

  // Получение рекомендаций
  const handleGetRecommendations = async () => {
    setIsLoading(true);
    try {
      const response = await axios.get("http://127.0.0.1:8000/recommendations", { withCredentials: true });
      setRecommendations(response.data);
      setShowRecommendations(true);
      setShowSoldCars(false);  // Скрываем проданные машины при показе рекомендаций
      setShowPreviousRecommendations(false);  // Скрываем предыдущие рекомендации
      setShowFilters(false);
    } catch (error) {
      alert("Ошибка при получении рекомендаций.");
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleMyAccount = () => {
    setShowMyAccount(true);
    setShowRecommendations(false);  // Прячем рекомендации
    fetchDealerInfo();  // Загружаем информацию о дилере
    setShowFilters(false);
  };

  // Получение проданных машин
  const fetchSoldCars = async () => {
    try {
      const response = await axios.get("http://127.0.0.1:8000/dealers_cars", { withCredentials: true });
      setSoldCars(response.data);
      setShowSoldCars(true);  // Показываем проданные машины
      setShowPreviousRecommendations(false);  // Скрываем предыдущие рекомендации
      setShowFilters(false);
    } catch (error) {
      alert("Ошибка при получении проданных машин.");
      console.error(error);
    }
  };

  // Получение рекомендованных машин
  const fetchRecommendedCars = async () => {
    try {
      const response = await axios.get("http://127.0.0.1:8000/dealers_previous_recommendations", { withCredentials: true });
      setRecommendedCars(response.data);
      setShowPreviousRecommendations(true);  // Показываем предыдущие рекомендации
      setShowSoldCars(false);  // Скрываем проданные машины
      setShowFilters(false);
    } catch (error) {
      alert("Ошибка при получении рекомендованных машин.");
      console.error(error);
    }
  };

  // Кнопка назад для возврата ко всем машинам
  const handleBackToAllCars = () => {
    setShowRecommendations(false);
    setShowMyAccount(false);
    setSoldCars([]);  // Очистка проданных машин
    setRecommendedCars([]);  // Очистка рекомендованных машин
    setShowSoldCars(false);  // Скрываем проданные машины
    setShowPreviousRecommendations(false);  // Скрываем предыдущие рекомендации
    setShowFilters(true);
  };


  // const formattedDate = new Date(dealerInfo.created_at).toLocaleDateString("en-EN", {
  //   year: "numeric",
  //   month: "long",
  //   day: "numeric"
  // });

  const handleAddCar = async (e) => {
    e.preventDefault();
    try {
      await axios.post("http://127.0.0.1:8000/add_dealer_car", newCar, {
        withCredentials: true,
        headers: {
          "Content-Type": "application/json",
        },
      });
      alert("Машина успешно добавлена!");
      setIsAddCarFormOpen(false);
      fetchSoldCars();
    } catch (error) {
      alert("Ошибка при добавлении машины.");
      console.error(error);
    }
  };
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setNewCar({ ...newCar, [name]: value });
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
          <>
            <button onClick={handleGetRecommendations}>Get Recommendations</button>
            <button onClick={handleMyAccount}>My Account</button>
            <button onClick={handleLogout}>Logout</button>
          </>
        )}
      </div>
      {/* Фильтры */}
      {showFilters && (
        <div className="filters">
          <input
            type="text"
            name="manufacturer_name"
            value={filters.manufacturer_name}
            onChange={handleFilterChange}
            placeholder="Manufacturer"
          />
          <input
            type="text"
            name="model_name"
            value={filters.model_name}
            onChange={handleFilterChange}
            placeholder="Model"
          />
          <input
            type="number"
            name="year_produced"
            value={filters.year_produced}
            onChange={handleFilterChange}
            placeholder="Year"
          />
          <input
            type="number"
            name="min_price"
            value={filters.min_price}
            onChange={handleFilterChange}
            placeholder="Min Price"
          />
          <input
            type="number"
            name="max_price"
            value={filters.max_price}
            onChange={handleFilterChange}
            placeholder="Max Price"
          />
          <input
            type="number"
            name="min_odometer"
            value={filters.min_odometer}
            onChange={handleFilterChange}
            placeholder="Min Odometer"
          />
          <input
            type="number"
            name="max_odometer"
            value={filters.max_odometer}
            onChange={handleFilterChange}
            placeholder="Max Odometer"
          />
          <select
            name="transmission"
            value={filters.transmission}
            onChange={handleFilterChange}
          >
            <option value="">All Transmissions</option>
            {transmissionOptions.map((option) => (
              <option key={option} value={option}>{option}</option>
            ))}
          </select>
          <select
            name="engine_type"
            value={filters.engine_type}
            onChange={handleFilterChange}
          >
            <option value="">All Engine Types</option>
            {engineTypeOptions.map((option) => (
              <option key={option} value={option}>{option}</option>
            ))}
          </select>
          <select
            name="body_type"
            value={filters.body_type}
            onChange={handleFilterChange}
          >
            <option value="">All Body Types</option>
            {bodyTypeOptions.map((option) => (
              <option key={option} value={option}>{option}</option>
            ))}
          </select>
          <select
            name="color"
            value={filters.color}
            onChange={handleFilterChange}
          >
            <option value="">All Colors</option>
            {colorOptions.map((option) => (
              <option key={option} value={option}>{option}</option>
            ))}
          </select>
          <button onClick={filterCars}>Filter</button>
        </div>
      )}
      {/* Модальное окно логина */}
      {isModalOpen && (
        <div className="modal">
          <div className="modal-content">
            <span className="close" onClick={closeModal}>&times;</span>
            <h2>Login</h2>
            <form onSubmit={handleLogin}>
              <div>
                <label htmlFor="username">E-mail</label>
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
      {/* Спиннер загрузки */}
      {isLoading && (
        <div className="spinner">
          <div className="loading-spinner"></div>
          <p>Loading recommendations...</p> {/* Текст загрузки */}
        </div>
      )}
      {/* Раздел My Account */}
      {showMyAccount && (
        <div className="my-account">
          <button onClick={handleBackToAllCars}>Back to All Cars</button>
          <h2>My Account</h2>
          {dealerInfo ? (
            <div>
              <p><strong>Name:</strong> {dealerInfo.name}</p>
              <p><strong>Email:</strong> {dealerInfo.email}</p>
              {/* <p><strong>You are with us since:</strong> {formattedDate}</p> */}
            </div>
          ) : (
            <p>Loading your account information...</p>
          )}
          <button onClick={() => setIsAddCarFormOpen(true)}>Add Car</button>

          {isAddCarFormOpen && (
            <div className="add-car-form">
              <form onSubmit={handleAddCar}>
                {/* Manufacturer Name */}
                <div>
                  <label>Manufacturer Name:</label>
                  <input type="text" name="manufacturer_name" value={newCar.manufacturer_name} onChange={handleInputChange} required />
                </div>

                {/* Model Name */}
                <div>
                  <label>Model Name:</label>
                  <input type="text" name="modуд" value={newCar.model} onChange={handleInputChange} required />
                </div>

                {/* Year Produced */}
                <div>
                  <label>Year Produced:</label>
                  <input type="number" name="year_produced" value={newCar.year_produced} onChange={handleInputChange} required />
                </div>

                {/* Odometer Value */}
                <div>
                  <label>Odometer Value:</label>
                  <input type="number" name="odometer_value" value={newCar.odometer_value} onChange={handleInputChange} required />
                </div>

                {/* Price USD */}
                <div>
                  <label>Price USD:</label>
                  <input type="number" name="price_usd" value={newCar.price_usd} onChange={handleInputChange} required />
                </div>

                {/* Transmission */}
                <div>
                  <label>Transmission:</label>
                  <select name="transmission" value={newCar.transmission} onChange={handleInputChange}>
                    <option value="">All Transmissions</option> {/* Пустое значение */}
                    {transmissionOptions.map((option) => (
                      <option key={option} value={option}>{option}</option>
                    ))}
                  </select>
                </div>

                {/* Engine Type */}
                <div>
                  <label>Engine Type:</label>
                  <select name="engine_type" value={newCar.engine_type} onChange={handleInputChange}>
                    <option value="">All Engine Types</option> {/* Пустое значение */}
                    {engineTypeOptions.map((option) => (
                      <option key={option} value={option}>{option}</option>
                    ))}
                  </select>
                </div>

                {/* Body Type */}
                <div>
                  <label>Body Type:</label>
                  <select name="body_type" value={newCar.body_type} onChange={handleInputChange}>
                    <option value="">All Body Types</option> {/* Пустое значение */}
                    {bodyTypeOptions.map((option) => (
                      <option key={option} value={option}>{option}</option>
                    ))}
                  </select>
                </div>

                {/* Color */}
                <div>
                  <label>Color:</label>
                  <select name="color" value={newCar.color} onChange={handleInputChange}>
                    <option value="">All Colors</option> {/* Пустое значение */}
                    {colorOptions.map((option) => (
                      <option key={option} value={option}>{option}</option>
                    ))}
                  </select>
                </div>

                {/* Previous Owners */}
                <div>
                  <label>Previous Owners:</label>
                  <select name="previous_owners" value={newCar.previous_owners} onChange={handleInputChange}>
                    <option value="">All Owners</option> {/* Пустое значение */}
                    {previousOwnersOptions.map((option) => (
                      <option key={option} value={option}>{option}</option>
                    ))}
                  </select>
                </div>

                {/* Submit */}
                <button type="submit">Add Car</button>
                <button type="button" onClick={() => setIsAddCarFormOpen(false)}>Cancel</button>
              </form>
            </div>
          )}
          <button onClick={fetchSoldCars}>My Sold Cars</button>
          <button onClick={fetchRecommendedCars}>Previous Recommendations</button>

          {/* Список проданных машин */}
          {showSoldCars && (
            <div className="car-list">
              <h3>Sold Cars:</h3>
              {soldCars.map(car => (
                <div className="car-card" key={car.id}>
                  <h2>{car.name} {car.model_name}</h2>
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
          )}

          {/* Список рекомендованных машин */}
          {showPreviousRecommendations && (
            <div className="car-list">
              <h3>Previously Recommended Cars:</h3>
              {recommendedCars.map(car => (
                <div className="car-card" key={car.id}>
                  <h2>{car.name} {car.model_name}</h2>
                  <p><strong>Year:</strong> {car.year_produced}</p>
                  <p><strong>Odometer:</strong> {car.odometer_value} km</p>
                  <p><strong>Previous Owners:</strong> {car.previous_owners}</p>
                  <p><strong>Color:</strong> {car.color}</p>
                  <p><strong>Transmission:</strong> {car.transmission}</p>
                  <p><strong>Engine Type:</strong> {car.engine_type}</p>
                  <p><strong>Body Type:</strong> {car.body_type}</p>
                  <p><strong>Price:</strong> ${car.price_usd}</p>
                  <p><strong>Predicted Price:</strong> ${parseFloat(car.predicted_price).toFixed(0)}</p>
                  <p><strong>Profit:</strong> ${parseFloat(car.predicted_price).toFixed(0) - car.price_usd}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Список машин */}
      <div className="car-list">
        {!showMyAccount && !showRecommendations && (
          // Проверяем, есть ли отфильтрованные машины
          (filteredCars.length > 0 ? (
            filteredCars.map(car => (
              <div className="car-card" key={car.id}>
                <h2>{car.manufacturer_name} {car.model}</h2>
                <p><strong>Year:</strong> {car.year_produced}</p>
                <p><strong>Odometer:</strong> {car.odometer_value} km</p>
                <p><strong>Previous Owners:</strong> {car.previous_owners}</p>
                <p><strong>Color:</strong> {car.color}</p>
                <p><strong>Transmission:</strong> {car.transmission}</p>
                <p><strong>Engine Type:</strong> {car.engine_type}</p>
                <p><strong>Body Type:</strong> {car.body_type}</p>
                <p><strong>Price:</strong> ${car.price_usd}</p>
              </div>
            ))
          ) : (
            // Если машин нет по текущим фильтрам, выводим сообщение
            <p>No cars found based on your filters.</p>
          ))
        )}
      </div>
      {/* Список рекомендованных машин */}
      {showRecommendations && (
        <div className="car-list">
          <h3>Recommended Cars:</h3>
          {recommendations.map(car => (
            <div className="car-card" key={car.id}>
              <h2>{car.manufacturer_name} {car.model_name}</h2>
              <p><strong>Year:</strong> {car.year_produced}</p>
              <p><strong>Odometer:</strong> {car.odometer_value} km</p>
              <p><strong>Previous Owners:</strong> {car.previous_owners}</p>
              <p><strong>Color:</strong> {car.color}</p>
              <p><strong>Transmission:</strong> {car.transmission}</p>
              <p><strong>Engine Type:</strong> {car.engine_type}</p>
              <p><strong>Body Type:</strong> {car.body_type}</p>
              <p><strong>Price:</strong> ${car.price_usd}</p>
              <p><strong>Predicted Price:</strong> ${car.predicted_price.toFixed(0)}</p>
              <p><strong>Profit:</strong> ${car.predicted_price.toFixed(0) - car.price_usd}</p>
            </div>
          ))}
          <button className="back-to-all-cars-btn" onClick={handleBackToAllCars}>Back to All Cars</button>
        </div>
      )}



    </div>
  );
}

export default App;
